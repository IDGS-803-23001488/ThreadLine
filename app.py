# app.py
import datetime
from flask import Flask, g, redirect, url_for, request
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from database.mysql import db,Token
from securrity.config import DevelopmentConfig
from utils.crypto_url import encrypt_id
from extensions import mail
# from database.mongo import ConexionMongo

# Blueprints
from routes import register_blueprints
from database.seed import seed_data

UPLOAD_FOLDER = 'static/uploads'

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mail.init_app(app)
csrf = CSRFProtect(app)
db.init_app(app)
migrate = Migrate(app, db)
register_blueprints(app)

@app.before_request
def verificar_token():
    rutas_libres = [
        "auth.login",
        "auth.verificar_2fa",
        "static"
    ]

    if request.endpoint and any(request.endpoint.startswith(r) for r in rutas_libres):
        return

    token_cookie = request.cookies.get("auth_token")

    # 🔒 No autenticado
    if not token_cookie:
        if request.path.startswith("/api"):
            return {"error": "No autenticado"}, 401
        return redirect(url_for("auth.login"))

    token_db = Token.query.filter_by(
        token=token_cookie,
        tipo="login",
        usado=False
    ).first()

    # 🔒 Token inválido
    if not token_db:
        if request.path.startswith("/api"):
            return {"error": "Token inválido"}, 401
        return redirect(url_for("auth.login"))

    # 🔒 Token expirado
    if token_db.esta_expirado():
        token_db.usado = True
        db.session.commit()

        resp = redirect(url_for("auth.login"))
        resp.set_cookie("auth_token", "", expires=0)

        if request.path.startswith("/api"):
            return {"error": "Sesión expirada"}, 401

        return resp

    # 🔒 Usuario bloqueado
    if token_db.usuario.bloqueado:
        token_db.usado = True
        db.session.commit()

        resp = redirect(url_for("auth.login"))
        resp.set_cookie("auth_token", "", expires=0)

        if request.path.startswith("/api"):
            return {"error": "Usuario bloqueado"}, 403

        return resp

    # ✅ Usuario válido
    g.usuario_actual = token_db.usuario
    g.token_actual = token_db

    # 🔄 Renovación inteligente (solo si faltan <5 min)
    ahora = datetime.datetime.utcnow()

    if token_db.fecha_expiracion - ahora < datetime.timedelta(minutes=5):
        token_db.fecha_expiracion = ahora + datetime.timedelta(minutes=10)
        db.session.commit()

@app.context_processor
def inject_request():
    from flask import request
    return dict(request=request)

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
        seed_data()
    app.run(debug=True, host='0.0.0.0', port=8000)
