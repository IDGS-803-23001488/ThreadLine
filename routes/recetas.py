# routes/recetas.py
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify, make_response
from database.mysql import db, Receta, RecetaDetalle, ProductoVariante, MateriaPrima, Producto, Talla, Color
from middlerware import login_requerido, permiso_requerido, decrypt_url_id
from sqlalchemy import or_
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus import Frame, KeepInFrame
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

recetas = Blueprint(
    "recetas",
    __name__,
    url_prefix="/recetas"
)

apiRecetas = Blueprint(
    "api_recetas",
    __name__,
    url_prefix="/api/recetas"
)

# ===========================================
# Vistas
# ===========================================


#===========================================
# Lista 
#===========================================
@recetas.route("/")
@login_requerido
@permiso_requerido("recetas", "ver")
def lista():
    search = request.args.get("search", "", type=str)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    query = (
        Receta.query
        .filter(Receta.activo == True)
        .join(Receta.producto_variante)
        .join(ProductoVariante.producto)
        .join(ProductoVariante.talla)
        .outerjoin(Producto.color)
    )

    if search:
        query = query.filter(
            or_(
                Producto.nombre.ilike(f"%{search}%"),
                Talla.nombre.ilike(f"%{search}%"),
            )
        )

    pagination = query.order_by(Receta.id.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    rows = [
        [
            ("ID",           r.id),
            ("Producto",     r.producto_variante.producto.nombre),
            ("Talla",        r.producto_variante.talla.nombre),
            ("Color",        r.producto_variante.producto.color.nombre if r.producto_variante.producto.color else "—"),
            ("Cantidad Base",r.cantidad_base),
            ("Insumos",      len(r.detalles)),
        ]
        for r in pagination.items
    ]

    return render_template(
        "recetas/lista.html",
        headers=["ID", "Producto", "Talla", "Color", "Cantidad Base", "Insumos"],
        rows=rows,
        pagination=pagination,
        search=search,
        per_page=per_page,
        endpoint="recetas",
        titulo="Recetas",
        descripcion="Listado general de recetas",
    )

@recetas.route("/crear", methods=["GET", "POST"])
@login_requerido
@permiso_requerido("recetas", "crear")
def crear():
    if request.method == "POST":
        return _guardar_receta(receta_id=None)

    return render_template(
        "recetas/crear.html",
        titulo="Crear Receta",
        descripcion="Registro de nueva receta de producción",
    )


@recetas.route("/editar/<id>", methods=["GET", "POST"])
@decrypt_url_id()
@login_requerido
@permiso_requerido("recetas", "editar")
def editar(id):
    receta = Receta.query.get_or_404(id)

    if request.method == "POST":
        return _guardar_receta(receta_id=id)

    return render_template(
        "recetas/editar.html",
        titulo="Editar Receta",
        descripcion="Modificación de receta de producción",
        receta=receta,
    )


# ===========================================
# Lógica compartida crear / editar
# ===========================================

def _guardar_receta(receta_id):
    variante_id   = request.form.get("producto_variante_id", type=int)
    cantidad_base = request.form.get("cantidad_base", 1, type=int)
    mp_ids        = request.form.getlist("materia_prima_id")
    cantidades    = request.form.getlist("cantidad_neta")

    # --- Validaciones ---
    errores = []
    if not variante_id:
        errores.append("Debes seleccionar una variante de producto.")
    if not mp_ids:
        errores.append("La receta debe tener al menos un insumo.")
    if len(mp_ids) != len(cantidades):
        errores.append("Error en el formulario: insumos y cantidades no coinciden.")
    if len(mp_ids) != len(set(mp_ids)):
        errores.append("Hay materias primas duplicadas en la receta.")

    if errores:
        for e in errores:
            flash(e, "error")
        return redirect(request.url)

    # --- Guardar ---
    if receta_id:
        receta = Receta.query.get_or_404(receta_id)
        receta.producto_variante_id = variante_id
        receta.cantidad_base        = cantidad_base
        receta.fecha_edicion        = datetime.datetime.utcnow()
        receta.editado_por          = g.usuario_actual.id
        # Borrar detalles anteriores y recrear
        RecetaDetalle.query.filter_by(receta_id=receta_id).delete()
    else:
        receta = Receta(
            producto_variante_id=variante_id,
            cantidad_base=cantidad_base,
            activo=True,
            creado_por=g.usuario_actual.id,
        )
        db.session.add(receta)
        db.session.flush()

    for mp_id, cant in zip(mp_ids, cantidades):
        detalle = RecetaDetalle(
            receta_id=receta.id,
            materia_prima_id=int(mp_id),
            cantidad_neta=float(cant),
        )
        db.session.add(detalle)

    db.session.commit()
    flash("Receta guardada correctamente.", "success")
    return redirect(url_for("recetas.lista"))


# ===========================================
# API — Variantes (para modal buscador)
# ===========================================

@apiRecetas.route("/variantes", methods=["GET"])
@login_requerido
@permiso_requerido("recetas", "crear")
def api_variantes():
    search   = request.args.get("q", "", type=str)
    page     = request.args.get("page", 1, type=int)
    per_page = 10
    
    # Permitir filtrar variantes con recetas o todas
    solo_con_recetas = request.args.get("solo_con_recetas", "false").lower() == "true"

    query = (
        ProductoVariante.query
        .join(Producto)
        .join(Talla)
        .filter(
            ProductoVariante.activo == True,
            Producto.activo == True,
        )
    )
    
    # Solo si se solicita explícitamente
    if solo_con_recetas:
        query = query.filter(ProductoVariante.recetas.any())

    if search:
        query = query.filter(
            or_(
                Producto.nombre.ilike(f"%{search}%"),
                Talla.nombre.ilike(f"%{search}%"),
            )
        )

    pag = query.order_by(Producto.nombre.asc(), Talla.orden.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "data": [
            {
                "id":       v.id,
                "producto": v.producto.nombre,
                "talla":    v.talla.nombre,
                "color":    v.producto.color.nombre if v.producto.color else None,
                "color_hex": v.producto.color.hex  if v.producto.color else None,
                "precio":   float(v.precio_venta),
            }
            for v in pag.items
        ],
        "total":    pag.total,
        "pages":    pag.pages,
        "page":     pag.page,
        "has_next": pag.has_next,
        "has_prev": pag.has_prev,
    })


