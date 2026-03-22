
import datetime 
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from database.mysql import db, MateriaPrima, Unidad, Empaque, Proveedor, Articulo
from forms import MateriaPrimaForm
from middlerware import login_requerido, permiso_requerido, decrypt_url_id

materia_prima = Blueprint("materia_prima", __name__, url_prefix = "/materia_prima")

#===========================================
#Lista 
#===========================================

@materia_prima.route("/")
@login_requerido
@permiso_requerido("materia_prima","ver")
def lista ():
    search = request.args.get("search", "", type=str)
    page = request.args.get("page",1, type=int)
    per_page = request.args.get("per_page",5,type=int)
    
    query = MateriaPrima.query.filter_by(activo=True)

    if search:
        query = query.filter_by(activo=True)
        
        if search :
            query = query.filter(
                MateriaPrima.nombre.ilike(f"%{search}%") |
                MateriaPrima.porcentaje_merma.ilike(f"%{search}%") |
                MateriaPrima.stock_minimo.ilike(f"%{search}%") |
                MateriaPrima.stock_maximo.ilike(f"%{search}%")
            )
        
    pagination = query.order_by(MateriaPrima.id.asc()).paginate(
        page = page,
        per_page= per_page,
        error_out = False
    )
    
    rows = [
        [
            ("ID", c.id),
            ("Nombre", c.nombre),
            ("Unidad", Unidad.query.get(c.unidad_id).unidad if c.unidad_id else ""),
            ("Empaque", Empaque.query.get(c.empaque_id).paquete if c.empaque_id else ""),
            ("Proveedor", Proveedor.query.get(c.proveedor_id).nombre if c.proveedor_id else ""),
            ("Porcentaje de merma", c.porcentaje_merma),
            ("Stock Minimo", c.stock_minimo),
            ("Stock Maximo", c.stock_maximo)
        ]
        for c in pagination.items
    ]
    
    return render_template(
        "materiaPrima/lista.html",
        headers=["ID","Nombre","Unidad","Empaque","Proveedor","Porcentaje de merma","Stock Minimo","Stock Maximo"],
        rows = rows,
        pagination = pagination,
        search = search,
        per_page = per_page,
        endpoint = "materia_prima",
        titulo = "Materia Primas",
        descripcion = "Listado general de colores"
    )

# ==============================
# CREAR
# ==============================
@materia_prima.route("/crear", methods=["GET", "POST"])
@login_requerido
@permiso_requerido("materia_prima", "crear")
def crear():
    form = MateriaPrimaForm(request.form)
    form.unidad_id.choices = [(u.id, u.unidad) for u in Unidad.query.all()]
    form.empaque_id.choices = [(e.id, e.paquete) for e in Empaque.query.all()]
    form.proveedor_id.choices = [(p.id, p.nombre) for p in Proveedor.query.all()]

    if request.method == "POST" and form.validate():
        
        articulo_mp = Articulo.query.filter_by(tipo="MATERIA_PRIMA").first()
        if articulo_mp is None:
            flash("No tienes articulos","articulos")
            return render_template("materiaPrima/crear.html",form=form,titulo="Crear MateriaPrima",
        descripcion="Registro de nuevo Materia Prima")
        
        if form.stock_minimo.data > form.stock_maximo.data:
            flash("El stock mínimo no puede ser mayor al máximo", "error")
            return render_template("materiaPrima/editar.html", form=form)
            
        try: 
            
            nuevo = MateriaPrima(
                articulo_id=articulo_mp.id,
                nombre=form.nombre.data,
                unidad_id=form.unidad_id.data,
                empaque_id=form.empaque_id.data,
                proveedor_id=form.proveedor_id.data,
                porcentaje_merma=form.porcentaje_merma.data,
                stock_minimo=form.stock_minimo.data,
                stock_maximo=form.stock_maximo.data,
                creado_por=g.usuario_actual.id
            )
        
            db.session.add(nuevo)
            db.session.commit()
        
            flash("MateriaPrima creado correctamente")
            return redirect(url_for("materia_prima.lista"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear: {str(e)}","error")
            return render_template("materiaPrima/crear.html", form=form, titulo="Crear MateriaPrima",
                descripcion="Registro de nuevo Materia Prima")
            
    return render_template(
        "materiaPrima/crear.html",
        form=form,
        titulo="Crear MateriaPrima",
        descripcion="Registro de nuevo Materia Prima"
    )

# ==============================
# EDITAR
# ==============================
@materia_prima.route("/editar/<id>", methods=["GET", "POST"])
@decrypt_url_id()
@login_requerido
@permiso_requerido("materia_prima", "editar")
def editar(id):
    color_obj = MateriaPrima.query.filter_by(id=id, activo=True).first_or_404()
    
    form = MateriaPrimaForm(request.form, obj=color_obj)
    form.unidad_id.choices = [(u.id, u.unidad) for u in Unidad.query.all()]
    form.empaque_id.choices = [(e.id, e.paquete) for e in Empaque.query.all()]
    form.proveedor_id.choices = [(p.id, p.nombre) for p in Proveedor.query.all()]

    if request.method == "POST" and form.validate():
        
        try:
            
            if form.stock_minimo.data > form.stock_maximo.data:
                flash("El stock mínimo no puede ser mayor al máximo", "error")
                return render_template("materiaPrima/editar.html", form=form)
           
            form.populate_obj(color_obj)
        
            color_obj.editado_por = g.usuario_actual.id
            color_obj.fecha_edicion = datetime.datetime.utcnow()
            
            db.session.commit()
            
            flash("MateriaPrima actualizado correctamente")
            return redirect(url_for("materia_prima.lista"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar: {str(e)}","error")
            return render_template("materiaPrima/editar.html", form=form, titulo="Editar MateriaPrima", descripcion="Modificar información")
    
    return render_template(
        "materiaPrima/editar.html",
        form=form,
        titulo="Editar MateriaPrima",
        descripcion="Modificar información del Materia Prima"
    )

# ==============================
# ELIMINAR (SOFT DELETE)
# ==============================
@materia_prima.route("/eliminar/<id>")
@decrypt_url_id()
@login_requerido
@permiso_requerido("materia_prima", "eliminar")
def eliminar(id):
    materia_obj = MateriaPrima.query.filter_by(id=id, activo=True).first_or_404()
    
    try:
        materia_obj.activo = False
        materia_obj.fecha_eliminacion = datetime.datetime.utcnow()
        materia_obj.eliminado_por = g.usuario_actual.id
        
        db.session.commit()
        
        flash("materia_prima eliminado correctamente")
        return redirect(url_for("materia_prima.lista"))
    
    except Exception as e:  
        db.session.rollback() 
        flash(f"Error al eliminar: {str(e)}", "error")
        return redirect(url_for("materia_prima.lista"))