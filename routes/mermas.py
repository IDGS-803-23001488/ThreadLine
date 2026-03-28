# routes/mermas.py
from flask import Blueprint, render_template

mermas = Blueprint("mermas", __name__, url_prefix="/mermas")

@mermas.route("/")
def lista():
    return render_template(
        "mermas/lista.html",
        titulo="Administración de Mermas",
        descripcion="Gestión de mermas en el sistema",
    )