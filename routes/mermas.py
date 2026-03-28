# routes/mermas.py
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from database.mysql import db, OrdenProduccion, MovimientoInventario, TipoMovimiento, StockArticulo
from middlerware import login_requerido, permiso_requerido, decrypt_url_id
from utils.crypto_url import encrypt_id
from decimal import Decimal
import datetime

mermas = Blueprint("mermas", __name__, url_prefix="/mermas")

@mermas.route("/")
@login_requerido
@permiso_requerido("mermas", "ver")
def lista():
    return render_template(
        "mermas/lista.html",
        titulo="Administración de Mermas",
        descripcion="Gestión de mermas en el sistema",
    )

@mermas.route("/crear/<orden_id>")
@decrypt_url_id()
@login_requerido
@permiso_requerido("mermas", "crear")
def crear(orden_id):
    orden = OrdenProduccion.query.get_or_404(orden_id)
    
    # Verificar que la orden esté en estado válido para registrar mermas
    if orden.estatus not in ['en_proceso', 'completada']:
        flash("Solo se pueden registrar mermas en órdenes en proceso o completadas.", "warning")
        return redirect(url_for('explosion.detalle', id=encrypt_id(orden.id)))
    
    return render_template(
        "mermas/crear.html",
        titulo=f"Registrar mermas - Orden #{orden.id}",
        descripcion="Captura de mermas por materia prima",
        orden=orden,
        orden_id_encrypted=encrypt_id(orden.id),
    )

@mermas.route("/guardar", methods=["POST"])
@login_requerido
@permiso_requerido("mermas", "crear")
def guardar():
    try:
        data = request.get_json()
        orden_id = data.get('orden_id')
        mermas = data.get('mermas', [])
        merma_global = data.get('merma_global')
        
        if not orden_id:
            return jsonify({'success': False, 'error': 'ID de orden no proporcionado'}), 400
        
        orden = OrdenProduccion.query.get_or_404(orden_id)
        
        # Obtener el tipo de movimiento para mermas
        tipo_mov_merma = TipoMovimiento.query.filter_by(tipo="Salida por merma").first()
        if not tipo_mov_merma:
            # Crear tipo de movimiento si no existe
            tipo_mov_merma = TipoMovimiento(
                tipo="Salida por merma",
                descripcion="Salida de inventario por merma en producción"
            )
            db.session.add(tipo_mov_merma)
            db.session.flush()
        
        # Procesar merma global (afecta a todas las materias primas proporcionalmente)
        if merma_global and merma_global > 0:
            if merma_global > orden.cantidad_solicitada - orden.cantidad_producida:
                return jsonify({
                    'success': False, 
                    'error': f'La merma global no puede exceder la cantidad pendiente de producir ({orden.cantidad_solicitada - orden.cantidad_producida})'
                }), 400
            
            # Calcular factor de merma
            factor_merma = merma_global / orden.cantidad_solicitada
            
            for detalle in orden.receta.detalles:
                mp = detalle.materia_prima
                cantidad_merma = detalle.cantidad_neta * factor_merma
                
                if cantidad_merma > 0:
                    _registrar_merma(mp, cantidad_merma, orden, tipo_mov_merma)
        
        # Procesar mermas individuales
        for merma in mermas:
            mp_id = merma.get('materia_prima_id')
            cantidad = Decimal(str(merma.get('cantidad')))
            
            if cantidad <= 0:
                continue
            
            # Buscar la materia prima en los detalles de la receta
            mp_encontrada = None
            for detalle in orden.receta.detalles:
                if detalle.materia_prima_id == mp_id:
                    mp_encontrada = detalle.materia_prima
                    break
            
            if not mp_encontrada:
                continue
            
            _registrar_merma(mp_encontrada, cantidad, orden, tipo_mov_merma)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Mermas registradas correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

def _registrar_merma(materia_prima, cantidad, orden, tipo_movimiento):
    """Registra una merma en el inventario"""
    if not materia_prima.articulo_id:
        return
    
    # Buscar stock en almacén de materia prima
    stock = StockArticulo.query.filter_by(
        articulo_id=materia_prima.articulo_id
    ).join(StockArticulo.inventario).filter(
        Inventario.nombre.ilike("%materia%")
    ).first()
    
    if not stock:
        # Buscar cualquier almacén disponible
        stock = StockArticulo.query.filter_by(
            articulo_id=materia_prima.articulo_id
        ).first()
    
    if stock and stock.cantidad >= cantidad:
        stock.cantidad -= cantidad
        
        # Registrar movimiento
        movimiento = MovimientoInventario(
            articulo_id=materia_prima.articulo_id,
            tipo_mov_id=tipo_movimiento.id,
            inv_id=stock.inv_id,
            cantidad=cantidad,
            unidad_id=materia_prima.unidad_id,
            signo=-1,
            existencia=stock.cantidad,
            descripcion=f"Merma en orden #{orden.id}"
        )
        db.session.add(movimiento)