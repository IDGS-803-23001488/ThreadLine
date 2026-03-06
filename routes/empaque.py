# routes/empaque.py
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from database.mysql import db, Empaque, Unidad
from forms import EmpaqueForm
from middlerware import login_requerido, permiso_requerido, decrypt_url_id

empaque = Blueprint("empaque", __name__, url_prefix="/empaque")

# ==============================
# LISTA
# ==============================
@empaque.route("/")
@login_requerido
@permiso_requerido("empaque", "ver")
def lista():
    search = request.args.get("search", "", type=str)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    query = Empaque.query.filter_by(activo=True)
    if search:
        query = query.filter(
            Empaque.paquete.ilike(f"%{search}%") |
            Empaque.unidad.unidad.ilike(f"%{search}%")
        )

    pagination = query.order_by(Empaque.id.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    rows = [
        [("ID", u.id), ("Paquete", u.paquete), ("Unidad", u.unidad.sigla), ("Cantidad", u.cantidad)]
        for u in pagination.items
    ]

    return render_template(
        "empaque/lista.html",
        headers=["ID", "Paquete", "Unidad", "Cantidad"],
        rows=rows,
        pagination=pagination,
        search=search,
        per_page=per_page,
        endpoint="empaque",
        titulo="Empaques",
        descripcion="Listado general de empaques"
    )


# ==============================
# CREAR
# ==============================
@empaque.route("/crear", methods=["GET", "POST"])
@login_requerido
@permiso_requerido("empaque", "crear")
def crear():

    form = EmpaqueForm(request.form)
    unidades = Unidad.query.filter_by(activo=True)

    if request.method == "POST" and form.validate():

        nuevo = Empaque(
            paquete=form.paquete.data,
            unidad_id=form.unidad_id.data,
            cantidad=form.cantidad.data,
            creado_por=g.usuario_actual.id  # 🔥 Auditoría
        )

        db.session.add(nuevo)
        db.session.commit()

        flash("Empaque creado correctamente")
        return redirect(url_for("empaque.lista"))

    return render_template(
        "empaque/crear.html",
        form=form,
        unidades=unidades,
        titulo="Crear Empaque",
        descripcion="Registro de nuevo empaque"
    )


# ==============================
# EDITAR
# ==============================
@empaque.route("/editar/<id>", methods=["GET", "POST"])
@decrypt_url_id()
@login_requerido
@permiso_requerido("empaque", "editar")
def editar(id):

    empaque = Empaque.query.filter_by(id=id, activo=True).first_or_404()
    unidades = Unidad.query.filter_by(activo=True)

    form = EmpaqueForm(request.form, obj=empaque)

    if request.method == "POST" and form.validate():

        form.populate_obj(empaque)

        empaque.editado_por = g.usuario_actual.id
        empaque.fecha_edicion = datetime.datetime.utcnow()

        db.session.commit()

        flash("Empaque actualizado correctamente")
        return redirect(url_for("empaque.lista"))

    return render_template(
        "empaque/editar.html",
        form=form,
        unidades=unidades,
        titulo="Editar Empaque",
        descripcion="Modificar información del empaque"
    )


# ==============================
# ELIMINAR (SOFT DELETE)
# ==============================
@empaque.route("/eliminar/<id>")
@decrypt_url_id()
@login_requerido
@permiso_requerido("empaque", "eliminar")
def eliminar(id):

    empaque = Empaque.query.filter_by(id=id, activo=True).first_or_404()

    empaque.activo = False
    empaque.fecha_eliminacion = datetime.datetime.utcnow()
    empaque.eliminado_por = g.usuario_actual.id

    db.session.commit()

    flash("Empaque eliminado correctamente")
    return redirect(url_for("empaque.lista"))