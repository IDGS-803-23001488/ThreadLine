
import datetime 
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from database.mysql import db, Categoria 
from forms import CategoriaForm
from middlerware import login_requerido, permiso_requerido, decrypt_url_id

categoria = Blueprint("categoria", __name__, url_prefix = "/categoria")

#===========================================
#Lista 
#===========================================

@categoria.route("/")
@login_requerido
@permiso_requerido("categoria","ver")
def lista ():
    search = request.args.get("search", "", type=str)
    page = request.args.get("page",1, type=int)
    per_page = request.args.get("per_page",5,type=int)
    
    query = Categoria.query.filter_by(activo=True)
    
    if search:
        query = query.filter_by(activo=True)
        
        if search :
            query = query.filtrer(
                Categoria.nombre.ilike(f"%{search}%") |
                Categoria.descripcion.ilike(f"%{search}%")
            )
        
    pagination = query.order_by(Categoria.id.asc()).paginate(
        page = page,
        per_page= per_page,
        error_out = False
    )
    
    rows = [
        [("ID", c.id),("Nombre", c.nombre),("Descripcion",c.descripcion)]
        for c in pagination.items
    ]
    
    return render_template(
        "categoria/lista.html",
        headers=["ID","Nombre","Descripcion"],
        rows = rows,
        pagination = pagination,
        search = search,
        per_page = per_page,
        endpoint = "categoria",
        titulo = "Categorias",
        descripcion = "Listado general de colores"
    )

# ==============================
# CREAR
# ==============================
@categoria.route("/crear", methods=["GET", "POST"])
@login_requerido
@permiso_requerido("categoria", "crear")
def crear():
    form = CategoriaForm(request.form)
    
    if request.method == "POST" and form.validate():
        
        nuevo = Categoria(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            creado_por=g.usuario_actual.id
        )
        
        db.session.add(nuevo)
        db.session.commit()
        
        flash("Categoria creado correctamente")
        return redirect(url_for("categoria.lista"))
    
    return render_template(
        "categoria/crear.html",
        form=form,
        titulo="Crear Categoria",
        descripcion="Registro de nuevo categoria"
    )

# ==============================
# EDITAR
# ==============================
@categoria.route("/editar/<id>", methods=["GET", "POST"])
@decrypt_url_id()
@login_requerido
@permiso_requerido("categoria", "editar")
def editar(id):
    color_obj = Categoria.query.filter_by(id=id, activo=True).first_or_404()
    
    form = CategoriaForm(request.form, obj=color_obj)
    
    if request.method == "POST" and form.validate():
        
        form.populate_obj(color_obj)
        
        color_obj.editado_por = g.usuario_actual.id
        color_obj.fecha_edicion = datetime.datetime.utcnow()
        
        db.session.commit()
        
        flash("Categoria actualizado correctamente")
        return redirect(url_for("categoria.lista"))
    
    return render_template(
        "categoria/editar.html",
        form=form,
        titulo="Editar Categoria",
        descripcion="Modificar información del categoria"
    )

# ==============================
# ELIMINAR (SOFT DELETE)
# ==============================
@categoria.route("/eliminar/<id>")
@decrypt_url_id()
@login_requerido
@permiso_requerido("categoria", "eliminar")
def eliminar(id):
    color_obj = Categoria.query.filter_by(id=id, activo=True).first_or_404()
    
    color_obj.activo = False
    color_obj.fecha_eliminacion = datetime.datetime.utcnow()
    color_obj.eliminado_por = g.usuario_actual.id
    
    db.session.commit()
    
    flash("Categoria eliminado correctamente")
    return redirect(url_for("categoria.lista"))