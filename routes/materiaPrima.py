
import datetime 
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, current_app
from database.mysql import db, MateriaPrima, Unidad, Empaque, Proveedor, Articulo
from forms import MateriaPrimaForm
from securrity.middlerware import login_requerido, permiso_requerido, decrypt_url_id
from werkzeug.utils import secure_filename
import os
import uuid

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
            ("Foto", c.ruta_imagen),
            ("Unidad", Unidad.query.get(c.unidad_id).unidad if c.unidad_id else ""),
            ("Empaque", Empaque.query.get(c.empaque_id).paquete if c.empaque_id else ""),
            ("Proveedor", Proveedor.query.get(c.proveedor_id).nombre if c.proveedor_id else ""),
            ("Stock Minimo", c.stock_minimo),
            ("Stock Maximo", c.stock_maximo)
        ]
        for c in pagination.items
    ]
    
    return render_template(
        "materiaPrima/lista.html",
        headers=["ID","Nombre","Foto","Unidad","Empaque","Proveedor","Stock Minimo","Stock Maximo"],
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
        
        if form.stock_minimo.data > form.stock_maximo.data:
            flash("El stock mínimo no puede ser mayor al máximo", "error")
            return render_template("materiaPrima/crear.html", form=form)
        
        if not request.files.get('imagen'):
            flash("Porfavor agrege una imagen del insumo a agregar", "error")
            return render_template("materiaPrima/crear.html", form=form)
            
        try: 
            articulo_mp = Articulo(
                tipo='MATERIA_PRIMA',
                creado_por=g.usuario_actual.id
            )

            db.session.add(articulo_mp)
            db.session.commit()

            file = request.files.get('imagen')
            filename = str(uuid.uuid4()) + "_" + secure_filename(file.filename)
            ruta_bd = f"uploads/{filename}"
            ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(ruta)

            nuevo = MateriaPrima(
                articulo_id=Articulo.query.count(),
                nombre=form.nombre.data,
                unidad_id=form.unidad_id.data,
                empaque_id=form.empaque_id.data,
                proveedor_id=form.proveedor_id.data,
                ruta_imagen = ruta_bd,
                stock_minimo=form.stock_minimo.data,
                stock_maximo=form.stock_maximo.data,
                creado_por=g.usuario_actual.id
            )
        
            db.session.add(nuevo)
            db.session.commit()
        
            flash("Materia prima creada correctamente")
            return redirect(url_for("materia_prima.lista"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear: {str(e)}","error")
            return render_template("materiaPrima/crear.html", form=form, titulo="Crear Materia Prima",
                descripcion="Registro de nuevo Materia Prima")
            
    return render_template(
        "materiaPrima/crear.html",
        form=form,
        titulo="Crear Materia Prima",
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
    ruta_imagen = color_obj.ruta_imagen
    form.unidad_id.choices = [(u.id, u.unidad) for u in Unidad.query.all()]
    form.empaque_id.choices = [(e.id, e.paquete) for e in Empaque.query.all()]
    form.proveedor_id.choices = [(p.id, p.nombre) for p in Proveedor.query.all()]

    if request.method == "POST" and form.validate():
        
        try:
            
            if form.stock_minimo.data > form.stock_maximo.data:
                flash("El stock mínimo no puede ser mayor al máximo", "error")
                return render_template("materiaPrima/editar.html", form=form, titulo="Editar MateriaPrima", 
                                   descripcion="Modificar información", imagen=ruta_imagen)
           
            form.populate_obj(color_obj)

            if request.files.get('imagen'):
                file = request.files.get('imagen')
                filename = str(uuid.uuid4()) + "_" + secure_filename(file.filename)
                ruta_bd = f"uploads/{filename}"
                ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(ruta)
                color_obj.ruta_imagen = ruta_bd

            color_obj.editado_por = g.usuario_actual.id
            color_obj.fecha_edicion = datetime.datetime.utcnow()
            
            db.session.commit()
            
            flash("MateriaPrima actualizado correctamente")
            return redirect(url_for("materia_prima.lista"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar: {str(e)}","error")
            return render_template("materiaPrima/editar.html", form=form, titulo="Editar MateriaPrima", 
                                   descripcion="Modificar información", imagen=ruta_imagen)
    
    return render_template(
        "materiaPrima/editar.html",
        form=form,
        titulo="Editar MateriaPrima",
        descripcion="Modificar información del Materia Prima", 
        imagen=ruta_imagen
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