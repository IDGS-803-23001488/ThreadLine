
import datetime 
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from database.mysql import db, Cliente 
from forms import ClienteForm
from middlerware import login_requerido, permiso_requerido, decrypt_url_id


cliente = Blueprint("cliente", __name__, url_prefix = "/cliente")

#===========================================
#Lista 
#===========================================

@cliente.route("/")
@login_requerido
@permiso_requerido("cliente", "ver")
def lista():
    search = request.args.get("search", "", type=str)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)
    
    query = Cliente.query.filter_by(activo=True)
    
    if search:
        query = query.filter(
            Cliente.nombre.ilike(f"%{search}%") |
            Cliente.correo.ilike(f"%{search}%") |
            Cliente.telefono.ilike(f"%{search}%")
        )
    
    pagination = query.order_by(Cliente.id.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    rows = [
        [("ID", c.id), ("Nombre", c.nombre), ("Correo", c.correo), ("Teléfono", c.telefono), ("Direcion", c.direccion)]
        for c in pagination.items
    ]
    
    return render_template(
        "cliente/lista.html",
        headers=["ID", "Nombre", "Correo", "Teléfono","Direcion"],
        rows=rows,
        pagination=pagination,
        search=search,
        per_page=per_page,
        endpoint="cliente",
        titulo="Clientes",
        telefono="Listado general de clientes"
    )

# ==============================
# CREAR
# ==============================
@cliente.route("/crear", methods=["GET", "POST"])
@login_requerido
@permiso_requerido("cliente", "crear")
def crear():
    form = ClienteForm(request.form)
    
    if request.method == "POST" and form.validate():
        
        existente = Cliente.query.filter_by(correo = form.correo.data).first()
        
        if existente :
            flash("El correo ya existe","correo")
            return render_template("cliente/crear.html",form=form)
        
        nuevo = Cliente(
            nombre=form.nombre.data,
            correo = form.correo.data,
            contrasenia = form.contrasenia,
            telefono=form.telefono.data,
            direccion= form.direccion.data,
            creado_por=g.usuario_actual.id
        )
        
        db.session.add(nuevo)
        db.session.commit()
        
        flash("Cliente creado correctamente")
        return redirect(url_for("cliente.lista"))
    
    return render_template(
        "cliente/crear.html",
        form=form,
        titulo="Crear Cliente",
        telefono="Registro de nuevo cliente"
    )

# ==============================
# EDITAR
# ==============================
@cliente.route("/editar/<id>", methods=["GET", "POST"])
@decrypt_url_id()
@login_requerido
@permiso_requerido("cliente", "editar")
def editar(id):
    color_obj = Cliente.query.filter_by(id=id, activo=True).first_or_404()
    
    form = ClienteForm(request.form, obj=color_obj)
    
    if request.method == "POST" and form.validate():
        
        form.populate_obj(color_obj)
        
        color_obj.editado_por = g.usuario_actual.id
        color_obj.fecha_edicion = datetime.datetime.utcnow()
        
        db.session.commit()
        
        flash("Cliente actualizado correctamente")
        return redirect(url_for("cliente.lista"))
    
    return render_template(
        "cliente/editar.html",
        form=form,
        titulo="Editar Cliente",
        telefono="Modificar información del cliente"
    )

# ==============================
# ELIMINAR (SOFT DELETE)
# ==============================
@cliente.route("/eliminar/<id>")
@decrypt_url_id()
@login_requerido
@permiso_requerido("cliente", "eliminar")
def eliminar(id):
    color_obj = Cliente.query.filter_by(id=id, activo=True).first_or_404()
    
    color_obj.activo = False
    color_obj.fecha_eliminacion = datetime.datetime.utcnow()
    color_obj.eliminado_por = g.usuario_actual.id
    
    db.session.commit()
    
    flash("Cliente eliminado correctamente")
    return redirect(url_for("cliente.lista"))