# routes/mermas.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, g
from database.mysql import (
    db, OrdenProduccion, OrdenProduccionInsumo,
    MermaEncabezado, MermaDetalle,
)
from middlerware import login_requerido, permiso_requerido, decrypt_url_id
from utils.crypto_url import encrypt_id
from decimal import Decimal, InvalidOperation
import json
import logging

logger = logging.getLogger(__name__)

mermas = Blueprint("mermas", __name__, url_prefix="/mermas")


# ══════════════════════════════════════════════════════
# LISTA
# ══════════════════════════════════════════════════════
@mermas.route("/")
@login_requerido
@permiso_requerido("mermas", "ver")
def lista():
    return render_template(
        "mermas/lista.html",
        titulo="Administración de Mermas",
        descripcion="Gestión de mermas en el sistema",
    )


# ══════════════════════════════════════════════════════
# CREAR (vista)
# ══════════════════════════════════════════════════════
@mermas.route("/crear/<orden_id>")
@decrypt_url_id("orden_id")
@login_requerido
@permiso_requerido("mermas", "crear")
def crear(orden_id):
    orden = OrdenProduccion.query.get_or_404(orden_id)

    if orden.estatus not in ['pendiente', 'en_proceso', 'completada']:
        flash("Solo se pueden registrar mermas en órdenes válidas.", "warning")
        return redirect(url_for('explosion.detalle', id=encrypt_id(orden.id)))

    return render_template(
        "mermas/crear.html",
        titulo=f"Registrar mermas - Orden #{orden.id}",
        descripcion="Captura de mermas por materia prima",
        orden=orden,
        orden_id_encrypted=encrypt_id(orden.id),
    )


