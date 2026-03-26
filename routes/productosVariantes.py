# routes/productosVariantes.py
import datetime 
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify
from database.mysql import db, Producto, ProductoVariante,Articulo, Categoria,Color, Talla
from middlerware import login_requerido, permiso_requerido, decrypt_url_id
from sqlalchemy import or_
from forms import ProductoForm,ProductoVarianteForm
from werkzeug.utils import secure_filename
import os
import uuid
from decimal import Decimal

productosVariantes = Blueprint(
    "productosVariantes",
    __name__,
    url_prefix="/productosVariantes"
)

apiProductosVariantes = Blueprint(
    "api_productosVariantes",
    __name__,
    url_prefix="/api/productosVariantes"
)

#===========================================
# Buscador
#===========================================
@productosVariantes.route("/buscador")
@login_requerido
@permiso_requerido("productosVariantes", "buscador")
def buscador():
    search = request.args.get("search", "", type=str)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    # Base query
    query = ProductoVariante.query.join(Producto).filter(Producto.activo == True)

    # Filtro de búsqueda
    if search:
        query = query.filter(
            or_(
                Producto.nombre.ilike(f"%{search}%"),
                Producto.descripcion.ilike(f"%{search}%")
            )
        )

    # Paginación
    pagination = query.order_by(Producto.nombre.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    # Formato para tabla
    rows = [
        [
            ("ID", p.id),
            ("Producto", p.producto.nombre),
            ("Talla", p.talla.nombre),
            ("Color", p.color.nombre),
            ("Precio", p.precio_venta)
        ]
        for p in pagination.items
    ]

    return render_template(
        "productosVariantes/buscador.html",
        headers=["ID", "Producto", "Talla", "Color", "Precio"],
        rows=rows,
        pagination=pagination,
        search=search,
        per_page=per_page,
        endpoint="productos",
        return_url=request.args.get("return_url"),
        titulo="Buscador de Productos",
        descripcion="Busca productos por nombre o descripción"
    )

@productosVariantes.route("/seleccionar/<int:id>")
@login_requerido
def seleccionar(id):
    return_url = request.args.get("return_url")

    return redirect(f"{return_url}?producto_variante_id={id}")

# ══════════════════════════════════════════════════════
# VISTA — Lista de productos
# ══════════════════════════════════════════════════════
@productosVariantes.route("/")
@login_requerido
@permiso_requerido("productosVariantes", "ver")
def lista():
    search   = request.args.get("search", "", type=str)
    categoria = request.args.get("categoria", type=int)
    page     = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    query = (
        ProductoVariante.query
        .join(ProductoVariante.producto)
        .join(ProductoVariante.talla)
        .join(ProductoVariante.articulo)
        .outerjoin(Producto.color)
        .filter(ProductoVariante.activo == True)
        .filter(Producto.activo == True)
    )

    if search:
        query = query.filter(Producto.nombre.ilike(f"%{search}%"))

    if categoria is not None:
        query = query.filter(Producto.categoria_id == categoria)

    pagination = query.order_by(Producto.nombre.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    #TRANSFORMACIÓN PARA MACRO
    rows = [
        [
            ("id", p.producto.id),
            ("producto", p.producto.nombre),
            ("talla", p.talla.nombre),
            ("color", p.producto.color.nombre if p.producto.color else "—"),
            ("precio", f"${p.precio_venta:,.2f}")
        ]
        for p in pagination.items
    ]

    headers = ["ID", "Producto", "Talla", "Color", "Precio"]

    return render_template(
        "productosVariantes/lista.html", 
        headers=headers,
        rows=rows,
        pagination=pagination,
        endpoint="productosVariantes",
        search=search,
        per_page=per_page,
        titulo="Productos",
        descripcion="Listado general de Productos"
    )

# ==============================
# CREAR
# ==============================
@productosVariantes.route("/crear", methods=["GET", "POST"])
@login_requerido
@permiso_requerido("productosVariantes", "crear")
def crear():

    form_producto = ProductoForm(request.form)
    form_variante = ProductoVarianteForm(request.form)

    # 🔹 Selects
    form_producto.categoria_id.choices = [
        (c.id, c.nombre) for c in Categoria.query.order_by(Categoria.nombre).all()
    ]

    form_producto.color_id.choices = [
        (c.id, c.nombre) for c in Color.query.order_by(Color.nombre).all()
    ]

    form_variante.talla_id.choices = [
        (t.id, t.nombre) for t in Talla.query.order_by(Talla.nombre).all()
    ]

    if request.method == "POST" and form_producto.validate():

        try:
            # =========================
            # 📸 IMAGEN
            # =========================
            imagen = request.files.get("imagen")
            ruta_imagen = None

            if imagen and imagen.filename != "":
                
                # 🔒 validar tipo
                if imagen.mimetype not in ["image/jpeg", "image/png"]:
                    raise Exception("Solo se permiten imágenes JPG o PNG")

                # 🔒 nombre seguro
                filename = secure_filename(imagen.filename)
                ext = filename.split(".")[-1]

                # 🔥 nombre único
                nuevo_nombre = f"{uuid.uuid4()}.{ext}"

                carpeta = "static/uploads/productos"
                os.makedirs(carpeta, exist_ok=True)

                ruta = os.path.join(carpeta, nuevo_nombre)
                imagen.save(ruta)

                # guardar ruta relativa
                ruta_imagen = f"uploads/productos/{nuevo_nombre}"

            # =========================
            # 1. Producto
            # =========================
            producto = Producto(
                nombre=form_producto.nombre.data,
                categoria_id=form_producto.categoria_id.data,
                color_id=form_producto.color_id.data,
                descripcion=form_producto.descripcion.data,
                imagen=ruta_imagen,
                creado_por=g.usuario_actual.id
            )
            db.session.add(producto)
            db.session.flush()

            # =========================
            # 2. Variantes
            # =========================
            tallas = request.form.getlist("talla_id[]")
            precios = request.form.getlist("precio_venta[]")

            if not tallas or not precios:
                raise Exception("Debes agregar al menos una variante")

            if len(tallas) != len(precios):
                raise Exception("Datos inconsistentes")

            if len(set(tallas)) != len(tallas):
                raise Exception("No puedes repetir tallas")

            # =========================
            # 3. Crear variantes
            # =========================
            for i in range(len(tallas)):

                if not tallas[i] or not precios[i]:
                    continue

                articulo = Articulo(
                    tipo="PRODUCTO",
                    creado_por=g.usuario_actual.id
                )
                db.session.add(articulo)
                db.session.flush()

                variante = ProductoVariante(
                    producto_id=producto.id,
                    talla_id=int(tallas[i]),
                    precio_venta=Decimal(precios[i]),
                    articulo_id=articulo.id,
                    creado_por=g.usuario_actual.id
                )
                db.session.add(variante)

            db.session.commit()

            flash("Producto creado correctamente", "success")
            return redirect(url_for("productosVariantes.lista"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "error")

    return render_template(
        "productosVariantes/crear.html",
        form_producto=form_producto,
        form_variante=form_variante,
        titulo="Crear Producto",
        descripcion="Registro de producto y su variante"
    )

##### Productos editar
# ==============================
# EDITAR
# ==============================
@productosVariantes.route("/editar/<id>", methods=["GET", "POST"])
@decrypt_url_id()
@login_requerido
@permiso_requerido("productosVariantes","editar")
def editar(id):

    # 🔹 obtener variante y producto
    variante = ProductoVariante.query.get_or_404(id)
    producto = variante.producto

    # 🔹 forms
    form_producto = ProductoForm(request.form, obj=producto)
    form_variante = ProductoVarianteForm(request.form)

    # 🔹 selects
    form_producto.categoria_id.choices = [
        (c.id, c.nombre) for c in Categoria.query.order_by(Categoria.nombre).all()
    ]

    form_producto.color_id.choices = [
        (c.id, c.nombre) for c in Color.query.order_by(Color.nombre).all()
    ]

    form_variante.talla_id.choices = [
        (t.id, t.nombre) for t in Talla.query.order_by(Talla.nombre).all()
    ]

    # 🔹 variantes actuales
    variantes = ProductoVariante.query.filter_by(producto_id=producto.id).all()

    # =========================
    # POST
    # =========================
    if request.method == "POST" and form_producto.validate():

        try:
            # =========================
            # 📸 IMAGEN (REEMPLAZO)
            # =========================
            imagen = request.files.get("imagen")

            if imagen and imagen.filename != "":

                if imagen.mimetype not in ["image/jpeg", "image/png"]:
                    raise Exception("Solo JPG o PNG")

                # 🗑️ eliminar anterior
                if producto.imagen:
                    ruta_vieja = os.path.join("static", producto.imagen)
                    if os.path.exists(ruta_vieja):
                        os.remove(ruta_vieja)

                filename = secure_filename(imagen.filename)
                ext = filename.split(".")[-1]
                nuevo_nombre = f"{uuid.uuid4()}.{ext}"

                carpeta = "static/uploads/productos"
                os.makedirs(carpeta, exist_ok=True)

                ruta = os.path.join(carpeta, nuevo_nombre)
                imagen.save(ruta)

                producto.imagen = f"uploads/productos/{nuevo_nombre}"

            # =========================
            # ✏️ PRODUCTO
            # =========================
            producto.nombre = form_producto.nombre.data
            producto.categoria_id = form_producto.categoria_id.data
            producto.color_id = form_producto.color_id.data
            producto.descripcion = form_producto.descripcion.data

            producto.editado_por = g.usuario_actual.id
            producto.fecha_edicion = datetime.datetime.utcnow()

            # =========================
            # 🔄 VARIANTES
            # =========================
            ProductoVariante.query.filter_by(producto_id=producto.id).delete()

            tallas = request.form.getlist("talla_id[]")
            precios = request.form.getlist("precio_venta[]")

            if not tallas or not precios:
                raise Exception("Debes agregar al menos una variante")

            if len(tallas) != len(precios):
                raise Exception("Datos inconsistentes")

            if len(set(tallas)) != len(tallas):
                raise Exception("No puedes repetir tallas")

            for i in range(len(tallas)):

                if not tallas[i] or not precios[i]:
                    continue

                articulo = Articulo(
                    tipo="PRODUCTO",
                    creado_por=g.usuario_actual.id
                )
                db.session.add(articulo)
                db.session.flush()

                nueva_variante = ProductoVariante(
                    producto_id=producto.id,
                    talla_id=int(tallas[i]),
                    precio_venta=Decimal(precios[i]),
                    articulo_id=articulo.id,
                    creado_por=g.usuario_actual.id
                )
                db.session.add(nueva_variante)

            db.session.commit()

            flash("Producto actualizado correctamente", "success")
            return redirect(url_for("productosVariantes.lista"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "error")

    # =========================
    # GET
    # =========================
    return render_template(
        "productosVariantes/editar.html",
        form_producto=form_producto,
        form_variante=form_variante,
        producto=producto,
        variantes=variantes,
        titulo="Editar Producto",
        descripcion="Modificar información del producto"
    )

# ##### Productos eliminar
@productosVariantes.route("/eliminar/<id>")
@decrypt_url_id()
@login_requerido
@permiso_requerido("productosVariantes","eliminar")
def eliminar(id):
    producto = Producto.query.filter_by(id=id, activo=True).first_or_404()

    # Soft delete producto
    producto.activo = False
    producto.fecha_eliminacion = datetime.datetime.utcnow()
    producto.eliminado_por = g.usuario_actual.id

    # Soft delete de TODAS sus variantes
    for variante in producto.variantes:  # relación ORM
        if variante.activo:
            variante.activo = False
            variante.fecha_eliminacion = datetime.datetime.utcnow()
            variante.eliminado_por = g.usuario_actual.id

    db.session.commit()

    flash("Producto eliminado correctamente")
    return redirect(url_for("productosVariantes.lista"))