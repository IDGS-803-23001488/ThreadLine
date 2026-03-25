# routes/auth.py
import uuid
import datetime

from wtforms import validators
from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from database.mysql import Cliente, Usuario, Token, db, Rol
import sys
from pprint import pprint
from utils.security import verify_password
import random
from flask_mail import Message
from extensions import mail
from flask import session

REQUIERE_2FA = False

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form.get("correo")
        contrasenia = request.form.get("contrasenia")

        usuario = Usuario.query.filter_by(correo=correo, activo=True).first()
        if not usuario:
            flash("El correo no está registrado", "danger")
            return render_template("auth/login.html")
        
        if usuario.bloqueado:
            return usuario_bloqueado_response(usuario)
        
        if not usuario.contrasenia or ":" not in usuario.contrasenia:
            flash("Error de seguridad: Formato de contraseña inválido.", "danger")
            return redirect(url_for("auth.login"))

        if not verify_password(usuario.contrasenia, contrasenia):
            flash("Contraseña incorrecta", "danger")
            return redirect(url_for("auth.login"))
        
        es_cliente = any(rol.nombre.lower() == "cliente" for rol in usuario.roles if rol.activo)
        tiene_permiso_tienda = any(
            p.modulo == "ecomers" and p.accion == "ver"
            for rol in usuario.roles if rol.activo
            for p in rol.permisos
        )
        es_empleado = any(rol.activo for rol in usuario.roles) and not es_cliente

        if usuario.bloqueado:
            return usuario_bloqueado_response(usuario)
        
        if es_empleado and tiene_permiso_tienda:
            session['correo'] =  usuario.correo
            return render_template("auth/login_user.html")
        if es_cliente :
            session['tipo_login'] = 'cliente'
            return verificar_user(usuario)
        
        session['tipo_login'] = 'empleado'
        return verificar_user(usuario)

    return render_template("auth/login.html")

@auth.route('/login_user', methods=['GET', 'POST'])
def login_user():
    if request.method == "POST":
        tipo = request.form.get("tipo")
        correo = session.get('correo')
        
        user = Usuario.query.filter_by(correo=correo, activo=True).first()
        if user:
            session['tipo_login'] = tipo
            session.pop('correo', None)
            return verificar_user(user)
        
    return render_template("auth/login_user.html")

@auth.route("/logout")
def logout():

    token_cookie = request.cookies.get("auth_token")

    if token_cookie:
        token_db = Token.query.filter_by(token=token_cookie, usado=False).first()
        if token_db:
            token_db.usado = True
            db.session.commit()

    response = make_response(redirect(url_for("auth.login")))
    response.delete_cookie("auth_token")

    return response

def enviar_codigo(destino, codigo):
    msg = Message(
        subject="Código de verificación",
        recipients=[destino]
    )

    msg.body = f"""
Tu código de verificación es: {codigo}

Expira en 10 minutos.
"""

    mail.send(msg)

def usuario_bloqueado_response(user):
    Token.query.filter_by(usuario_id=user.id, usado=False).update({
        "usado": True
    })
    db.session.commit()

    if request.path.startswith("/api"):
        return {"error": "Usuario bloqueado"}, 403

    flash("Tu cuenta está bloqueada. Contacta al administrador.", "error")
    return redirect(url_for("auth.login"))

@auth.route("/verificar-2fa/<int:user_id>", methods=["GET", "POST"])
def verificar_2fa(user_id):

    if request.method == "POST":
        codigo = request.form.get("codigo")

        token_db = Token.query.filter_by(
            usuario_id=user_id,
            token=codigo,
            tipo="2fa",
            usado=False
        ).first()

        if token_db:
            if token_db.esta_expirado():
                flash("Código expirado", "error")
                return redirect(request.url)

            if token_db.intentos >= 3:
                user = Usuario.query.get(user_id)
                user.bloqueado = True
                db.session.commit()

                return usuario_bloqueado_response(user)

            token_db.usado = True

            nuevo_token = str(uuid.uuid4())

            login_token = Token(
                usuario_id=user_id,
                token=nuevo_token,
                tipo="login",
                fecha_expiracion=datetime.datetime.utcnow() + datetime.timedelta(hours=2)
            )

            db.session.add(login_token)
            db.session.commit()

            response = make_response(redirect(url_for("main.index")))
            response.set_cookie(
                "auth_token",
                nuevo_token,
                httponly=True,
                samesite="Lax",
                secure=False
            )

            return response

        else:
            intento = Token.query.filter_by(
                usuario_id=user_id,
                tipo="2fa",
                usado=False
            ).first()

            if intento:
                intento.intentos += 1
                db.session.commit()

            flash("Código inválido", "error")

    return render_template("auth/verificar_2fa.html")

def verificar_user(user):
        
            
            if not REQUIERE_2FA:
                nuevo_token = str(uuid.uuid4())

                login_token = Token(
                    usuario_id=user.id,
                    token=nuevo_token,
                    tipo="login",
                    fecha_expiracion=datetime.datetime.utcnow() + datetime.timedelta(hours=2)
                )

                db.session.add(login_token)
                db.session.commit()
                tipo_acceso = session.get('tipo_login')
                destino = url_for("main.pagina_blanca") if tipo_acceso == 'cliente' else url_for("main.index")
                
                session.pop('correo', None)
                session.pop('tipo_login', None)

                response = make_response(redirect(destino))
                response.set_cookie(
                    "auth_token",
                    nuevo_token,
                    httponly=True,
                    samesite="Lax",
                    secure=False
                )

                return response

            codigo = str(random.randint(100000, 999999))

            token_db = Token(
                usuario_id=user.id,
                token=codigo,
                tipo="2fa",
                fecha_expiracion=datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
            )

            db.session.add(token_db)
            db.session.commit()

            enviar_codigo(user.correo, codigo)

            return redirect(url_for("auth.verificar_2fa", user_id=user.id))

        