# ══════════════════════════════════════════════════════
# GUARDAR
# Flujo:
#   1. Validar datos del formulario
#   2. Crear MermaEncabezado ligado a la OrdenProduccion
#   3. Por cada materia prima con merma:
#        a. Descontar de OrdenProduccionInsumo.cantidad
#        b. Insertar MermaDetalle
#   4. Commit único al final
# ══════════════════════════════════════════════════════
@mermas.route("/guardar", methods=["POST"])
@login_requerido
@permiso_requerido("mermas", "crear")
def guardar():

    # ── 1. orden_id ────────────────────────────────────────────────────
    orden_id_raw = request.form.get('orden_id', '').strip()
    try:
        orden_id = int(orden_id_raw)
    except (ValueError, TypeError):
        flash(f'orden_id inválido: "{orden_id_raw}"', 'danger')
        return redirect(request.referrer or url_for('mermas.lista'))

    orden = OrdenProduccion.query.get(orden_id)
    if not orden:
        flash(f'Orden #{orden_id} no encontrada.', 'danger')
        return redirect(url_for('mermas.lista'))

    url_detalle = url_for('explosion.detalle', id=encrypt_id(orden.id))

    # ── 2. Leer campos del formulario ───────────────────────────────────
    merma_global_raw = request.form.get('merma_global', '').strip()
    mermas_json_raw  = request.form.get('mermas_json',  '').strip()

    tiene_global      = merma_global_raw not in ('', '0', '0.0', '0.0000')
    tiene_individuales = bool(mermas_json_raw and mermas_json_raw != '[]')

    if not tiene_global and not tiene_individuales:
        flash('No se recibió ninguna merma con cantidad mayor a 0.', 'warning')
        return redirect(url_detalle)

    try:
        usuario_id = getattr(g, 'usuario_id', None) or getattr(g, 'user_id', None)

        # ── Crear encabezado (uno por envío, ligado a la orden) ─────────
        encabezado = MermaEncabezado(
            orden_produccion_id=orden.id,
            creado_por=usuario_id,
        )
        db.session.add(encabezado)
        db.session.flush()      # genera encabezado.id sin hacer commit

        registros = 0

        # ════════════════════════════════════════════════
        # MERMA GLOBAL — distribuye proporcional por insumo
        # ════════════════════════════════════════════════
        if tiene_global:
            try:
                merma_global = Decimal(merma_global_raw)
            except InvalidOperation:
                flash(f'Cantidad global inválida: "{merma_global_raw}"', 'danger')
                db.session.rollback()
                return redirect(url_detalle)

            if merma_global <= 0:
                flash('La merma global debe ser mayor a 0.', 'danger')
                db.session.rollback()
                return redirect(url_detalle)

            cant_solicitada = Decimal(str(orden.cantidad_solicitada))
            if merma_global > cant_solicitada:
                flash(
                    f'La merma global ({merma_global}) supera '
                    f'la cantidad solicitada ({cant_solicitada}).',
                    'danger'
                )
                db.session.rollback()
                return redirect(url_detalle)

            if not orden.insumos:
                flash('La orden no tiene insumos registrados.', 'danger')
                db.session.rollback()
                return redirect(url_detalle)

            factor = merma_global / cant_solicitada
            for ins in orden.insumos:
                cantidad_merma = (Decimal(str(ins.cantidad)) * factor).quantize(Decimal('0.0001'))
                if cantidad_merma <= 0:
                    continue
                _descontar_insumo(ins, cantidad_merma)
                _insertar_detalle(encabezado.id, ins.materia_prima_id, cantidad_merma)
                registros += 1

        # ════════════════════════════════════════════════
        # MERMAS INDIVIDUALES
        # ════════════════════════════════════════════════
        if tiene_individuales:
            try:
                mermas_list = json.loads(mermas_json_raw)
            except json.JSONDecodeError as exc:
                flash(f'Datos de mermas individuales malformados: {exc}', 'danger')
                db.session.rollback()
                return redirect(url_detalle)

            for item in mermas_list:
                mp_id_raw = item.get('materia_prima_id')
                cant_raw  = item.get('cantidad')

                try:
                    mp_id = int(mp_id_raw)
                except (ValueError, TypeError):
                    flash(f'materia_prima_id inválido: "{mp_id_raw}"', 'danger')
                    db.session.rollback()
                    return redirect(url_detalle)

                try:
                    cantidad = Decimal(str(cant_raw))
                except (InvalidOperation, TypeError):
                    flash(f'Cantidad inválida para mp_id {mp_id}: "{cant_raw}"', 'danger')
                    db.session.rollback()
                    return redirect(url_detalle)

                if cantidad <= 0:
                    continue

                insumo = next(
                    (i for i in orden.insumos if i.materia_prima_id == mp_id),
                    None
                )
                if not insumo:
                    ids_disponibles = [i.materia_prima_id for i in orden.insumos]
                    flash(
                        f'El insumo con materia_prima_id={mp_id} no pertenece '
                        f'a la orden #{orden.id}. IDs disponibles: {ids_disponibles}',
                        'danger'
                    )
                    db.session.rollback()
                    return redirect(url_detalle)

                cantidad_asignada = Decimal(str(insumo.cantidad))
                if cantidad > cantidad_asignada:
                    flash(
                        f'La merma de "{insumo.materia_prima.nombre}" '
                        f'({cantidad}) supera lo asignado ({cantidad_asignada}).',
                        'danger'
                    )
                    db.session.rollback()
                    return redirect(url_detalle)

                _descontar_insumo(insumo, cantidad)
                _insertar_detalle(encabezado.id, mp_id, cantidad)
                registros += 1

        if registros == 0:
            flash('No se generó ningún descuento. Verifica que las cantidades sean mayores a 0.', 'warning')
            db.session.rollback()
            return redirect(url_detalle)

        db.session.commit()
        flash(f'{registros} merma(s) registrada(s) correctamente.', 'success')
        return redirect(url_detalle)

    except Exception as e:
        db.session.rollback()
        logger.exception("mermas.guardar — error no controlado")
        flash(f'Error inesperado: {e}', 'danger')
        return redirect(url_detalle)


# ══════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════
def _descontar_insumo(insumo: OrdenProduccionInsumo, cantidad_merma: Decimal) -> None:
    """Resta la merma de la cantidad asignada al insumo en la orden."""
    cantidad_actual = Decimal(str(insumo.cantidad))
    nueva_cantidad  = cantidad_actual - cantidad_merma

    if nueva_cantidad < 0:
        logger.warning(
            "merma (%s) > cantidad asignada (%s) en insumo id=%s — forzado a 0",
            cantidad_merma, cantidad_actual, insumo.id,
        )
        nueva_cantidad = Decimal('0')

    insumo.cantidad = nueva_cantidad
    logger.debug(
        "Insumo id=%s | mp='%s' | %s → %s (merma: %s)",
        insumo.id, insumo.materia_prima.nombre,
        cantidad_actual, nueva_cantidad, cantidad_merma,
    )


def _insertar_detalle(merma_id: int, materia_prima_id: int, cantidad: Decimal) -> None:
    """Inserta un MermaDetalle asociado al encabezado."""
    db.session.add(MermaDetalle(
        merma_id=merma_id,
        materia_prima_id=materia_prima_id,
        cantidad=cantidad,
    ))