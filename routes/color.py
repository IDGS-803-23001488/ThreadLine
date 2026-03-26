import datetime 
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from database.mysql import db, Color 
from forms import ColorForm
from securrity.middlerware import login_requerido, permiso_requerido, decrypt_url_id

color = Blueprint("color", __name__, url_prefix = "/color")

#===========================================
#Lista 
#===========================================

@color.route("/")
@login_requerido
@permiso_requerido("color","ver")
def lista ():
    search = request.args.get("search", "", type=str)
    page = request.args.get("page",1, type=int)
    per_page = request.args.get("per_page",5,type=int)
    
    query = Color.query.filter_by(activo=True)
    
    if search:
        query = query.filter_by(activo=True)
        
        if search :
            query = query.filtrer(
                Color.nombre.ilike(f"%{search}%") |
                Color.hex.ilike(f"%{search}%")
            )
        
    pagination = query.order_by(Color.id.asc()).paginate(
        page = page,
        per_page= per_page,
        error_out = False
    )
    
    rows = [
        [("ID", c.id),("Nombre", c.nombre),("Codigo Hex",c.hex)]
        for c in pagination.items
    ]
    
    return render_template(
        "color/lista.html",
        headers=["ID","Nombre","Codigo Hex"],
        rows = rows,
        pagination = pagination,
        search = search,
        per_page = per_page,
        endpoint = "color",
        titulo = "Colores",
        descripcion = "Listado general de colores"
    )

# ==============================
# CREAR
# ==============================
@color.route("/crear", methods=["GET", "POST"])
@login_requerido
@permiso_requerido("color", "crear")
def crear():
    form = ColorForm(request.form)
    
    if request.method == "POST" and form.validate():
        
        nuevo = Color(
            nombre=form.nombre.data,
            hex=form.hex.data,
            creado_por=g.usuario_actual.id
        )
        
        db.session.add(nuevo)
        db.session.commit()
        
        flash("Color creado correctamente")
        return redirect(url_for("color.lista"))
    
    return render_template(
        "color/crear.html",
        form=form,
        titulo="Crear Color",
        descripcion="Registro de nuevo color"
    )

# ==============================
# EDITAR
# ==============================
@color.route("/editar/<id>", methods=["GET", "POST"])
@decrypt_url_id()
@login_requerido
@permiso_requerido("color", "editar")
def editar(id):
    color_obj = Color.query.filter_by(id=id, activo=True).first_or_404()
    
    form = ColorForm(request.form, obj=color_obj)
    
    if request.method == "POST" and form.validate():
        
        form.populate_obj(color_obj)
        
        color_obj.editado_por = g.usuario_actual.id
        color_obj.fecha_edicion = datetime.datetime.utcnow()
        
        db.session.commit()
        
        flash("Color actualizado correctamente")
        return redirect(url_for("color.lista"))
    
    return render_template(
        "color/editar.html",
        form=form,
        titulo="Editar Color",
        descripcion="Modificar información del color"
    )

# ==============================
# ELIMINAR (SOFT DELETE)
# ==============================
@color.route("/eliminar/<id>")
@decrypt_url_id()
@login_requerido
@permiso_requerido("color", "eliminar")
def eliminar(id):
    color_obj = Color.query.filter_by(id=id, activo=True).first_or_404()
    
    color_obj.activo = False
    color_obj.fecha_eliminacion = datetime.datetime.utcnow()
    color_obj.eliminado_por = g.usuario_actual.id
    
    db.session.commit()
    
    flash("Color eliminado correctamente")
    return redirect(url_for("color.lista"))