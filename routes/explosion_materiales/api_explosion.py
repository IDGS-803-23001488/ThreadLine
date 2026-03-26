# routes/explosion/api_explosion.py
from flask import Blueprint, request, g, jsonify
from sqlalchemy import or_
from database.mysql import (
    db, OrdenProduccion, Receta, ProductoVariante, Producto, Talla, 
    Inventario
)
from securrity.middlerware import login_requerido, permiso_requerido
from routes.explosion_materiales.explosion import _calcular_insumos

apiExplosion = Blueprint("api_explosion", __name__, url_prefix="/api/explosion")


@apiExplosion.route("/recetas", methods=["GET"])
@login_requerido
@permiso_requerido("explosion", "crear")
def api_recetas():
    q = request.args.get("q", "", type=str)
    page = request.args.get("page", 1, type=int)
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
            "id": r.id,
            "producto": r.producto_variante.producto.nombre,
            "talla": r.producto_variante.talla.nombre,
            "color": r.producto_variante.producto.color.nombre if r.producto_variante.producto.color else None,
            "color_hex": r.producto_variante.producto.color.hex if r.producto_variante.producto.color else None,
            "cantidad_base": r.cantidad_base,
            "insumos": len(r.detalles),
        } for r in pag.items],
        "total": pag.total,
        "pages": pag.pages,
        "page": pag.page,
        "has_next": pag.has_next,
        "has_prev": pag.has_prev,
    })

@apiExplosion.route("/validar", methods=["GET"])
@login_requerido
@permiso_requerido("explosion", "crear")
def api_validar():
    receta_id = request.args.get("receta_id", type=int)
    cantidad = request.args.get("cantidad", type=int)
    inv_id = request.args.get("inv_id", type=int)

    if not receta_id or not cantidad or cantidad < 1:
        return jsonify({"error": "Parámetros inválidos"}), 400

    receta = Receta.query.get_or_404(receta_id)
    faltantes, insumos = _calcular_insumos(receta, cantidad, inv_id)

    return jsonify({
        "viable": not faltantes,
        "faltantes": faltantes,
        "insumos": [{
            "nombre": i["materia_prima"].nombre,
            "unidad": i["materia_prima"].unidad.sigla if i["materia_prima"].unidad else "—",
            "cantidad_neta": float(i["cantidad_neta"]),
            "stock_disponible": float(i["stock_disponible"]),
            "suficiente": i["suficiente"],
            "faltante": float(i["faltante"]),
        } for i in insumos],
    })

@apiExplosion.route("/inventarios", methods=["GET"])
@login_requerido
@permiso_requerido("explosion", "crear")
def api_inventarios():
    invs = Inventario.query.filter_by(activo=True, tipo=False).order_by(Inventario.nombre).all()
    return jsonify({"data": [{"id": i.id, "nombre": i.nombre} for i in invs]})

@apiExplosion.route("/producir/<int:orden_id>", methods=["POST"])
@login_requerido
@permiso_requerido("explosion", "editar")
def api_producir(orden_id):
    # ... (Aquí va toda la lógica de producción que ya tienes, 
    # incluyendo el procesamiento de mermas y actualización de stock)
    # Se omite por brevedad pero debe ir íntegra aquí.
    pass

@apiExplosion.route("/insumos/<int:orden_id>", methods=["GET"])
@login_requerido
@permiso_requerido("explosion", "ver")
def api_insumos(orden_id):
    orden = OrdenProduccion.query.get_or_404(orden_id)
    return jsonify({
        "insumos": [{
            "materia_prima_id": d.materia_prima_id,
            "nombre": d.materia_prima.nombre,
            "unidad": d.materia_prima.unidad.sigla if d.materia_prima.unidad else "—",
        } for d in orden.receta.detalles]
    })