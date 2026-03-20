
import datetime 
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from database.mysql import db, Producto, ProductoVariante, Receta
from forms import RecetaForm
from middlerware import login_requerido, permiso_requerido, decrypt_url_id
from sqlalchemy import or_

recetas = Blueprint("recetas", __name__, url_prefix = "/recetas")

#===========================================
#Lista 
#===========================================
@recetas.route("/")
@login_requerido
@permiso_requerido("recetas", "ver")
def lista():
    search = request.args.get("search", "", type=str)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)
    
    query = Receta.query.filter(Receta.activo == True)
    query = query.join(Receta.producto_variante).join(ProductoVariante.producto)

    if search:
        query = query.filter(
            or_(
                Producto.nombre.ilike(f"%{search}%")
            )
        )

    pagination = query.order_by(Receta.id.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    rows = [
        [
            ("ID", r.id),
            ("Producto", r.producto_variante.producto.nombre),
            ("Talla", r.producto_variante.talla.nombre),
            ("Color", r.producto_variante.color.nombre),
            ("Cantidad Base", r.cantidad_base)
        ]
        for r in pagination.items
    ]
    
    return render_template(
        "recetas/lista.html",
        headers=["ID", "Producto", "Talla", "Color","Cantidad Base"],
        rows=rows,
        pagination=pagination,
        search=search,
        per_page=per_page,
        endpoint="recetas",
        titulo="Recetas",
        telefono="Listado general de recetas"
    )

@recetas.route("/crear", methods=["GET", "POST"])
@login_requerido
@permiso_requerido("recetas", "crear")
def crear():
    
    form = RecetaForm(request.form)
    
    return render_template(
        "recetas/crear.html",
        form=form,
        titulo="Crear Receta",
        descripcion="Registro de nueva receta"
    )