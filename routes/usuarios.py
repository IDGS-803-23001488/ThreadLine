# routes/usuarios.py
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from database.mysql import db, Usuario, Rol
from forms import UserForm
from middlerware import login_requerido, permiso_requerido, decrypt_url_id
from utils.excel_export import exportar_excel

usuarios = Blueprint("usuarios", __name__, url_prefix="/usuarios")

# ==============================
# LISTA
# ==============================
@usuarios.route("/")
@login_requerido
@permiso_requerido("usuarios", "ver")
def lista():
    search = request.args.get("search", "", type=str)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    query = Usuario.query.filter_by(activo=True)
    if search:
        query = query.filter(
            Usuario.usuario.ilike(f"%{search}%") |
            Usuario.correo.ilike(f"%{search}%")
        )

    pagination = query.order_by(Usuario.id.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    rows = [
        [("ID", u.id), ("Usuario", u.usuario), ("Correo", u.correo)]
        for u in pagination.items
    ]

    return render_template(
        "usuarios/lista.html",
        headers=["ID", "Usuario", "Correo"],
        rows=rows,
        pagination=pagination,
        search=search,
        per_page=per_page,
        endpoint="usuarios",
        titulo="Usuarios",
        descripcion="Listado general de usuarios"
    )


# ==============================
# CREAR
# ==============================
@usuarios.route("/crear", methods=["GET", "POST"])
@login_requerido
@permiso_requerido("usuarios", "crear")
def crear():

    form = UserForm(request.form)    
    form.rol.choices = [(r.id, r.nombre) for r in Rol.query.order_by(Rol.nombre).all()]

    if request.method == "POST" and form.validate():

        nuevo = Usuario(
            usuario=form.usuario.data,
            correo=form.correo.data,
            contrasenia=form.contrasenia.data,
            creado_por=g.usuario_actual.id  # 🔥 Auditoría
        )
        rol = Rol.query.get(form.rol.data)
        nuevo.roles = [rol]
        
        db.session.add(nuevo)
        db.session.commit()

        flash("Usuario creado correctamente")
        return redirect(url_for("usuarios.lista"))

    return render_template(
        "usuarios/crear.html",
        form=form,
        titulo="Crear Usuario",
        descripcion="Registro de nuevo usuario"
    )


# ==============================
# EDITAR
# ==============================
@usuarios.route("/editar/<id>", methods=["GET", "POST"])
@decrypt_url_id()
@login_requerido
@permiso_requerido("usuarios", "editar")
def editar(id):

    usuario = Usuario.query.filter_by(id=id, activo=True).first_or_404()

    form = UserForm(request.form, obj=usuario)
    form.rol.choices = [(r.id, r.nombre) for r in Rol.query.order_by(Rol.nombre).all()]

    if request.method == "POST" and form.validate():

        usuario.usuario = form.usuario.data
        usuario.correo = form.correo.data

        if form.cambiar_contrasenia.data and form.contrasenia.data:
            usuario.contrasenia = hash_password(form.contrasenia.data)

        usuario.editado_por = g.usuario_actual.id
        usuario.fecha_edicion = datetime.datetime.utcnow()
        rol = Rol.query.get(form.rol.data)
        usuario.roles = [rol]

        db.session.commit()

        flash("Usuario actualizado correctamente")
        return redirect(url_for("usuarios.lista"))

    return render_template(
        "usuarios/editar.html",
        form=form,
        titulo="Editar Usuario",
        descripcion="Modificar información del usuario"
    )


# ==============================
# ELIMINAR (SOFT DELETE)
# ==============================
@usuarios.route("/eliminar/<id>")
@decrypt_url_id()
@login_requerido
@permiso_requerido("usuarios", "eliminar")
def eliminar(id):

    usuario = Usuario.query.filter_by(id=id, activo=True).first_or_404()

    usuario.activo = False
    usuario.fecha_eliminacion = datetime.datetime.utcnow()
    usuario.eliminado_por = g.usuario_actual.id

    db.session.commit()

    flash("Usuario eliminado correctamente")
    return redirect(url_for("usuarios.lista"))


# ==============================
# EXPORTAR EXCEL
# ==============================
@usuarios.route("/exportar")
@login_requerido
@permiso_requerido("usuarios", "ver")
def exportar():

    search = request.args.get("search", "", type=str)

    query = Usuario.query.filter_by(activo=True)

    if search:
        query = query.filter(
            Usuario.usuario.ilike(f"%{search}%") |
            Usuario.correo.ilike(f"%{search}%")
        )

    usuarios_list = query.order_by(Usuario.id.asc()).all()

    headers = ["ID", "Usuario", "Correo"]

    data = [
        [u.id, u.usuario, u.correo]
        for u in usuarios_list
    ]

    return exportar_excel(
        "usuarios",
        "Usuarios",
        headers,
        data
    )
