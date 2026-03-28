# routes/explosion_materiales/api_explosion.py
from decimal import Decimal
from flask import Blueprint, request, g, jsonify
from sqlalchemy import or_
from database.mysql import (
    db, OrdenProduccion, Receta, ProductoVariante, Producto, Talla,
    Inventario, StockArticulo, OrdenProduccionInsumo, MovimientoInventario,
    TipoMovimiento, Articulo
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


# ── Producir (actualiza cantidad producida y resta insumos) ─────────────────
@apiExplosion.route("/producir/<int:orden_id>", methods=["POST"])
@login_requerido
@permiso_requerido("explosion", "editar")
def api_producir(orden_id):
    """
    Endpoint para registrar producción:
    - Recibe la cantidad producida
    - Resta los insumos asignados proporcionalmente
    - Actualiza el stock en los almacenes correspondientes
    - Registra movimientos de inventario
    """
    try:
        data = request.get_json()
        cantidad_producida = data.get('cantidad', type=int)
        
        if not cantidad_producida or cantidad_producida <= 0:
            return jsonify({"error": "Cantidad inválida"}), 400
        
        orden = OrdenProduccion.query.get_or_404(orden_id)
        
        # Validar que la cantidad no exceda lo solicitado
        max_producir = orden.cantidad_solicitada - orden.cantidad_producida
        if cantidad_producida > max_producir:
            return jsonify({
                "error": f"No se puede producir más de {max_producir} unidades"
            }), 400
        
        # Validar que la orden esté en estado pendiente o en_proceso
        if orden.estatus not in ['pendiente', 'en_proceso']:
            return jsonify({
                "error": "Solo se puede producir en órdenes pendientes o en proceso"
            }), 400
        
        # Obtener el tipo de movimiento para salida de producción
        tipo_mov_salida = TipoMovimiento.query.filter_by(tipo="Salida producción").first()
        if not tipo_mov_salida:
            return jsonify({"error": "Tipo de movimiento 'Salida producción' no encontrado"}), 500
        
        # Calcular el factor de producción
        factor_produccion = Decimal(str(cantidad_producida)) / Decimal(str(orden.cantidad_solicitada))
        
        # Procesar cada insumo asignado
        for insumo in orden.insumos_asignados:
            # Calcular la cantidad a consumir de este insumo
            cantidad_consumir = insumo.cantidad * factor_produccion
            
            if cantidad_consumir <= 0:
                continue
            
            # Buscar el stock actual
            stock = StockArticulo.query.filter_by(
                articulo_id=insumo.materia_prima.articulo_id,
                inv_id=insumo.inv_id
            ).first()
            
            if not stock:
                return jsonify({
                    "error": f"No hay stock registrado para {insumo.materia_prima.nombre} en {insumo.inventario.nombre}"
                }), 400
            
            # Validar stock suficiente
            if stock.cantidad < cantidad_consumir:
                return jsonify({
                    "error": f"Stock insuficiente para {insumo.materia_prima.nombre}. "
                            f"Disponible: {stock.cantidad}, Requerido: {cantidad_consumir}"
                }), 400
            
            # Restar del stock
            stock.cantidad -= cantidad_consumir
            stock.actualizado_por = g.usuario_actual.id
            
            # Registrar movimiento de inventario
            movimiento = MovimientoInventario(
                articulo_id=insumo.materia_prima.articulo_id,
                tipo_mov_id=tipo_mov_salida.id,
                inv_id=insumo.inv_id,
                cantidad=cantidad_consumir,
                unidad_id=insumo.unidad_id,
                signo=-1,
                existencia=stock.cantidad,
                descripcion=f"Consumo para orden #{orden.id} - Producción de {cantidad_producida} unidades"
            )
            db.session.add(movimiento)
        
        # Actualizar la orden
        orden.cantidad_producida += cantidad_producida
        
        # Actualizar estatus si es necesario
        if orden.cantidad_producida >= orden.cantidad_solicitada:
            orden.estatus = 'completada'
            orden.fecha_fin = datetime.datetime.utcnow()
        elif orden.estatus == 'pendiente':
            orden.estatus = 'en_proceso'
            orden.fecha_inicio = datetime.datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Producción de {cantidad_producida} unidades registrada correctamente",
            "orden": {
                "id": orden.id,
                "cantidad_producida": orden.cantidad_producida,
                "cantidad_solicitada": orden.cantidad_solicitada,
                "estatus": orden.estatus,
                "porcentaje": round((orden.cantidad_producida / orden.cantidad_solicitada) * 100, 2)
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ── Obtener detalle de una orden ──────────────────────────────────────────────
@apiExplosion.route("/orden/<int:orden_id>", methods=["GET"])
@login_requerido
@permiso_requerido("explosion", "ver")
def api_orden(orden_id):
    """Obtiene el detalle completo de una orden"""
    orden = OrdenProduccion.query.get_or_404(orden_id)
    
    return jsonify({
        "id": orden.id,
        "receta_id": orden.receta_id,
        "cantidad_solicitada": orden.cantidad_solicitada,
        "cantidad_producida": orden.cantidad_producida,
        "estatus": orden.estatus,
        "fecha_inicio": orden.fecha_inicio.isoformat() if orden.fecha_inicio else None,
        "fecha_fin": orden.fecha_fin.isoformat() if orden.fecha_fin else None,
        "producto": orden.receta.producto_variante.producto.nombre,
        "talla": orden.receta.producto_variante.talla.nombre,
        "color": orden.receta.producto_variante.producto.color.nombre if orden.receta.producto_variante.producto.color else None,
        "porcentaje": round((orden.cantidad_producida / orden.cantidad_solicitada) * 100, 2) if orden.cantidad_solicitada > 0 else 0,
        "insumos_asignados": [{
            "id": ins.id,
            "materia_prima": ins.materia_prima.nombre,
            "cantidad": float(ins.cantidad),
            "unidad": ins.unidad.sigla if ins.unidad else "—",
            "inventario": ins.inventario.nombre
        } for ins in orden.insumos_asignados]
    })