# routes/auth.py
import uuid
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from database.mysql import Usuario, Token, db
import sys
from pprint import pprint
from utils.security import verify_password
import random
from flask_mail import Message
from extensions import mail

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        correo = request.form.get("correo")
        contrasenia = request.form.get("contrasenia")

        user = Usuario.query.filter_by(correo=correo, activo=True).first()

        if user and verify_password(user.contrasenia, contrasenia):

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

        flash("Credenciales incorrectas", "error")

    return render_template("auth/login.html")

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

            # 🔒 validar expiración
            if token_db.esta_expirado():
                flash("Código expirado", "error")
                return redirect(request.url)

            # 🔥 anti brute force
            if token_db.intentos >= 5:
                flash("Demasiados intentos", "error")
                return redirect(url_for("auth.login"))

            token_db.usado = True

            # 🔑 crear sesión real
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
                secure=False  # 🔥 IMPORTANTE EN LOCAL
            )

            return response

        else:
            # 🔥 aumentar intentos si existe alguno activo
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