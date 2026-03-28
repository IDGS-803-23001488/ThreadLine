# routes/ecomerce.py
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from database.mysql import db, Usuario, Rol, Producto, ProductoVariante
from forms import UserForm
from middlerware import login_requerido, permiso_requerido, decrypt_url_id
from utils.excel_export import exportar_excel
from sqlalchemy import func
ecomerce = Blueprint("ecomerce", __name__, url_prefix="/ecomerce")

# ==============================
# LISTA 
# ==============================

@ecomerce.route("/")
@login_requerido
@permiso_requerido("ecomerce", "ver")
def lista():

    # 🔥 Productos populares (puedes cambiar lógica después)
    productos_populares = (
        db.session.query(
            Producto,
            func.min(ProductoVariante.precio_venta).label("precio_min")
        )
        .join(ProductoVariante, Producto.id == ProductoVariante.producto_id)
        .filter(
            Producto.activo.is_(True),
            ProductoVariante.activo.is_(True)
        )
        .group_by(Producto.id)
        .order_by(func.min(ProductoVariante.precio_venta))  # opcional
        .limit(4)
        .all()
    )

    # 🆕 Productos recientes
    productos_recientes = (
        db.session.query(
            Producto,
            func.min(ProductoVariante.precio_venta).label("precio_min")
        )
        .join(ProductoVariante, Producto.id == ProductoVariante.producto_id)
        .filter(
            Producto.activo.is_(True),
            ProductoVariante.activo.is_(True)
        )
        .group_by(Producto.id)
        .order_by(Producto.fecha_creacion.desc())
        .limit(4)
        .all()
    )

    return render_template(
        "ecomerce/index.html",
        productos_populares=productos_populares,
        productos_recientes=productos_recientes
    )

@ecomerce.route("/shop")
@login_requerido
@permiso_requerido("ecomerce", "ver")
def shop():
    return render_template("ecomerce/shop.html")


@ecomerce.route("/product")
@login_requerido
@permiso_requerido("ecomerce", "ver")
def product():
    return render_template("ecomerce/single-product-page.html")


@ecomerce.route("/cart")
@login_requerido
@permiso_requerido("ecomerce", "ver")
def cart():
    return render_template("ecomerce/cart.html")


@ecomerce.route("/checkout")
@login_requerido
@permiso_requerido("ecomerce", "ver")
def checkout():
    return render_template("ecomerce/checkout.html")
    

@ecomerce.route("/register")
@login_requerido
@permiso_requerido("ecomerce", "ver")
def register():
    return render_template("ecomerce/register.html")

@ecomerce.route("/404")
def error_404():
    return render_template("ecomerce/404.html")