
import datetime 
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from database.mysql import db, Inventario 
from forms import InventarioForm
from middlerware import login_requerido, permiso_requerido, decrypt_url_id

inventario = Blueprint("inventario", __name__, url_prefix = "/inventario")

#===========================================
#Lista 
#===========================================

@inventario.route("/")
@login_requerido
@permiso_requerido("inventario","ver")
def lista ():
    search = request.args.get("search", "", type=str)
    page = request.args.get("page",1, type=int)
    per_page = request.args.get("per_page",5,type=int)
    
    query = Inventario.query.filter_by(activo=True)
    
    if search:
        query = query.filter_by(activo=True)
        
        if search :
            query = query.filtrer(
                Inventario.nombre.ilike(f"%{search}%") 
            )
        
    pagination = query.order_by(Inventario.id.asc()).paginate(
        page = page,
        per_page= per_page,
        error_out = False
    )
    
    rows = [
        [("ID", c.id),("Nombre", c.nombre)]
        for c in pagination.items
    ]
    
    return render_template(
        "inventario/lista.html",
        headers=["ID","Nombre"],
        rows = rows,
        pagination = pagination,
        search = search,
        per_page = per_page,
        endpoint = "inventario",
        titulo = "Inventarios",
        descripcion = "Listado general de colores"
    )

# ==============================
# CREAR
# ==============================
@inventario.route("/crear", methods=["GET", "POST"])
@login_requerido
@permiso_requerido("inventario", "crear")
def crear():
    form = InventarioForm(request.form)
    
    if request.method == "POST" and form.validate():
        
        nuevo = Inventario(
            nombre=form.nombre.data,
            creado_por=g.usuario_actual.id
        )
        
        db.session.add(nuevo)
        db.session.commit()
        
        flash("Inventario creado correctamente")
        return redirect(url_for("inventario.lista"))
    
    return render_template(
        "inventario/crear.html",
        form=form,
        titulo="Crear Inventario",
        descripcion="Registro de nuevo inventario"
    )

# ==============================
# EDITAR
# ==============================
@inventario.route("/editar/<id>", methods=["GET", "POST"])
@decrypt_url_id()
@login_requerido
@permiso_requerido("inventario", "editar")
def editar(id):
    color_obj = Inventario.query.filter_by(id=id, activo=True).first_or_404()
    
    form = InventarioForm(request.form, obj=color_obj)
    
    if request.method == "POST" and form.validate():
        
        form.populate_obj(color_obj)
        
        color_obj.editado_por = g.usuario_actual.id
        color_obj.fecha_edicion = datetime.datetime.utcnow()
        
        db.session.commit()
        
        flash("Inventario actualizado correctamente")
        return redirect(url_for("inventario.lista"))
    
    return render_template(
        "inventario/editar.html",
        form=form,
        titulo="Editar Inventario",
        descripcion="Modificar información del inventario"
    )

# ==============================
# ELIMINAR (SOFT DELETE)
# ==============================
@inventario.route("/eliminar/<id>")
@decrypt_url_id()
@login_requerido
@permiso_requerido("inventario", "eliminar")
def eliminar(id):
    color_obj = Inventario.query.filter_by(id=id, activo=True).first_or_404()
    
    color_obj.activo = False
    color_obj.fecha_eliminacion = datetime.datetime.utcnow()
    color_obj.eliminado_por = g.usuario_actual.id
    
    db.session.commit()
    
    flash("Inventario eliminado correctamente")
    return redirect(url_for("inventario.lista"))