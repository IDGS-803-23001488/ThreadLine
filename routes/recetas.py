# routes/recetas.py
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify
from database.mysql import db, Receta, RecetaDetalle, ProductoVariante, MateriaPrima, Producto, Talla, Color
from middlerware import login_requerido, permiso_requerido, decrypt_url_id
from sqlalchemy import or_

recetas = Blueprint(
    "recetas",
    __name__,
    url_prefix="/recetas"
)

apiRecetas = Blueprint(
    "api_recetas",
    __name__,
    url_prefix="/api/recetas"
)

# ===========================================
# Vistas
# ===========================================


#===========================================
# Lista 
#===========================================
@recetas.route("/")
@login_requerido
@permiso_requerido("recetas", "ver")
def lista():
    search = request.args.get("search", "", type=str)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    query = (
        Receta.query
        .filter(Receta.activo == True)
        .join(Receta.producto_variante)
        .join(ProductoVariante.producto)
        .join(ProductoVariante.talla)
        .outerjoin(Producto.color)
    )

    if search:
        query = query.filter(
            or_(
                Producto.nombre.ilike(f"%{search}%"),
                Talla.nombre.ilike(f"%{search}%"),
            )
        )

    pagination = query.order_by(Receta.id.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    rows = [
        [
            ("ID",           r.id),
            ("Producto",     r.producto_variante.producto.nombre),
            ("Talla",        r.producto_variante.talla.nombre),
            ("Color",        r.producto_variante.producto.color.nombre if r.producto_variante.producto.color else "—"),
            ("Cantidad Base",r.cantidad_base),
            ("Insumos",      len(r.detalles)),
        ]
        for r in pagination.items
    ]

    return render_template(
        "recetas/lista.html",
        headers=["ID", "Producto", "Talla", "Color", "Cantidad Base", "Insumos"],
        rows=rows,
        pagination=pagination,
        search=search,
        per_page=per_page,
        endpoint="recetas",
        titulo="Recetas",
        descripcion="Listado general de recetas",
    )

@recetas.route("/crear", methods=["GET", "POST"])
@login_requerido
@permiso_requerido("recetas", "crear")
def crear():
    if request.method == "POST":
        return _guardar_receta(receta_id=None)

    return render_template(
        "recetas/crear.html",
        titulo="Crear Receta",
        descripcion="Registro de nueva receta de producción",
    )


@recetas.route("/editar/<id>", methods=["GET", "POST"])
@decrypt_url_id()
@login_requerido
@permiso_requerido("recetas", "editar")
def editar(id):
    receta = Receta.query.get_or_404(id)

    if request.method == "POST":
        return _guardar_receta(receta_id=id)

    return render_template(
        "recetas/crear.html",
        titulo="Editar Receta",
        descripcion="Modificación de receta de producción",
        receta=receta,
    )


# ===========================================
# Lógica compartida crear / editar
# ===========================================

def _guardar_receta(receta_id):
    variante_id   = request.form.get("producto_variante_id", type=int)
    cantidad_base = request.form.get("cantidad_base", 1, type=int)
    mp_ids        = request.form.getlist("materia_prima_id")
    cantidades    = request.form.getlist("cantidad_neta")

    # --- Validaciones ---
    errores = []
    if not variante_id:
        errores.append("Debes seleccionar una variante de producto.")
    if not mp_ids:
        errores.append("La receta debe tener al menos un insumo.")
    if len(mp_ids) != len(cantidades):
        errores.append("Error en el formulario: insumos y cantidades no coinciden.")
    if len(mp_ids) != len(set(mp_ids)):
        errores.append("Hay materias primas duplicadas en la receta.")

    if errores:
        for e in errores:
            flash(e, "error")
        return redirect(request.url)

    # --- Guardar ---
    if receta_id:
        receta = Receta.query.get_or_404(receta_id)
        receta.producto_variante_id = variante_id
        receta.cantidad_base        = cantidad_base
        receta.fecha_edicion        = datetime.datetime.utcnow()
        receta.editado_por          = g.usuario_actual.id
        # Borrar detalles anteriores y recrear
        RecetaDetalle.query.filter_by(receta_id=receta_id).delete()
    else:
        receta = Receta(
            producto_variante_id=variante_id,
            cantidad_base=cantidad_base,
            activo=True,
            creado_por=g.usuario_actual.id,
        )
        db.session.add(receta)
        db.session.flush()

    for mp_id, cant in zip(mp_ids, cantidades):
        detalle = RecetaDetalle(
            receta_id=receta.id,
            materia_prima_id=int(mp_id),
            cantidad_neta=float(cant),
        )
        db.session.add(detalle)

    db.session.commit()
    flash("Receta guardada correctamente.", "success")
    return redirect(url_for("recetas.lista"))


# ===========================================
# API — Variantes (para modal buscador)
# ===========================================

@apiRecetas.route("/variantes", methods=["GET"])
@login_requerido
@permiso_requerido("recetas", "crear")
def api_variantes():
    search   = request.args.get("q", "", type=str)
    page     = request.args.get("page", 1, type=int)
    per_page = 10

    query = (
        ProductoVariante.query
        .join(Producto)
        .join(Talla)
        .filter(ProductoVariante.activo == True, Producto.activo == True)
    )

    if search:
        query = query.filter(
            or_(
                Producto.nombre.ilike(f"%{search}%"),
                Talla.nombre.ilike(f"%{search}%"),
            )
        )

    pag = query.order_by(Producto.nombre.asc(), Talla.orden.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "data": [
            {
                "id":       v.id,
                "producto": v.producto.nombre,
                "talla":    v.talla.nombre,
                "color":    v.producto.color.nombre if v.producto.color else None,
                "color_hex": v.producto.color.hex  if v.producto.color else None,
                "precio":   float(v.precio_venta),
            }
            for v in pag.items
        ],
        "total":    pag.total,
        "pages":    pag.pages,
        "page":     pag.page,
        "has_next": pag.has_next,
        "has_prev": pag.has_prev,
    })


