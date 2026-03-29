# routes/auth.py
import uuid
import datetime

from wtforms.validators import url
from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from database.mysql import Usuario, Token, db, Cliente
import sys
from pprint import pprint
from utils.security import verify_password
import random
from flask_mail import Message
from extensions import mail
from utils.crypto_url import encrypt_id, decrypt_id
from middlerware import login_requerido, permiso_requerido, decrypt_url_id
from forms import ClienteForm
from utils.security import hash_password


REQUIERE_2FA = False

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    
    if request.method == "POST":

        correo = request.form.get("correo")
        contrasenia = request.form.get("contrasenia")
        
        user = Usuario.query.filter_by(correo=correo, activo=True).first()
        cliente = Cliente.query.filter_by(correo=correo, activo=True).first()
        if not user and not cliente:
            flash("Usuario no encontrado", "error")
            return redirect(url_for('auth.login'))
        
        user_valido = user and verify_password(user.contrasenia, contrasenia)
        cliente_valido = cliente and verify_password(cliente.contrasenia, contrasenia)
        
        if (not user and cliente)or (user and not cliente):
            if user and user.bloqueado:
                return usuario_bloqueado_response(user)
            if cliente and not cliente.activo:
                return usuario_bloqueado_response(cliente)
        if user_valido or cliente_valido:
            if user:
                Token.query.filter_by(usuario_id=user.id, tipo="error_login", usado=False).update({"usado": True})
            if cliente:
                Token.query.filter_by(cliente_id=cliente.id, tipo="error_login", usado=False).update({"usado": True})
                db.session.commit()

            if not REQUIERE_2FA:
                nuevo_token = str(uuid.uuid4())
                login_token = None
                destino = ""
                if user_valido and cliente_valido:
                        return redirect( url_for(
                            "auth.modal_user",
                            id_cliente=encrypt_id(cliente.id),
                            id_usuario=encrypt_id(user.id)
                            ))
                if cliente_valido or user_valido:
                    login_token = Token(
                        usuario_id=user.id if user_valido else None,
                        cliente_id=cliente.id if cliente_valido else None,
                        token=nuevo_token,
                        tipo = "login_cliente" if cliente_valido else "login_usuario",
                        fecha_expiracion=datetime.datetime.utcnow() + datetime.timedelta(hours=2)
                    )
                    destino = 'main.ecommerse' if cliente_valido else 'main.index'
                db.session.add(login_token)
                db.session.commit()
                
                response = make_response(redirect(url_for(destino)))
                response.set_cookie(
                    "auth_token",
                    nuevo_token,
                    httponly=True,
                    samesite="Lax",
                    secure=False
                )

                return response

            codigo = str(random.randint(100000, 999999))
            token_db = None
            
            token_db = Token(
                usuario_id = user.id if user else None,
                cliente_id = cliente.id if cliente else None,
                token=codigo,
                tipo="2fa",
                fecha_expiracion=datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
            )
            db.session.add(token_db)
            db.session.commit()

            enviar_codigo(cliente.correo, codigo)

            return redirect(url_for("auth.verificar_2fa", user_id=user.id))

        else:
            intento = None
            if user:
                intento = Token.query.filter_by(
                    usuario_id=user.id,
                    tipo="error_login",
                    usado=False
                ).first()

            elif cliente:
                intento = Token.query.filter_by(
                    cliente_id=cliente.id,
                    tipo="error_login",
                    usado=False
                ).first()

            if not intento:
                intento = Token(
                    usuario_id=user.id if user else None, 
                    cliente_id=cliente.id if cliente else None, 
                    tipo='error_login',
                    intentos=1, 
                    fecha_expiracion=datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
                    usado=False
                )
                db.session.add(intento)
                db.session.commit()
            else:
                intento.intentos += 1
                db.session.commit()
            if intento.intentos >= 3:
                if user:
                    user.bloqueado = True
                    user.activo = False
                if cliente:
                    cliente.activo = False
                
                intento.fecha_expiracion=datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
                intento.usado = True
                db.session.commit()
                
                return usuario_bloqueado_response(user if user else cliente)
                           
            flash(f"Credenciales incorrectas  intento {intento.intentos} de 3", "error")
            return render_template("auth/login.html")
    return render_template("auth/login.html")

