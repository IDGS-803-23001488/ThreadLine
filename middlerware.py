from flask import g, redirect, abort, url_for
from functools import wraps

# ==============================
# DECORADOR LOGIN REQUERIDO
# ==============================
def login_requerido(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(g, "usuario_actual"):
            return redirect(url_for("auth.login"))
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