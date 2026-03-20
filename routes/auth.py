# routes/auth.py
import uuid
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from database.mysql import Usuario, Token, db
import sys
from pprint import pprint
from utils.security import verify_password

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        correo = request.form.get("correo")
        contrasenia = request.form.get("contrasenia")

        user = Usuario.query.filter_by(correo=correo, activo=True).first()

        if user and verify_password(user.contrasenia, contrasenia):

            nuevo_token = str(uuid.uuid4())

            token_db = Token(
                usuario_id=user.id,
                token=nuevo_token,
                tipo="login",
                fecha_expiracion=datetime.datetime.utcnow() + datetime.timedelta(hours=2)
            )

            db.session.add(token_db)
            db.session.commit()

            response = make_response(redirect(url_for("main.index")))

            response.set_cookie(
                "auth_token",
                nuevo_token,
                httponly=True,
                samesite="Lax"
            )

            return response

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
