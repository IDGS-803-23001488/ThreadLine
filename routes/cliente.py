
import datetime 
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from database.mysql import db, Cliente, Usuario, Rol
from forms import ClienteForm
from middlerware import login_requerido, permiso_requerido, decrypt_url_id
from utils.security import hash_password


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
    
    query = db.session.query(Cliente).join(
        Usuario, Cliente.usuario_id == Usuario.id
    ).filter(Cliente.activo == True)
        
    if search:
        query = query.filter(
            Cliente.nombre.ilike(f"%{search}%") |
            Usuario.correo.ilike(f"%{search}%") |
            Cliente.telefono.ilike(f"%{search}%")
        )
    
    pagination = query.order_by(Cliente.id.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    rows = [
        [
            
            ("ID", c.id), ("Nombre", c.nombre), ("Correo", c.usuario.correo if c.usuario else "Sin usuario"), ("Teléfono", c.telefono), ("Direcion", c.direccion)]
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
        
        existente = Usuario.query.filter_by(correo = form.correo.data).first()
        
        if existente :
            flash("El correo ya existe","correo")
            return render_template("cliente/crear.html",form=form)
        
        rol_cliente = Rol.query.filter_by(nombre = "cliente").first()
        if not rol_cliente:
            rol_cliente = Rol(
                nombre = "cliente",
                descripcion = "Rol de clientes",
                activo = True,
                creado_por=g.usuario_actual.id
            )
            db.session.add(rol_cliente)
            db.session.flush()
            
        nuevo_usuario = Usuario(
            usuario = form.correo.data,
            correo = form.correo.data,
            contrasenia=hash_password(form.contrasenia.data),
            creado_por=g.usuario_actual.id,
        )
        
        nuevo_usuario.roles.append(rol_cliente)
        
        db.session.add(nuevo_usuario)
        db.session.flush()
        
        nuevo = Cliente(
            nombre=form.nombre.data,
            telefono=form.telefono.data,
            direccion= form.direccion.data,
            usuario_id = nuevo_usuario.id,
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
    usuario = color_obj.usuario
    form = ClienteForm(request.form, obj=color_obj)
    
    if request.method == "POST" and form.validate():
        existente = Usuario.query.filter_by(correo = form.correo.data).first()
        
        if existente :
            flash("El correo ya existe","correo")
            return render_template("cliente/crear.html",form=form)
        
        color_obj.nombre = form.nombre.data
        usuario.correo = form.correo.data
        color_obj.telefono = form.telefono.data
        color_obj.direccion = form.direccion.data

        if form.cambiar_contrasenia.data and form.contrasenia.data:
            color_obj.contrasenia = hash_password(form.contrasenia.data)
        
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