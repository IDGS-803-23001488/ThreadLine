# app.py
import datetime
from flask import Flask, render_template, g, session, redirect, url_for, request
from flask_migrate import Migrate
from database.mysql import db, Usuario, Rol, Permiso, Token
from config import DevelopmentConfig
from utils.crypto_url import encrypt_id
from extensions import mail, csrf
# from database.mongo import ConexionMongo

# Blueprints
from routes.main import main
from routes.usuarios import usuarios
from routes.auth import auth
from routes.roles import roles
from routes.unidad import unidad
from routes.empaque import empaque
from routes.eccomerce.ecomerce import ecomerce
from routes.color import color
from routes.proveedores import proveedor
from utils.security import hash_password
from routes.categoria import categoria
from routes.inventario import inventario
from routes.talla import talla
from routes.cliente import cliente
from routes.recetas import recetas, apiRecetas
from routes.productosVariantes import productosVariantes , apiProductosVariantes
from routes.materiaPrima import materia_prima
from routes.explosion_materiales.explosion import explosion
from routes.explosion_materiales.api_explosion import apiExplosion
from routes.mermas import mermas

import os

UPLOAD_FOLDER = 'static/uploads'

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['WTF_CSRF_HEADERS'] = ['X-CSRFToken', 'X-CSRF-Token']


mail.init_app(app)
csrf.init_app(app)
db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(main)
app.register_blueprint(usuarios)
app.register_blueprint(auth)
app.register_blueprint(roles)
app.register_blueprint(unidad)
app.register_blueprint(empaque)
app.register_blueprint(ecomerce)
app.register_blueprint(color)
app.register_blueprint(proveedor)
app.register_blueprint(categoria)
app.register_blueprint(inventario)
app.register_blueprint(talla)
app.register_blueprint(cliente)
app.register_blueprint(recetas)
app.register_blueprint(apiRecetas)
app.register_blueprint(productosVariantes)
app.register_blueprint(apiProductosVariantes)
app.register_blueprint(materia_prima)
app.register_blueprint(explosion)
app.register_blueprint(apiExplosion)
app.register_blueprint(mermas)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(403)
def forbidden(e):
    if request.path.startswith("/api"):
        return {"error": "Forbidden", "detalle": e.description}, 403
    return render_template("403.html", error=e.description), 403

@app.before_request
def verificar_token():
    usuario = None
    cliente = None
    rol_actual = None
    rutas_libres = [
        "auth.login",
        "auth.verificar_2fa",
        "auth.modal_user",
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
        tipo="login_usuario",
        usado=False
    ).first()
    
    if not token_db :
        token_db = Token.query.filter_by(
            token=token_cookie,
            tipo="login_cliente",
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

        if request.path.startswith("/api"):
            return {"error": "Sesión expirada"}, 401
        
        resp = redirect(url_for("auth.login"))
        resp.set_cookie("auth_token", "", expires=0)

        return resp

    # 🔒 Usuario bloqueado
    if token_db.tipo == "login_usuario":
        usuario = token_db.usuario
        if usuario and usuario.bloqueado:
            token_db.usado = True
            db.session.commit()
            
            if request.path.startswith("/api"):
                return {"error": "Usuario bloqueado"}, 403
            resp = redirect(url_for("auth.login"))
            resp.set_cookie("auth_token", "", expires=0)
            return resp
    elif token_db.tipo == "login_cliente":
        cliente = token_db.cliente
        rol_actual = "cliente"
        if not cliente.activo:
            token_db.usado = True
            db.session.commit()

            resp = redirect(url_for("auth.login"))
            resp.set_cookie("auth_token", "", expires=0)

            if request.path.startswith("/api"):
                return {"error": "Cliente inactivo"}, 403

            return resp

    else:
        return redirect(url_for("auth.login"))

    # ✅ Usuario válido
    g.usuario_actual = usuario
    g.cliente_actual = cliente
    g.token_actual = token_db
    g.rol_actual = rol_actual

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

def seed_data():
    from sqlalchemy.exc import IntegrityError

    try:
        # =========================================
        # PERMISOS (DINÁMICO)
        # =========================================
        PERMISOS = {
            "usuarios": ["ver", "crear", "editar", "eliminar", "exportar"],
            "roles": ["ver", "crear", "editar", "eliminar", "exportar"],
            "unidad": ["ver", "crear", "editar", "eliminar", "exportar"],
            "empaque": ["ver", "crear", "editar", "eliminar", "exportar"],
            "color": ["ver", "crear", "editar", "eliminar", "exportar"],
            "proveedor": ["ver", "crear", "editar", "eliminar", "exportar"],
            "categoria": ["ver", "crear", "editar", "eliminar", "exportar"],
            "inventario": ["ver", "crear", "editar", "eliminar", "exportar"],
            "talla": ["ver", "crear", "editar", "eliminar", "exportar"],
            "cliente": ["ver", "crear", "editar", "eliminar", "exportar"],
            "recetas": ["ver", "crear", "editar", "eliminar", "exportar"],
            "materia_prima": ["ver", "crear", "editar", "eliminar", "exportar"],
            "explosion": ["ver", "crear"],    
            "productosVariantes": ["ver","crear", "editar", "eliminar"],
            "ecomerce": ["ver","crear", "editar", "eliminar"],
            "mermas": ["ver","crear", "editar", "eliminar"]

        }

        permisos_db = []

        for modulo, acciones in PERMISOS.items():
            for accion in acciones:
                permiso = Permiso.query.filter_by(
                    modulo=modulo, accion=accion
                ).first()

                if not permiso:
                    permiso = Permiso(modulo=modulo, accion=accion)
                    db.session.add(permiso)

                permisos_db.append(permiso)

        db.session.flush()

        # =========================================
        # ROL ADMIN
        # =========================================
        admin_role = Rol.query.filter_by(nombre="Administrador").first()

        if not admin_role:
            admin_role = Rol(
                nombre="Administrador",
                descripcion="Rol con todos los permisos del sistema"
            )
            db.session.add(admin_role)
            db.session.flush()

        # =========================================
        # ASIGNAR PERMISOS AL ADMIN
        # =========================================
        for permiso in permisos_db:
            if permiso not in admin_role.permisos:
                admin_role.permisos.append(permiso)

        # =========================================
        # USUARIO ADMIN
        # =========================================
        admin_user = Usuario.query.filter_by(usuario="admin").first()

        if not admin_user:
            admin_user = Usuario(
                usuario="admin",
                correo="admin@example.com",
                contrasenia=hash_password("admin123"),  # ⚠️ luego usa hash
                activo=True
            )
            db.session.add(admin_user)
            db.session.flush()

        # =========================================
        # ASIGNAR ROL AL USUARIO
        # =========================================
        if admin_role not in admin_user.roles:
            admin_user.roles.append(admin_role)

        # =========================================
        # COMMIT
        # =========================================
        db.session.commit()

    except IntegrityError:
        db.session.rollback()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True, host='0.0.0.0', port=8000)