# ===========================================
# API — Materias primas
# ===========================================

@apiRecetas.route("/materias-primas", methods=["GET"])
@login_requerido
@permiso_requerido("recetas", "crear")
def api_materias_primas():
    materias = MateriaPrima.query.filter_by(activo=True).order_by(MateriaPrima.nombre).all()

    return jsonify({
        "data": [
            {
                "id":     mp.id,
                "nombre": mp.nombre,
                "unidad": mp.unidad.sigla if mp.unidad else "—",
                "merma":  float(mp.porcentaje_merma or 0),
            }
            for mp in materias
        ]
    })


# ===========================================
# API — Detalle de una receta (para editar)
# ===========================================

@apiRecetas.route("/<id>", methods=["GET"])
@decrypt_url_id()
@permiso_requerido("recetas", "ver")
def api_detalle(id):
    receta = Receta.query.get_or_404(id)
    v = receta.producto_variante

    return jsonify({
        "id":            receta.id,
        "cantidad_base": receta.cantidad_base,
        "variante": {
            "id":       v.id,
            "producto": v.producto.nombre,
            "talla":    v.talla.nombre,
            "color":    v.producto.color.nombre if v.producto.color else None,
            "color_hex": v.producto.color.hex   if v.producto.color else None,
        },
        "detalles": [
            {
                "materia_prima_id": d.materia_prima_id,
                "nombre":           d.materia_prima.nombre,
                "cantidad_neta":    float(d.cantidad_neta),
                "unidad":           d.materia_prima.unidad.sigla if d.materia_prima.unidad else "—",
                "merma":            float(d.materia_prima.porcentaje_merma or 0),
            }
            for d in receta.detalles
        ],
    })

@recetas.route("/eliminar/<id>")
@decrypt_url_id()
@login_requerido
@permiso_requerido("recetas", "eliminar")
def eliminar(id):

    receta = Receta.query.filter_by(id=id, activo=True).first_or_404()

    receta.activo = False
    receta.fecha_eliminacion = datetime.datetime.utcnow()
    receta.eliminado_por = g.usuario_actual.id

    db.session.commit()

    flash("Receta eliminada correctamente", "success")
    return redirect(url_for("recetas.lista"))