# ===========================================
# API — Materias primas
# ===========================================

@apiRecetas.route("/materias-primas", methods=["GET"])
@login_requerido
@permiso_requerido("recetas", "crear")
def api_materias_primas():
    materias = MateriaPrima.query.filter_by(activo=True).order_by(MateriaPrima.nombre).all()

    return jsonify({
        "data": [
            {
                "id":     mp.id,
                "nombre": mp.nombre,
                "unidad": mp.unidad.sigla if mp.unidad else "—",
                "merma":  0,  # ← Cambiado de porcentaje_merma a merma
            }
            for mp in materias
        ]
    })

# ===========================================
# API — Detalle de una receta (para editar)
# ===========================================

@apiRecetas.route("/<id>", methods=["GET"])
@decrypt_url_id()
@permiso_requerido("recetas", "ver")
def api_detalle(id):
    receta = Receta.query.get_or_404(id)
    v = receta.producto_variante

    return jsonify({
        "id":            receta.id,
        "cantidad_base": receta.cantidad_base,
        "variante": {
            "id":       v.id,
            "producto": v.producto.nombre,
            "talla":    v.talla.nombre,
            "color":    v.producto.color.nombre if v.producto.color else None,
            "color_hex": v.producto.color.hex   if v.producto.color else None,
        },
        "detalles": [
            {
                "materia_prima_id": d.materia_prima_id,
                "nombre":           d.materia_prima.nombre,
                "cantidad_neta":    float(d.cantidad_neta),
                "unidad":           d.materia_prima.unidad.sigla if d.materia_prima.unidad else "—",
                "merma":            0,
            }
            for d in receta.detalles
        ],
    })

