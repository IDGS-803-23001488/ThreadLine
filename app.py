# app.py
from flask import Flask, render_template, g, session, redirect, url_for, request
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from database.mysql import db, Usuario, Rol, Permiso, Token
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
from routes.color import color
from routes.proveedores import proveedor
from utils.security import hash_password
from routes.categoria import categoria
from routes.inventario import inventario
from routes.talla import talla
from routes.cliente import cliente
from routes.recetas import recetas
from routes.productosVariantes import productosVariantes

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
app.register_blueprint(color)
app.register_blueprint(proveedor)
app.register_blueprint(categoria)
app.register_blueprint(inventario)
app.register_blueprint(talla)
app.register_blueprint(cliente)
app.register_blueprint(recetas)
app.register_blueprint(productosVariantes)

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
            "productosVariantes": ["buscador"],
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
    app.run(debug=True)
