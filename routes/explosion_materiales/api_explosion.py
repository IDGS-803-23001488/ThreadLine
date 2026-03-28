# routes/explosion_materiales/api_explosion.py
from decimal import Decimal
from flask import Blueprint, request, g, jsonify
from sqlalchemy import or_
from database.mysql import (
    db, OrdenProduccion, Receta, ProductoVariante, Producto, Talla,
    Inventario, StockArticulo
)
from middlerware import login_requerido, permiso_requerido
from routes.explosion_materiales.explosion import _calcular_insumos_multi

apiExplosion = Blueprint("api_explosion", __name__, url_prefix="/api/explosion")


# ── Recetas disponibles (paginadas, con búsqueda) ────────────────────────────
@apiExplosion.route("/recetas", methods=["GET"])
@login_requerido
@permiso_requerido("explosion", "crear")
def api_recetas():
    q        = request.args.get("q", "", type=str)
    page     = request.args.get("page", 1, type=int)
    per_page = 8

    query = (
        Receta.query.filter_by(activo=True)
        .join(Receta.producto_variante)
        .join(ProductoVariante.producto)
        .join(ProductoVariante.talla)
    )

    if q:
        query = query.filter(or_(
            Producto.nombre.ilike(f"%{q}%"),
            Talla.nombre.ilike(f"%{q}%"),
        ))

    pag = query.order_by(Producto.nombre.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "data": [{
            "id":            r.id,
            "producto":      r.producto_variante.producto.nombre,
            "talla":         r.producto_variante.talla.nombre,
            "color":         r.producto_variante.producto.color.nombre
                             if r.producto_variante.producto.color else None,
            "color_hex":     r.producto_variante.producto.color.hex
                             if r.producto_variante.producto.color else None,
            "cantidad_base": r.cantidad_base,
            "insumos":       len(r.detalles),
        } for r in pag.items],
        "total":    pag.total,
        "pages":    pag.pages,
        "page":     pag.page,
        "has_next": pag.has_next,
        "has_prev": pag.has_prev,
    })


# ── Validar explosión contra múltiples almacenes ─────────────────────────────
@apiExplosion.route("/validar", methods=["GET"])
@login_requerido
@permiso_requerido("explosion", "crear")
def api_validar():
    receta_id = request.args.get("receta_id", type=int)
    cantidad  = request.args.get("cantidad",  type=int)
    # El frontend envía: ?inv_ids[]=1&inv_ids[]=3
    inv_ids   = request.args.getlist("inv_ids[]", type=int)

    if not receta_id or not cantidad or cantidad < 1:
        return jsonify({"error": "Parámetros inválidos"}), 400

    if not inv_ids:
        return jsonify({"error": "Debes seleccionar al menos un almacén"}), 400

    receta    = Receta.query.get_or_404(receta_id)
    factor    = Decimal(str(cantidad)) / Decimal(str(receta.cantidad_base))
    faltantes, tramos = _calcular_insumos_multi(receta, cantidad, inv_ids)

    # ── Construir resumen por materia prima ──────────────────────────────────
    # Calculamos cantidad requerida y stock total sumando todos los almacenes
    insumos_out = []
    for detalle in receta.detalles:
        mp             = detalle.materia_prima
        cantidad_neta  = round(Decimal(str(detalle.cantidad_neta)) * factor, 4)

        stock_total = sum(
            (StockArticulo.query.filter_by(
                articulo_id=mp.articulo_id, inv_id=inv_id
            ).first() or _stock_cero()).cantidad
            for inv_id in inv_ids
        )

        suficiente = stock_total >= cantidad_neta
        faltante   = max(Decimal("0"), cantidad_neta - stock_total)

        # Detalle por almacén (cuánto hay en cada uno)
        detalle_inv = []
        for inv_id in inv_ids:
            s = StockArticulo.query.filter_by(
                articulo_id=mp.articulo_id, inv_id=inv_id
            ).first()
            inv = Inventario.query.get(inv_id)
            detalle_inv.append({
                "inv_id":     inv_id,
                "nombre_inv": inv.nombre if inv else "—",
                "disponible": float(s.cantidad) if s else 0.0,
            })

        insumos_out.append({
            "nombre":           mp.nombre,
            "unidad":           mp.unidad.sigla if mp.unidad else "—",
            "cantidad_neta":    float(cantidad_neta),
            "stock_disponible": float(round(stock_total, 4)),
            "suficiente":       suficiente,
            "faltante":         float(round(faltante, 4)),
            "almacenes":        detalle_inv,
        })

    return jsonify({
        "viable":    not faltantes,
        "faltantes": faltantes,
        "insumos":   insumos_out,
    })


def _stock_cero():
    """Objeto ficticio con cantidad=0 para simplificar la suma."""
    class _S:
        cantidad = Decimal("0")
    return _S()


# ── Lista de almacenes de materia prima ──────────────────────────────────────
@apiExplosion.route("/inventarios", methods=["GET"])
@login_requerido
@permiso_requerido("explosion", "crear")
def api_inventarios():
    invs = (
        Inventario.query
        .filter_by(activo=True, tipo=False)
        .order_by(Inventario.nombre)
        .all()
    )
    return jsonify({"data": [{"id": i.id, "nombre": i.nombre} for i in invs]})


# ── Insumos asignados a una orden (para captura posterior) ───────────────────
@apiExplosion.route("/insumos/<int:orden_id>", methods=["GET"])
@login_requerido
@permiso_requerido("explosion", "ver")
def api_insumos(orden_id):
    orden = OrdenProduccion.query.get_or_404(orden_id)
    return jsonify({
        "insumos": [{
            "materia_prima_id": ins.materia_prima_id,
            "nombre":           ins.materia_prima.nombre,
            "unidad":           ins.unidad.sigla if ins.unidad else "—",
            "inv_id":           ins.inv_id,
            "inventario":       ins.inventario.nombre,
            "cantidad":         float(ins.cantidad),
        } for ins in orden.insumos_asignados]
    })


# ── Producir (placeholder — mantener lógica existente aquí) ─────────────────
@apiExplosion.route("/producir/<int:orden_id>", methods=["POST"])
@login_requerido
@permiso_requerido("explosion", "editar")
def api_producir(orden_id):
    # Aquí va la lógica de producción/mermas existente
    pass