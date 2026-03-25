
import datetime 
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from database.mysql import db, Talla 
from forms import TallaForm
from middlerware import login_requerido, permiso_requerido, decrypt_url_id

talla = Blueprint("talla", __name__, url_prefix = "/talla")

#===========================================
#Lista 
#===========================================

@talla.route("/")
@login_requerido
@permiso_requerido("talla","ver")
def lista ():
    search = request.args.get("search", "", type=str)
    page = request.args.get("page",1, type=int)
    per_page = request.args.get("per_page",5,type=int)
    
    query = Talla.query.filter_by(activo=True)
    
    if search:
        query = query.filter_by(activo=True)
        
        if search :
            query = query.filtrer(
                Talla.nombre.ilike(f"%{search}%") |
                Talla.orden.ilike(f"%{search}%")
            )
        
    pagination = query.order_by(Talla.id.asc()).paginate(
        page = page,
        per_page= per_page,
        error_out = False
    )
    
    rows = [
        [("ID", c.id),("Nombre", c.nombre),("Descripcion",c.orden)]
        for c in pagination.items
    ]
    
    return render_template(
        "talla/lista.html",
        headers=["ID","Nombre","Orden"],
        rows = rows,
        pagination = pagination,
        search = search,
        per_page = per_page,
        endpoint = "talla",
        titulo = "Tallas",
        orden = "Listado general de colores"
    )

# ==============================
# CREAR
# ==============================
@talla.route("/crear", methods=["GET", "POST"])
@login_requerido
@permiso_requerido("talla", "crear")
def crear():
    form = TallaForm(request.form)
    
    if request.method == "POST" and form.validate():
        
        existente = Talla.query.filter_by(nombre = form.nombre.data).first()
        
        if existente :
            flash("La talla ya existe","talla")
            return render_template("talla/crear.html",form=form)
        
        nuevo = Talla(
            nombre=form.nombre.data,
            orden=form.orden.data,
            creado_por=g.usuario_actual.id
        )
        
        db.session.add(nuevo)
        db.session.commit()
        
        flash("Talla creado correctamente")
        return redirect(url_for("talla.lista"))
    
    return render_template(
        "talla/crear.html",
        form=form,
        titulo="Crear Talla",
        orden="Registro de nuevo talla"
    )

# ==============================
# EDITAR
# ==============================
@talla.route("/editar/<id>", methods=["GET", "POST"])
@decrypt_url_id()
@login_requerido
@permiso_requerido("talla", "editar")
def editar(id):
    color_obj = Talla.query.filter_by(id=id, activo=True).first_or_404()
    
    form = TallaForm(request.form, obj=color_obj)
    
    if request.method == "POST" and form.validate():
        
        form.populate_obj(color_obj)
        
        color_obj.editado_por = g.usuario_actual.id
        color_obj.fecha_edicion = datetime.datetime.utcnow()
        
        db.session.commit()
        
        flash("Talla actualizado correctamente")
        return redirect(url_for("talla.lista"))
    
    return render_template(
        "talla/editar.html",
        form=form,
        titulo="Editar Talla",
        orden="Modificar información del talla"
    )

# ==============================
# ELIMINAR (SOFT DELETE)
# ==============================
@talla.route("/eliminar/<id>")
@decrypt_url_id()
@login_requerido
@permiso_requerido("talla", "eliminar")
def eliminar(id):
    color_obj = Talla.query.filter_by(id=id, activo=True).first_or_404()
    
    color_obj.activo = False
    color_obj.fecha_eliminacion = datetime.datetime.utcnow()
    color_obj.eliminado_por = g.usuario_actual.id
    
    db.session.commit()
    
    flash("Talla eliminado correctamente")
    return redirect(url_for("talla.lista"))