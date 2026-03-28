# routes/explosion_materiales/explosion.py
import datetime
from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from database.mysql import (
    db, OrdenProduccion, OrdenProduccionInsumo, Receta,
    ProductoVariante, Producto, MovimientoInventario, TipoMovimiento, StockArticulo
)
from middlerware import login_requerido, permiso_requerido, decrypt_url_id
from utils.crypto_url import encrypt_id

explosion = Blueprint("explosion", __name__, url_prefix="/explosion")


# ══════════════════════════════════════════════════════
# VISTA — Lista de órdenes de producción
# ══════════════════════════════════════════════════════
@explosion.route("/")
@login_requerido
@permiso_requerido("explosion", "ver")
def lista():
    search   = request.args.get("search", "", type=str)
    estatus  = request.args.get("estatus", "", type=str)
    page     = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    query = (
        OrdenProduccion.query
        .join(OrdenProduccion.receta)
        .join(Receta.producto_variante)
        .join(ProductoVariante.producto)
        .join(ProductoVariante.talla)
    )

    if search:
        query = query.filter(Producto.nombre.ilike(f"%{search}%"))

    if estatus:
        query = query.filter(OrdenProduccion.estatus == estatus)

    pagination = query.order_by(OrdenProduccion.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template(
        "explosion/lista.html",
        titulo="Explosión de Materiales",
        descripcion="Órdenes de producción y validación de insumos",
        pagination=pagination,
        search=search,
        estatus_filtro=estatus,
        per_page=per_page,
    )


# ══════════════════════════════════════════════════════
# VISTA — Crear nueva orden
# ══════════════════════════════════════════════════════
@explosion.route("/nueva", methods=["GET", "POST"])
@login_requerido
@permiso_requerido("explosion", "crear")
def nueva():
    if request.method == "POST":
        return _procesar_orden()

    return render_template(
        "explosion/nueva.html",
        titulo="Nueva Orden de Producción",
        descripcion="Selecciona una receta y define la cantidad a producir",
    )


# ══════════════════════════════════════════════════════
# VISTA — Detalle de una orden
# ══════════════════════════════════════════════════════
@explosion.route("/detalle/<id>")
@decrypt_url_id()
@login_requerido
@permiso_requerido("explosion", "ver")
def detalle(id):
    orden = OrdenProduccion.query.get_or_404(id)
    return render_template(
        "explosion/detalle.html",
        titulo=f"Orden #{orden.id}",
        descripcion="Detalle de explosión de materiales",
        orden=orden,
    )


# ══════════════════════════════════════════════════════
# LÓGICA — Procesar creación de orden
# ══════════════════════════════════════════════════════
def _procesar_orden():
    receta_id = request.form.get("receta_id", type=int)
    cantidad  = request.form.get("cantidad_solicitada", type=int)
    inv_ids   = request.form.getlist("inv_ids[]", type=int)

    if not receta_id or not cantidad or cantidad < 1:
        flash("Receta y cantidad son requeridas.", "error")
        return redirect(url_for("explosion.nueva"))

    if not inv_ids:
        flash("Debes seleccionar al menos un almacén de materia prima.", "error")
        return redirect(url_for("explosion.nueva"))

    receta = Receta.query.get_or_404(receta_id)

    faltantes, tramos = _calcular_insumos_multi(receta, cantidad, inv_ids)

    if faltantes:
        flash(
            "Inventario insuficiente para generar la orden. "
            "Verifica el stock en los almacenes seleccionados.",
            "warning",
        )
        return redirect(url_for("explosion.nueva"))

    # — Crear la orden —
    orden = OrdenProduccion(
        receta_id=receta_id,
        cantidad_solicitada=cantidad,
        cantidad_producida=0,
        estatus="pendiente",
    )
    db.session.add(orden)
    db.session.flush()

    tipo_mov = TipoMovimiento.query.filter_by(tipo="Salida producción").first()

    for tramo in tramos:
        mp     = tramo["materia_prima"]
        inv_id = tramo["inv_id"]
        cant   = Decimal(str(tramo["cantidad"]))

        db.session.add(OrdenProduccionInsumo(
            orden_id=orden.id,
            materia_prima_id=mp.id,
            inv_id=inv_id,
            cantidad=cant,
            unidad_id=mp.unidad_id,
            creado_por=g.usuario_actual.id,
        ))

        stock = StockArticulo.query.filter_by(
            articulo_id=mp.articulo_id, inv_id=inv_id
        ).first()

        if stock:
            stock.cantidad        = max(Decimal("0"), stock.cantidad - cant)
            stock.actualizado_por = g.usuario_actual.id

        if tipo_mov and mp.articulo_id:
            existencia_post = stock.cantidad if stock else Decimal("0")
            db.session.add(MovimientoInventario(
                articulo_id=mp.articulo_id,
                tipo_mov_id=tipo_mov.id,
                inv_id=inv_id,
                cantidad=cant,
                unidad_id=mp.unidad_id,
                signo=-1,
                existencia=existencia_post,
            ))

    db.session.commit()
    flash(f"Orden #{orden.id} generada correctamente.", "success")
    return redirect(url_for("explosion.detalle", id=encrypt_id(orden.id)))

def _calcular_insumos_multi(receta: Receta, cantidad: int, inv_ids: list):
    factor    = Decimal(str(cantidad)) / Decimal(str(receta.cantidad_base))
    faltantes = False
    tramos    = []

    for detalle in receta.detalles:
        mp        = detalle.materia_prima
        pendiente = Decimal(str(detalle.cantidad_neta)) * factor

        for inv_id in inv_ids:
            if pendiente <= 0:
                break

            stock      = StockArticulo.query.filter_by(
                articulo_id=mp.articulo_id, inv_id=inv_id
            ).first()
            disponible = stock.cantidad if stock else Decimal("0")
            tomar      = min(disponible, pendiente)

            if tomar > 0:
                tramos.append({
                    "materia_prima": mp,
                    "inv_id":        inv_id,
                    "cantidad":      round(tomar, 4),
                    "suficiente":    True,
                })
                pendiente -= tomar

        if pendiente > 0:
            faltantes = True
            # Tramo con faltante — se asocia al primer almacén como referencia
            tramos.append({
                "materia_prima": mp,
                "inv_id":        inv_ids[0],
                "cantidad":      round(pendiente, 4),
                "suficiente":    False,
            })

    return faltantes, tramos
