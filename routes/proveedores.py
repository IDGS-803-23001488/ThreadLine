# routes/proveedores.py
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from database.mysql import db, Proveedor
from forms import ProveedorForm
from securrity.middlerware import login_requerido, permiso_requerido, decrypt_url_id

proveedor = Blueprint("proveedor", __name__, url_prefix="/proveedor")

# ==============================
# LISTA
# ==============================
@proveedor.route("/")
@login_requerido
@permiso_requerido("proveedor", "ver")
def lista():
    search = request.args.get("search", "", type=str)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    query = Proveedor.query.filter_by(activo=True)
    if search:
        query = query.filter(
            Proveedor.nombre.ilike(f"%{search}%") |
            Proveedor.rfc.ilike(f"%{search}%")
        )

    pagination = query.order_by(Proveedor.id.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    rows = [
        [("ID", u.id), ("Nombre", u.nombre), ("RFC", u.rfc), ("Correo", u.correo)]
        for u in pagination.items
    ]

    return render_template(
        "proveedores/lista.html",
        headers=["ID", "Nombre", "RFC", "Correo"],
        rows=rows,
        pagination=pagination,
        search=search,
        per_page=per_page,
        endpoint="proveedor",
        titulo="Proveedores",
        descripcion="Listado general de Proveedores"
    )


# ==============================
# CREAR
# ==============================
@proveedor.route("/crear", methods=["GET", "POST"])
@login_requerido
@permiso_requerido("proveedor", "crear")
def crear():

    form = ProveedorForm(request.form)

    if request.method == "POST" and form.validate():

        nuevo = Proveedor(
            nombre=form.nombre.data,
            rfc=form.rfc.data,
            correo=form.correo.data,
            creado_por=g.usuario_actual.id  # 🔥 Auditoría
        )

        db.session.add(nuevo)
        db.session.commit()

        flash("Proveedor creado correctamente")
        return redirect(url_for("proveedor.lista"))

    return render_template(
        "proveedores/crear.html",
        form=form,
        titulo="Crear Proveedor",
        descripcion="Registro de nuevo proveedor"
    )


# ==============================
# EDITAR
# ==============================
@proveedor.route("/editar/<id>", methods=["GET", "POST"])
@decrypt_url_id()
@login_requerido
@permiso_requerido("proveedor", "editar")
def editar(id):

    pro = Proveedor.query.filter_by(id=id, activo=True).first_or_404()

    form = ProveedorForm(request.form, obj=pro)

    if request.method == "POST" and form.validate():

        form.populate_obj(pro)

        pro.editado_por = g.usuario_actual.id
        pro.fecha_edicion = datetime.datetime.utcnow()

        db.session.commit()

        flash("Proveedor actualizado correctamente")
        return redirect(url_for("proveedor.lista"))

    return render_template(
        "proveedores/editar.html",
        form=form,
        titulo="Editar Proveedor",
        descripcion="Modificar información del proveedor"
    )


# ==============================
# ELIMINAR (SOFT DELETE)
# ==============================
@proveedor.route("/eliminar/<id>")
@decrypt_url_id()
@login_requerido
@permiso_requerido("proveedor", "eliminar")
def eliminar(id):

    pro = Proveedor.query.filter_by(id=id, activo=True).first_or_404()

    pro.activo = False
    pro.fecha_eliminacion = datetime.datetime.utcnow()
    pro.eliminado_por = g.usuario_actual.id

    db.session.commit()

    flash("Proveedor eliminado correctamente")
    return redirect(url_for("proveedor.lista"))