@auth.route("/modal_user/<id_cliente>/<id_usuario>", methods=["GET", "POST"])
def modal_user(id_cliente, id_usuario):
    id_cliente = decrypt_id(id_cliente)
    id_usuario = decrypt_id(id_usuario)
    print(id_usuario)
    if not id_usuario or not id_cliente:
        flash("Acceso inválido", "danger")
        return redirect(url_for("auth.login"))
    usuario = Usuario.query.filter_by(id=id_usuario, activo=True).first()
    cliente = Cliente.query.filter_by(id=id_cliente, activo=True).first()
    
    if not usuario or not cliente:
        flash("Usuario o cliente no encontrado", "danger")
        return redirect(url_for("auth.login"))
    
    tipo = request.form.get("tipo")
    if request.method == "POST":
        
            tipo = request.form.get("tipo")
            if usuario and usuario.bloqueado and tipo == "empleado":
                return usuario_bloqueado_response(usuario)
            if cliente and not cliente.activo and tipo == "cliente":
                return usuario_bloqueado_response(cliente)
            if not REQUIERE_2FA:
                    nuevo_token = str(uuid.uuid4())
                    login_token = None
                    login_token = Token(
                        cliente_id=id_cliente if tipo == "cliente" else None,
                        usuario_id=id_usuario if tipo == "empleado" else None,
                        token=nuevo_token,
                        tipo = "login_cliente" if tipo == "cliente" else "login_usuario",
                        fecha_expiracion=datetime.datetime.utcnow() + datetime.timedelta(hours=2)
                    )
                    destino = "main.ecommerse" if tipo == "cliente" else "main.index"
                    db.session.add(login_token)
                    db.session.commit()

                    response = make_response(redirect(url_for(destino)))
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
                usuario_id=usuario.id if tipo == 'empleado' else None,
                cliente_id = cliente.id if tipo == 'cliente' else None,
                token=codigo,
                tipo="2fa",
                fecha_expiracion=datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
            )
            db.session.add(token_db)
            db.session.commit()
            enviar_codigo(cliente.correo, codigo)
            return redirect(url_for("auth.verificar_2fa", user_id=(usuario.id if tipo=="empleado" else cliente.id), tipo=tipo))

    return render_template("auth/modal_user.html")

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

def usuario_bloqueado_response(user_obj):
    if isinstance(user_obj, Usuario):
        Token.query.filter_by(usuario_id=user_obj.id, usado=False).update({"usado": True})
        contexto = {
            "usuario": user_obj, 
            "tipo_bloqueo": 'empleado',
            "tipo_cuenta": 'Empleado'
        }
    else:
        Token.query.filter_by(cliente_id=user_obj.id, usado=False).update({"usado": True})
        contexto = {
            "cliente": user_obj, 
            "tipo_bloqueo": 'cliente',
            "tipo_cuenta": 'Cliente'
        }

    db.session.commit()

    if request.path.startswith("/api"):
        return {"error": "Usuario bloqueado"}, 403

    flash("Tu cuenta está bloqueada. Contacta al administrador.", "error")
    
    return render_template("auth/bloqueo.html", **contexto)


@auth.route("/verificar-2fa/<int:user_id>/<tipo>", methods=["GET", "POST"])
def verificar_2fa(user_id,tipo):

    if request.method == "POST":
        codigo = request.form.get("codigo")

        token_db = Token.query.filter_by(
            usuario_id= user_id if tipo == 'empleado' else None,
            cliente_id = user_id if tipo == 'cliente' else None,
            token=codigo,
            tipo="2fa",
            usado=False
        ).first()

        if token_db:
            if token_db.esta_expirado():
                flash("Código expirado", "error")
                return redirect(request.url)

            if token_db.intentos >= 3:
                if tipo == 'empleado':
                    user = Usuario.query.get(user_id)
                    if user:
                        user.bloqueado = True
                        user.activo = False
                else:
                    user = Cliente.query.get(user_id)
                    if user:
                        user.bloqueado = True
                        user.activo = False
                db.session.commit()

                return usuario_bloqueado_response(user) if user else redirect(url_for("auth.login"))

            token_db.usado = True

            nuevo_token = str(uuid.uuid4())

            login_token = Token(
                usuario_id= user_id if tipo == 'empleado' else None,
                cliente_id = user_id if tipo == 'cliente' else None,
                token=nuevo_token,
                tipo="login_usuario" if tipo == 'empleado' else "login_cliente",
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
                usuario_id= user_id if tipo == 'empleado' else None,
                cliente_id = user_id if tipo == 'cliente' else None,
                tipo="2fa",
                usado=False
            ).first()

            if intento:
                intento.intentos += 1
                if intento.intentos >= 3:
                    if tipo == 'empleado':
                        user = Usuario.query.get(user_id)
                        if user:
                            user.bloqueado = True
                            user.activo = False
                    else:
                        user = Cliente.query.get(user_id)
                        if user:
                            user.bloqueado = True
                            user.activo = False
                    intento.usado = True
                    db.session.commit()
                    return usuario_bloqueado_response(user) if user else redirect(url_for("auth.login"))
                db.session.commit()
                flash(f"Código inválido. Intento {intento.intentos} de 3", "error")
            else:
                flash("Código inválido", "error")

    return render_template("auth/verificar_2fa.html")

@auth.route("/registrar", methods=["GET", "POST"])
def registrar():
    form = ClienteForm(request.form)
    
    if request.method == "POST" and form.validate():
        
        existente = Cliente.query.filter_by(correo = form.correo.data).first()
        
        if existente :
            flash("El correo ya existe","correo")
            return render_template("auth/registrar.html",form=form)
        
        nuevo = Cliente(
            nombre=form.nombre.data,
            correo = form.correo.data,
            contrasenia = hash_password(form.contrasenia.data),
            telefono=form.telefono.data,
            direccion= form.direccion.data,
            fecha_registro = datetime.datetime.now()
        )
        
        db.session.add(nuevo)
        db.session.commit()
        
        flash("Ahora eres parte")
        return redirect(url_for("auth.login"))
    
    return render_template(
        "auth/registrar.html",
        form=form,
        titulo="Registro",
        telefono="Registro de nuevo cliente"
    )
