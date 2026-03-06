# app.py
from flask import Flask, render_template, g, session, redirect, url_for, request
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from database.mysql import db, Token
from config import DevelopmentConfig
# from database.mongo import ConexionMongo
from utils.crypto_url import encrypt_id

# Blueprints
from routes.main import main
from routes.usuarios import usuarios
from routes.auth import auth
from routes.roles import roles
from routes.unidad import unidad
from routes.empaque import empaque

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

csrf = CSRFProtect(app)
db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(main)
app.register_blueprint(usuarios)
app.register_blueprint(auth)
app.register_blueprint(roles)
app.register_blueprint(unidad)
app.register_blueprint(empaque)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html", error=e.description), 403

@app.before_request
def verificar_token():

    rutas_libres = ["auth.login", "static"]

    if request.endpoint in rutas_libres:
        return

    token_cookie = request.cookies.get("auth_token")

    if not token_cookie:
        return redirect(url_for("auth.login"))

    token_db = Token.query.filter_by(token=token_cookie, usado=False).first()

    if not token_db or token_db.esta_expirado():
        return redirect(url_for("auth.login"))

    g.usuario_actual = token_db.usuario

# @app.after_request
def registrar_log(response):

    rutas_libres = ["auth.login", "static"]

    if request.endpoint not in rutas_libres: # Temporal

        try:
            usuario = None
            datos_enviados = None

            if hasattr(g, "usuario_actual"):
                usuario = g.usuario_actual.usuario

            if request.method == "POST":
                if request.is_json:
                    datos_enviados = request.get_json()
                else:
                    datos_enviados = request.form.to_dict()

            ConexionMongo.guardar_log(
                usuario=usuario,
                endpoint=request.endpoint,
                ip=request.remote_addr,
                estado=response.status_code,
                metodo=request.method,
                url=request.url,
                datos=datos_enviados
            )

        except Exception as e:
            print("Error guardando log:", e)

    return response

@app.template_filter('encrypt')
def encrypt_filter(value):
    return encrypt_id(value)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
