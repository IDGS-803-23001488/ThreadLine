# routes/unidad.py
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from database.mysql import db, Unidad
from forms import UnidadForm
from securrity.middlerware import login_requerido, permiso_requerido, decrypt_url_id

unidad = Blueprint("unidad", __name__, url_prefix="/unidad")

# ==============================
# LISTA
# ==============================
@unidad.route("/")
@login_requerido
@permiso_requerido("unidad", "ver")
def lista():
    search = request.args.get("search", "", type=str)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    query = Unidad.query.filter_by(activo=True)
    if search:
        query = query.filter(
            Unidad.unidad.ilike(f"%{search}%") |
            Unidad.sigla.ilike(f"%{search}%")
        )

    pagination = query.order_by(Unidad.id.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    rows = [
        [("ID", u.id), ("Unidad", u.unidad), ("Sigla", u.sigla), ("Cantidad", u.cantidad)]
        for u in pagination.items
    ]

    return render_template(
        "unidad/lista.html",
        headers=["ID", "Unidad", "Sigla", "Cantidad"],
        rows=rows,
        pagination=pagination,
        search=search,
        per_page=per_page,
        endpoint="unidad",
        titulo="Unidades",
        descripcion="Listado general de unidades"
    )


# ==============================
# CREAR
# ==============================
@unidad.route("/crear", methods=["GET", "POST"])
@login_requerido
@permiso_requerido("unidad", "crear")
def crear():

    form = UnidadForm(request.form)

    if request.method == "POST" and form.validate():

        nuevo = Unidad(
            unidad=form.unidad.data,
            sigla=form.sigla.data,
            cantidad=form.cantidad.data,
            creado_por=g.usuario_actual.id  # 🔥 Auditoría
        )

        db.session.add(nuevo)
        db.session.commit()

        flash("Unidad creada correctamente")
        return redirect(url_for("unidad.lista"))

    return render_template(
        "unidad/crear.html",
        form=form,
        titulo="Crear Unidad",
        descripcion="Registro de nueva unidad"
    )


# ==============================
# EDITAR
# ==============================
@unidad.route("/editar/<id>", methods=["GET", "POST"])
@decrypt_url_id()
@login_requerido
@permiso_requerido("unidad", "editar")
def editar(id):

    unidad = Unidad.query.filter_by(id=id, activo=True).first_or_404()

    form = UnidadForm(request.form, obj=unidad)

    if request.method == "POST" and form.validate():

        form.populate_obj(unidad)

        unidad.editado_por = g.usuario_actual.id
        unidad.fecha_edicion = datetime.datetime.utcnow()

        db.session.commit()

        flash("Unidad actualizada correctamente")
        return redirect(url_for("unidad.lista"))

    return render_template(
        "unidad/editar.html",
        form=form,
        titulo="Editar Unidad",
        descripcion="Modificar información de la unidad"
    )


# ==============================
# ELIMINAR (SOFT DELETE)
# ==============================
@unidad.route("/eliminar/<id>")
@decrypt_url_id()
@login_requerido
@permiso_requerido("unidad", "eliminar")
def eliminar(id):

    unidad = Unidad.query.filter_by(id=id, activo=True).first_or_404()

    unidad.activo = False
    unidad.fecha_eliminacion = datetime.datetime.utcnow()
    unidad.eliminado_por = g.usuario_actual.id

    db.session.commit()

    flash("Unidad eliminada correctamente")
    return redirect(url_for("unidad.lista"))