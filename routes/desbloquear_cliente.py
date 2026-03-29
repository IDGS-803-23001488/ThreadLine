# routes/clientes.py
import datetime
from re import U
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from database.mysql import Token, db, Cliente, Rol
from forms import ClienteForm
from middlerware import login_requerido, permiso_requerido, decrypt_url_id

desbloquear_cliente = Blueprint("desbloquear_cliente", __name__, url_prefix="/desbloquear_cliente")

# ==============================
# LISTA
# ==============================
@desbloquear_cliente.route("/")
@login_requerido
@permiso_requerido("desbloquear_cliente", "ver")
def lista():
    search = request.args.get("search", "", type=str)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    query = Cliente.query.filter_by(activo=False)
    if search:
        query = query.filter(
            Cliente.nombre.ilike(f"%{search}%") |
            Cliente.correo.ilike(f"%{search}%")
        )

    pagination = query.order_by(Cliente.id.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    rows = [
        [("ID", u.id), ("Nombre", u.nombre), ("Correo", u.correo)]
        for u in pagination.items
    ]

    return render_template(
        "desbloquear_cliente/lista.html",
        headers=["ID", "Cliente", "Correo"],
        rows=rows,
        pagination=pagination,
        search=search,
        per_page=per_page,
        endpoint="desbloquear_cliente",
        titulo="Desbloquear Cliente",
        descripcion="Listado general de Clientes"
    )



@desbloquear_cliente.route("/desbloquear/<id>", methods=["GET", "POST"])
@decrypt_url_id()
@login_requerido
@permiso_requerido("desbloquear_cliente", "desbloquear")
def desbloquear(id):
    
    cliente = Cliente.query.filter_by(id = id).first()
    if not cliente:
        flash("Cliente no encontrado", "error")
        return redirect(url_for("desbloquear_cliente.lista"))
    form = ClienteForm(request.form, obj=cliente)
    form.nombre.data = cliente.nombre
    form.correo.data = cliente.correo
    
    if request.method == "POST":
         
        Token.query.filter_by(id = id, tipo= "error_login", usado = False ).update({"usado":True})
        cliente.activo = True
        db.session.commit()
        flash("Cliente desbloqueado correctamente", "success")
        return redirect(url_for("desbloquear_cliente.lista"))
    
    return render_template(
        "desbloquear_cliente/desbloquear.html",
        form=form,
        titulo="Desbloquear Cliente",
        descripcion="Modificar información del cliente"
    )