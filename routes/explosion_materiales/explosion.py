# routes/explosion_materiales/explosion.py
from datetime import datetime, timezone
from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from database.mysql import (
    db, OrdenProduccion, OrdenProduccionInsumo, Receta,
    ProductoVariante, Producto, MovimientoInventario, TipoMovimiento, StockArticulo,
    MovimientoProduccion
)
from middlerware import login_requerido, permiso_requerido, decrypt_url_id
from utils.crypto_url import encrypt_id

explosion = Blueprint("explosion", __name__, url_prefix="/explosion")

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

@explosion.route("/capturar-produccion/<id>", methods=["GET", "POST"])
@decrypt_url_id()
@login_requerido
@permiso_requerido("explosion", "editar")
def capturar_produccion(id):
    orden = OrdenProduccion.query.get_or_404(id)

    if request.method == "POST":
        cantidad_p = request.form.get("cantidad", type=int)
        
        # 1. Validaciones básicas
        if not cantidad_p or cantidad_p <= 0:
            flash("La cantidad debe ser mayor a 0", "error")
            return redirect(request.url)
        
        max_producir = orden.cantidad_solicitada - orden.cantidad_producida
        if cantidad_p > max_producir:
            flash(f"No se puede producir más de {max_producir} unidades", "warning")
            return redirect(request.url)

        try:
            # 2. Obtener tipo de movimiento
            tipo_mov_salida = TipoMovimiento.query.filter_by(tipo="Salida producción").first()
            if not tipo_mov_salida:
                raise Exception("Tipo de movimiento 'Salida producción' no configurado.")
            
            # 4. Procesar Insumos (Restar Stock y Crear Movimientos)
            for insumo in orden.insumos_asignados:
                cantidad_consumir = insumo.cantidad

                if insumo.cantidad < cantidad_consumir:
                    raise Exception(f"Insumo insuficiente asignado para {insumo.materia_prima.nombre}")

                insumo.cantidad -= cantidad_consumir

                db.session.add(MovimientoInventario(
                    articulo_id=insumo.materia_prima.articulo_id,
                    tipo_mov_id=tipo_mov_salida.id,
                    inv_id=insumo.inv_id,
                    cantidad=cantidad_consumir,
                    unidad_id=insumo.unidad_id,
                    signo=-1,
                    existencia=insumo.cantidad,  # 👈 ahora representa lo restante asignado
                ))

            # 5. Registrar historial de producción
            db.session.add(MovimientoProduccion(
                orden_id=orden.id,
                cantidad=cantidad_p,
                creado_por=g.usuario_actual.id
            ))

            # 6. Actualizar Estatus de la Orden
            orden.cantidad_producida += cantidad_p
            if orden.cantidad_producida >= orden.cantidad_solicitada:
                orden.estatus = 'completada'
                orden.fecha_fin = datetime.utcnow()
            elif orden.estatus == 'pendiente':
                orden.estatus = 'en_proceso'
                orden.fecha_inicio = datetime.utcnow()

            db.session.commit()
            flash(f"Producción de {cantidad_p} unidades registrada.", "success")
            return redirect(url_for("explosion.detalle", id=encrypt_id(orden.id)))

        except Exception as e:
            db.session.rollback()
            flash(f"Error al procesar: {str(e)}", "error")
            return redirect(request.url)

    return render_template("explosion/capturar_produccion.html", orden=orden)


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
