# middlerware.py
import datetime
from database.mysql import db
from flask import g, redirect, abort, url_for, request, jsonify
from functools import wraps
from functools import wraps
from flask import abort
from utils.crypto_url import decrypt_id

# ==============================
# DECORADOR LOGIN REQUERIDO
# ==============================
def login_requerido(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        if not hasattr(g, "usuario_actual") or not hasattr(g, "token_actual"):
            
            if request.path.startswith("/api"):
                return jsonify({"error": "No autenticado"}), 401
            
            return redirect(url_for("auth.login"))

        token = g.token_actual

        if token.esta_expirado():
            
            token.usado = True
            db.session.commit()

            if request.path.startswith("/api"):
                return jsonify({"error": "Sesión expirada"}), 401

            return redirect(url_for("auth.login"))

        token.fecha_expiracion = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        db.session.commit()

        return f(*args, **kwargs)

    return decorated

# ==============================
# DECORADOR PERMISO REQUERIDO
# ==============================
def permiso_requerido(modulo, accion):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not g.usuario_actual:
                abort(401)

            if not g.usuario_actual.tiene_permiso(modulo, accion):
                abort(403, description=f"{modulo}/{accion}")

            return f(*args, **kwargs)
        return wrapper
    return decorator

def api_protegida(modulo, accion):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            
            if not hasattr(g, "usuario_actual"):
                return {"error": "No autenticado"}, 401

            if not g.usuario_actual.tiene_permiso(modulo, accion):
                return {"error": "Sin permisos"}, 403

            return f(*args, **kwargs)
        return wrapper
    return decorator

def decrypt_url_id(param="id"):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                kwargs[param] = decrypt_id(kwargs[param])
            except:
                abort(404)
            return f(*args, **kwargs)
        return wrapper
    return decorator