@recetas.route("/eliminar/<id>")
@decrypt_url_id()
@login_requerido
@permiso_requerido("recetas", "eliminar")
def eliminar(id):

    receta = Receta.query.filter_by(id=id, activo=True).first_or_404()

    receta.activo = False
    receta.fecha_eliminacion = datetime.datetime.utcnow()
    receta.eliminado_por = g.usuario_actual.id

    db.session.commit()

    flash("Receta eliminada correctamente", "success")
    return redirect(url_for("recetas.lista"))

@recetas.route("/pdf/<id>")
@decrypt_url_id()
@login_requerido
@permiso_requerido("recetas", "ver")
def generar_pdf(id):
    receta = Receta.query.get_or_404(id)
    v = receta.producto_variante

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    # 🎨 Colores del layout
    PRIMARY = colors.HexColor("#0c7779")
    TEXT = colors.HexColor("#1f2937")
    MUTED = colors.HexColor("#6b7280")
    BORDER = colors.HexColor("#e5e7eb")

    # 🧾 Estilos personalizados
    title_style = ParagraphStyle(
        "title",
        parent=styles["Heading1"],
        fontSize=16,
        textColor=colors.white,
        alignment=1,  # center
        spaceAfter=10
    )

    label_style = ParagraphStyle(
        "label",
        parent=styles["Normal"],
        fontSize=9,
        textColor=MUTED
    )

    value_style = ParagraphStyle(
        "value",
        parent=styles["Normal"],
        fontSize=11,
        textColor=TEXT,
        spaceAfter=6
    )

    elements = []

    # =========================================
    # 🟩 HEADER (tipo navbar)
    # =========================================
    header_data = [[Paragraph(f"RECETA DE PRODUCCIÓN #{receta.id}", title_style)]]

    header = Table(header_data, colWidths=[doc.width])
    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PRIMARY),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))

    elements.append(header)
    elements.append(Spacer(1, 14))

    # =========================================
    # 📦 CARD DE INFORMACIÓN
    # =========================================
    info_data = [
        [
            Paragraph("<b>Producto</b>", label_style),
            Paragraph("<b>Talla</b>", label_style),
            Paragraph("<b>Color</b>", label_style),
            Paragraph("<b>Cantidad Base</b>", label_style),
        ],
        [
            Paragraph(v.producto.nombre, value_style),
            Paragraph(v.talla.nombre, value_style),
            Paragraph(v.producto.color.nombre if v.producto.color else "—", value_style),
            Paragraph(str(receta.cantidad_base), value_style),
        ]
    ]

    info_table = Table(info_data, colWidths=[doc.width/4.0]*4)

    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("BOX", (0, 0), (-1, -1), 1, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER),

        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    elements.append(info_table)
    elements.append(Spacer(1, 18))

    # =========================================
    # 📊 TABLA DE INSUMOS
    # =========================================
    data = [["Materia Prima", "Cantidad", "Unidad"]]

    for d in receta.detalles:
        data.append([
            d.materia_prima.nombre,
            f"{float(d.cantidad_neta):,.2f}",
            d.materia_prima.unidad.sigla if d.materia_prima.unidad else "—",
        ])

    table = Table(data, colWidths=[
        doc.width * 0.4,
        doc.width * 0.2,
        doc.width * 0.2,
        doc.width * 0.2,
    ])

    table.setStyle(TableStyle([
        # Header
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

        # Filas alternadas
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),

        # Bordes suaves
        ("LINEBELOW", (0, 0), (-1, 0), 1, PRIMARY),
        ("LINEBELOW", (0, 1), (-1, -1), 0.25, BORDER),

        # Padding
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    elements.append(table)

    # =========================================
    # 📄 FOOTER
    # =========================================
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        f"Generado el {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}",
        ParagraphStyle("footer", fontSize=8, textColor=MUTED, alignment=1)
    ))

    # --- Construir PDF ---
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename=receta_{receta.id}.pdf"

    return response
