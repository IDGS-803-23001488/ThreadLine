# routes/roles.py
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from database.mysql import db, Rol, Permiso
from forms import RolForm
from middlerware import login_requerido, permiso_requerido, decrypt_url_id

roles = Blueprint("roles", __name__, url_prefix="/roles")

# ==============================
# LISTA
# ==============================
@roles.route("/")
@login_requerido
@permiso_requerido("roles", "ver")
def lista():
    search = request.args.get("search", "", type=str)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    query = Rol.query.filter_by(activo=True)
    
    if search:
        query = query.filter(Rol.nombre.ilike(f"%{search}%"))

    pagination = query.order_by(Rol.id.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    rows = [
        [("ID", u.id), ("Nombre", u.nombre), ("Descripción", u.descripcion)]
        for u in pagination.items
    ]


    return render_template(
        "roles/lista.html",
        headers=["ID", "Nombre", "Descripción"],
        rows=rows,
        pagination=pagination,
        search=search,
        per_page=per_page,
        titulo="Roles",
        descripcion="Listado de roles y permisos"
    )

# ==============================
# CREAR
# ==============================
@roles.route("/crear", methods=["GET", "POST"])
@login_requerido
@permiso_requerido("roles", "crear")
def crear():
    form = RolForm(request.form)

    todos_permisos = Permiso.query.all()

    permisos_por_modulo = {}
    for p in todos_permisos:
        if p.modulo not in permisos_por_modulo:
            permisos_por_modulo[p.modulo] = {}
        permisos_por_modulo[p.modulo][p.accion] = p

    if request.method == "POST" and form.validate():
        nuevo = Rol(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            creado_por=g.usuario_actual.id  # 🔥 Auditoría
        )

        permisos_seleccionados = request.form.getlist("permisos")
        if permisos_seleccionados:
            nuevo.permisos = Permiso.query.filter(Permiso.id.in_(permisos_seleccionados)).all()

        db.session.add(nuevo)
        db.session.commit()

        flash("Rol creado correctamente")
        return redirect(url_for("roles.lista"))

    return render_template(
        "roles/crear.html",
        form=form,
        todos_permisos=todos_permisos,
        permisos_por_modulo=permisos_por_modulo,
        titulo="Crear Rol",
        descripcion="Registro de un nuevo rol"
    )

# ==============================
# EDITAR
# ==============================
@roles.route("/editar/<id>", methods=["GET", "POST"])
@decrypt_url_id()
@login_requerido
@permiso_requerido("roles", "editar")
def editar(id):
    rol = Rol.query.get_or_404(id)
    form = RolForm(request.form, obj=rol)
    todos_permisos = Permiso.query.all()

    permisos_por_modulo = {}
    for p in todos_permisos:
        if p.modulo not in permisos_por_modulo:
            permisos_por_modulo[p.modulo] = {}
        permisos_por_modulo[p.modulo][p.accion] = p
    
    if request.method == "POST" and form.validate():
        form.populate_obj(rol)

        permisos_seleccionados = request.form.getlist("permisos")
        rol.permisos = Permiso.query.filter(Permiso.id.in_(permisos_seleccionados)).all()

        db.session.commit()
        flash("Rol actualizado correctamente")
        return redirect(url_for("roles.lista"))

    return render_template(
        "roles/editar.html",
        form=form,
        rol=rol,
        todos_permisos=todos_permisos,
        permisos_por_modulo=permisos_por_modulo,
        titulo="Editar Rol",
        descripcion="Modificar información del rol"
    )

# ==============================
# ELIMINAR (SOFT DELETE)
# ==============================
@roles.route("/eliminar/<id>")
@decrypt_url_id()
@login_requerido
@permiso_requerido("roles", "eliminar")
def eliminar(id):
    rol = Rol.query.filter_by(id=id, activo=True).first_or_404()

    rol.activo = False
    rol.fecha_eliminacion = datetime.datetime.utcnow()
    rol.eliminado_por = g.usuario_actual.id

    db.session.commit()
    flash("Rol eliminado correctamente")
    return redirect(url_for("roles.lista"))