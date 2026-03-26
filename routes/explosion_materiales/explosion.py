# routes/explosion.py
import datetime
from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify
from sqlalchemy import or_
from database.mysql import (
    db, OrdenProduccion, Receta, RecetaDetalle,
    ProductoVariante, Producto, Talla, MateriaPrima,
    StockArticulo, Inventario, MovimientoInventario, TipoMovimiento,
    MermaEncabezado, MermaDetalle, Articulo  # ← Asegurar imports
)
from securrity.middlerware import login_requerido, permiso_requerido, decrypt_url_id
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
    inv_mp_id = request.form.get("inv_id", type=int)      # almacén de MP
    forzar    = request.form.get("forzar", "0") == "1"    # ignorar faltantes

    # — Validaciones básicas —
    if not receta_id or not cantidad or cantidad < 1:
        flash("Receta y cantidad son requeridas.", "error")
        return redirect(url_for("explosion.nueva"))

    receta = Receta.query.get_or_404(receta_id)

    # — Calcular insumos necesarios —
    faltantes, insumos = _calcular_insumos(receta, cantidad, inv_mp_id)

    if faltantes and not forzar:
        flash("Inventario insuficiente para generar la orden. Revisa los faltantes.", "warning")
        return redirect(url_for("explosion.nueva"))

    # — Crear orden —
    orden = OrdenProduccion(
        receta_id=receta_id,
        cantidad_solicitada=cantidad,
        cantidad_producida=0,
        estatus="pendiente",
    )
    db.session.add(orden)
    db.session.flush()

    # — Descontar materia prima del stock —
    INV_MP = inv_mp_id or _inv_mp_default()
    tipo_mov = TipoMovimiento.query.filter_by(tipo="Salida producción").first()

    for insumo in insumos:
        mp    = insumo["materia_prima"]
        cant  = insumo["cantidad_neta"]  # Ya no se usa merma

        # Actualizar stock estático
        stock = StockArticulo.query.filter_by(
            articulo_id=mp.articulo_id, inv_id=INV_MP
        ).first()

        if stock:
            stock.cantidad       = max(Decimal("0"), stock.cantidad - Decimal(str(cant)))
            stock.actualizado_por = g.usuario_actual.id
        # Si no existe el stock, se omite (forzar=True lo permite)

        # Registrar movimiento
        if tipo_mov and mp.articulo_id:
            existencia_actual = stock.cantidad if stock else Decimal("0")
            mov = MovimientoInventario(
                articulo_id=mp.articulo_id,
                tipo_mov_id=tipo_mov.id,
                inv_id=INV_MP,
                cantidad=Decimal(str(cant)),
                unidad_id=mp.unidad_id,
                signo=-1,
                existencia=existencia_actual,
            )
            db.session.add(mov)

    db.session.commit()
    flash(f"Orden #{orden.id} generada correctamente.", "success")
    return redirect(url_for("explosion.detalle", id=encrypt_id(orden.id)))


def _calcular_insumos(receta: Receta, cantidad: int, inv_id: int):
    """
    Retorna (faltantes: bool, insumos: list[dict])
    donde cada insumo tiene: materia_prima, cantidad_neta,
    stock_disponible, suficiente.
    """
    INV_MP   = inv_id or _inv_mp_default()
    faltantes = False
    insumos   = []

    factor = Decimal(str(cantidad)) / Decimal(str(receta.cantidad_base))

    for detalle in receta.detalles:
        mp      = detalle.materia_prima
        c_neta  = Decimal(str(detalle.cantidad_neta)) * factor

        # Stock disponible
        stock = StockArticulo.query.filter_by(
            articulo_id=mp.articulo_id, inv_id=INV_MP
        ).first()
        disponible = stock.cantidad if stock else Decimal("0")
        suficiente = disponible >= c_neta

        if not suficiente:
            faltantes = True

        insumos.append({
            "materia_prima":      mp,
            "cantidad_neta":      round(c_neta,  4),
            "stock_disponible":   disponible,
            "suficiente":         suficiente,
            "faltante":           max(Decimal("0"), c_neta - disponible),
        })

    return faltantes, insumos


def _inv_mp_default():
    """ID del almacén de Materia Prima (fallback al primero disponible)."""
    inv = Inventario.query.filter(
        Inventario.nombre.ilike("%materia%"), Inventario.activo == True
    ).first()
    return inv.id if inv else 2   # fallback al id=2 del seed
