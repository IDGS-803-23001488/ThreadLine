# routes/productosVariantes.py
import datetime 
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify
from database.mysql import db, Producto, ProductoVariante
from securrity.middlerware import login_requerido, permiso_requerido
from sqlalchemy import or_

productosVariantes = Blueprint(
    "productosVariantes",
    __name__,
    url_prefix="/productosVariantes"
)

apiProductosVariantes = Blueprint(
    "api_productosVariantes",
    __name__,
    url_prefix="/api/productosVariantes"
)

#===========================================
# Buscador
#===========================================
@productosVariantes.route("/buscador")
@login_requerido
@permiso_requerido("productosVariantes", "buscador")
def buscador():
    search = request.args.get("search", "", type=str)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    # Base query
    query = ProductoVariante.query.join(Producto).filter(Producto.activo == True)

    # Filtro de búsqueda
    if search:
        query = query.filter(
            or_(
                Producto.nombre.ilike(f"%{search}%"),
                Producto.descripcion.ilike(f"%{search}%")
            )
        )

    # Paginación
    pagination = query.order_by(Producto.nombre.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    # Formato para tabla
    rows = [
        [
            ("ID", p.id),
            ("Producto", p.producto.nombre),
            ("Talla", p.talla.nombre),
            ("Color", p.color.nombre),
            ("Precio", p.precio_venta)
        ]
        for p in pagination.items
    ]

    return render_template(
        "productosVariantes/buscador.html",
        headers=["ID", "Producto", "Talla", "Color", "Precio"],
        rows=rows,
        pagination=pagination,
        search=search,
        per_page=per_page,
        endpoint="productos",
        return_url=request.args.get("return_url"),
        titulo="Buscador de Productos",
        descripcion="Busca productos por nombre o descripción"
    )

@productosVariantes.route("/seleccionar/<int:id>")
@login_requerido
def seleccionar(id):
    return_url = request.args.get("return_url")

    return redirect(f"{return_url}?producto_variante_id={id}")

@apiProductosVariantes.route("/productos", methods=["GET"])
@login_requerido
@permiso_requerido("productosVariantes", "buscador")
def obtener_productos():
    return jsonify({"data": []})
