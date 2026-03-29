# routes/usuarios.py
import datetime
from re import U
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from database.mysql import Token, db, Usuario, Rol
from forms import UserForm
from middlerware import login_requerido, permiso_requerido, decrypt_url_id
from utils.security import hash_password

desbloquear_usuario = Blueprint("desbloquear_usuario", __name__, url_prefix="/desbloquear_usuario")

# ==============================
# LISTA
# ==============================
@desbloquear_usuario.route("/")
@login_requerido
@permiso_requerido("desbloquear_usuario", "ver")
def lista():
    search = request.args.get("search", "", type=str)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    query = Usuario.query.filter_by(activo=False, bloqueado=True)
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
        "desbloquear_usuario/lista.html",
        headers=["ID", "Usuario", "Correo"],
        rows=rows,
        pagination=pagination,
        search=search,
        per_page=per_page,
        endpoint="desbloquear_usuario",
        titulo="Desbloquear Usuario",
        descripcion="Listado general de Usuarios"
    )



@desbloquear_usuario.route("/desbloquear/<id>", methods=["GET", "POST"])
@decrypt_url_id()
@login_requerido
@permiso_requerido("desbloquear_usuario", "desbloquear")
def desbloquear(id):
    
    usuario = Usuario.query.filter_by(id = id).first()
    if not usuario:
        flash("Usuario no encontrado", "error")
        return redirect(url_for("desbloquear_usuario.lista"))
    form = UserForm(request.form, obj=usuario)
    form.usuario.data = usuario.usuario
    form.correo.data = usuario.correo
    form.rol.data = [rol.nombre + " " for rol in usuario.roles]
    
    if request.method == "POST":
         
        Token.query.filter_by(id = id, tipo= "error_login", usado = False ).update({"usado":True})
        usuario.activo = True
        usuario.bloqueado = False
        db.session.commit()
        flash("Usuario desbloqueado correctamente", "success")
        return redirect(url_for("desbloquear_usuario.lista"))
    
    return render_template(
        "desbloquear_usuario/desbloquear.html",
        form=form,
        titulo="Desbloquear Usuario",
        descripcion="Modificar información del usuario"
    )