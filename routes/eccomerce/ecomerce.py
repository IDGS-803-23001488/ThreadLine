# routes/ecomerce.py
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from database.mysql import db, Usuario, Rol
from forms import UserForm
from middlerware import login_requerido, permiso_requerido, decrypt_url_id
from utils.excel_export import exportar_excel

ecomerce = Blueprint("ecomerce", __name__, url_prefix="/ecomerce")

# ==============================
# LISTA 
# ==============================
@ecomerce.route("/")
@login_requerido
@permiso_requerido("ecomerce", "ver")
def lista():
    return render_template("ecomerce/index.html")


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