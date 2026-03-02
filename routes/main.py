# routes/main.py
from flask import Blueprint, render_template

main = Blueprint("main", __name__)

@main.route("/")
@main.route("/index")
def index():
    return render_template(
        "index.html",
        titulo="Dashboard Principal",
        descripcion="Resumen general del sistema"
    )