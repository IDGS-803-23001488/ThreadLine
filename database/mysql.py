import datetime
import uuid
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

BASE_ARGS = {
    'mysql_engine': 'InnoDB',
    'mysql_charset': 'utf8mb4',
    'mysql_collate': 'utf8mb4_unicode_ci'
}

class BaseModel(db.Model):
    __abstract__ = True
    __table_args__ = BASE_ARGS

# =====================================================
# TABLAS INTERMEDIAS (RBAC)
# =====================================================

usuario_rol = db.Table(
    "usuario_rol",
    db.Column("usuario_id", db.Integer, db.ForeignKey("usuario.id"), primary_key=True),
    db.Column("rol_id", db.Integer, db.ForeignKey("rol.id"), primary_key=True),
    **BASE_ARGS
)

rol_permiso = db.Table(
    "rol_permiso",
    db.Column("rol_id", db.Integer, db.ForeignKey("rol.id"), primary_key=True),
    db.Column("permiso_id", db.Integer, db.ForeignKey("permiso.id"), primary_key=True),
    **BASE_ARGS
)

# =====================================================
# SISTEMA DE USUARIOS Y ACCESO
# =====================================================

class Usuario(BaseModel):
    __tablename__ = "usuario"
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), nullable=False, unique=True)
    correo = db.Column(db.String(100), nullable=False, unique=True)
    contrasenia = db.Column(db.String(255), nullable=False)
    
    roles = db.relationship("Rol", secondary=usuario_rol, backref="usuarios")
    
    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    fecha_edicion = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    fecha_eliminacion = db.Column(db.DateTime, nullable=True)
    creado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    editado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    eliminado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    activo = db.Column(db.Boolean, default=True)

    def tiene_permiso(self, modulo, accion):
        for rol in self.roles:
            if not rol.activo: continue
            for permiso in rol.permisos:
                if permiso.modulo == modulo and permiso.accion == accion:
                    return True
        return False

class Rol(BaseModel):
    __tablename__ = "rol"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.String(255))
    permisos = db.relationship("Permiso", secondary=rol_permiso, backref="roles")
    activo = db.Column(db.Boolean, default=True)

    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    fecha_edicion = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    fecha_eliminacion = db.Column(db.DateTime, nullable=True)
    creado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    editado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    eliminado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    activo = db.Column(db.Boolean, default=True)

class Permiso(BaseModel):
    __tablename__ = "permiso"
    id = db.Column(db.Integer, primary_key=True)
    modulo = db.Column(db.String(50), nullable=False)
    accion = db.Column(db.String(50), nullable=False)
    __table_args__ = (db.UniqueConstraint("modulo", "accion", name="uq_modulo_accion"),BASE_ARGS)

class Token(BaseModel):
    __tablename__ = "token"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    token = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    tipo = db.Column(db.String(50), nullable=False) # login, recovery, etc
    fecha_expiracion = db.Column(db.DateTime, nullable=False)
    usado = db.Column(db.Boolean, default=False)
    
    usuario = db.relationship("Usuario", backref="tokens")
    def esta_expirado(self):
        return datetime.datetime.utcnow() > self.fecha_expiracion

    def __repr__(self):
        return f"<Token {self.tipo} - {self.usuario_id}>"

# =====================================================
# CATÁLOGOS BASE (INVENTARIO Y VENTAS)
# =====================================================

class Unidad(BaseModel):
    __tablename__ = "unidad"
    id = db.Column(db.Integer, primary_key=True)
    unidad = db.Column(db.String(50), nullable=False)
    sigla = db.Column(db.String(10), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    
    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    fecha_edicion = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    fecha_eliminacion = db.Column(db.DateTime, nullable=True)
    creado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    editado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    eliminado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    activo = db.Column(db.Boolean, default=True)

class Empaque(BaseModel):
    __tablename__ = "empaque"
    id = db.Column(db.Integer, primary_key=True)
    paquete = db.Column(db.String(50), nullable=False)
    unidad_id = db.Column(db.Integer, db.ForeignKey("unidad.id"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    
    unidad = db.relationship("Unidad", backref="empaques")
    
    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    fecha_edicion = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    fecha_eliminacion = db.Column(db.DateTime, nullable=True)
    creado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    editado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    eliminado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    activo = db.Column(db.Boolean, default=True)

class Color(BaseModel):
    __tablename__ = "color"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    hex = db.Column(db.String(7))
    activo = db.Column(db.Boolean, default=True)
    
    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    fecha_edicion = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    fecha_eliminacion = db.Column(db.DateTime, nullable=True)
    creado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    editado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    eliminado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    activo = db.Column(db.Boolean, default=True)

class Talla(BaseModel):
    __tablename__ = "talla"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), nullable=False)
    orden = db.Column(db.Integer, default=0)
    activo = db.Column(db.Boolean, default=True)

    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    fecha_edicion = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    fecha_eliminacion = db.Column(db.DateTime, nullable=True)
    creado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    editado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    eliminado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    activo = db.Column(db.Boolean, default=True)

class Categoria(BaseModel):
    __tablename__ = "categoria"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255))
    activo = db.Column(db.Boolean, default=True)

    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    fecha_edicion = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    fecha_eliminacion = db.Column(db.DateTime, nullable=True)
    creado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    editado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    eliminado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    activo = db.Column(db.Boolean, default=True)

# =====================================================
# CORE DE PRODUCTOS Y MATERIA PRIMA
# =====================================================

class Articulo(BaseModel):
    __tablename__ = "articulo"
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.Enum('PRODUCTO', 'MATERIA_PRIMA'), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    fecha_edicion = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    fecha_eliminacion = db.Column(db.DateTime, nullable=True)
    creado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    editado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    eliminado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    activo = db.Column(db.Boolean, default=True)

class Proveedor(BaseModel):
    __tablename__ = "proveedor"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    rfc = db.Column(db.String(20))
    correo = db.Column(db.String(100))
    activo = db.Column(db.Boolean, default=True)

    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    fecha_edicion = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    fecha_eliminacion = db.Column(db.DateTime, nullable=True)
    creado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    editado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    eliminado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    activo = db.Column(db.Boolean, default=True)

class MateriaPrima(BaseModel):
    __tablename__ = "materia_prima"
    id = db.Column(db.Integer, primary_key=True)
    articulo_id = db.Column(db.Integer, db.ForeignKey("articulo.id"), unique=True)
    nombre = db.Column(db.String(100), nullable=False)
    unidad_id = db.Column(db.Integer, db.ForeignKey("unidad.id"), nullable=False)
    empaque_id = db.Column(db.Integer, db.ForeignKey("empaque.id"))
    proveedor_id = db.Column(db.Integer, db.ForeignKey("proveedor.id"))
    porcentaje_merma = db.Column(db.Numeric(5, 2), default=0.00)
    stock_minimo = db.Column(db.Numeric(10, 4), default=0.0000)
    activo = db.Column(db.Boolean, default=True)

    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    fecha_edicion = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    fecha_eliminacion = db.Column(db.DateTime, nullable=True)
    creado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    editado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    eliminado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    activo = db.Column(db.Boolean, default=True)

class Producto(BaseModel):
    __tablename__ = "producto"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categoria.id"))
    descripcion = db.Column(db.Text)
    imagen = db.Column(db.String(255))
    activo = db.Column(db.Boolean, default=True)

    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    fecha_edicion = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    fecha_eliminacion = db.Column(db.DateTime, nullable=True)
    creado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    editado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    eliminado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    activo = db.Column(db.Boolean, default=True)

class ProductoVariante(BaseModel):
    __tablename__ = "producto_variante"
    id = db.Column(db.Integer, primary_key=True)
    articulo_id = db.Column(db.Integer, db.ForeignKey("articulo.id"))
    producto_id = db.Column(db.Integer, db.ForeignKey("producto.id"), nullable=False)
    talla_id = db.Column(db.Integer, db.ForeignKey("talla.id"), nullable=False)
    color_id = db.Column(db.Integer, db.ForeignKey("color.id"), nullable=False)
    precio_venta = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)

    producto = db.relationship("Producto", backref="variantes")
    talla = db.relationship("Talla")
    color = db.relationship("Color")
    articulo = db.relationship("Articulo")

    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    fecha_edicion = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    fecha_eliminacion = db.Column(db.DateTime, nullable=True)
    creado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    editado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    eliminado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    activo = db.Column(db.Boolean, default=True)    

    __table_args__ = (db.UniqueConstraint('producto_id', 'talla_id', 'color_id', name='uq_variante'),BASE_ARGS)

# =====================================================
# PRODUCCIÓN (RECETAS Y ÓRDENES)
# =====================================================

class Receta(BaseModel):
    __tablename__ = "receta"
    id = db.Column(db.Integer, primary_key=True)
    producto_variante_id = db.Column(db.Integer, db.ForeignKey("producto_variante.id"), nullable=False)
    cantidad_base = db.Column(db.Integer, default=1)
    activo = db.Column(db.Boolean, default=True)

    producto_variante = db.relationship("ProductoVariante", backref="recetas")
    
    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    fecha_edicion = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    fecha_eliminacion = db.Column(db.DateTime, nullable=True)
    creado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    editado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    eliminado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    activo = db.Column(db.Boolean, default=True)

class RecetaDetalle(BaseModel):
    __tablename__ = "receta_detalle"
    id = db.Column(db.Integer, primary_key=True)
    articulo_id = db.Column(db.Integer, db.ForeignKey("articulo.id"), nullable=False)
    materia_prima_id = db.Column(db.Integer, db.ForeignKey("materia_prima.id"), nullable=False)
    cantidad_neta = db.Column(db.Numeric(10, 4), nullable=False)
    cantidad_con_merma = db.Column(db.Numeric(10, 4), nullable=False)

class OrdenProduccion(BaseModel):
    __tablename__ = "orden_produccion"
    id = db.Column(db.Integer, primary_key=True)
    receta_id = db.Column(db.Integer, db.ForeignKey("receta.id"), nullable=False)
    cantidad_solicitada = db.Column(db.Integer, nullable=False)
    cantidad_producida = db.Column(db.Integer, default=0)
    estatus = db.Column(db.String(30), default='pendiente')
    fecha_inicio = db.Column(db.DateTime)
    fecha_fin = db.Column(db.DateTime)

# =====================================================
# E-COMMERCE (CLIENTES, CARRITO, PEDIDOS)
# =====================================================

class Cliente(BaseModel):
    __tablename__ = "cliente"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contrasenia = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(255))
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    fecha_edicion = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    fecha_eliminacion = db.Column(db.DateTime, nullable=True)
    creado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    editado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    eliminado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    activo = db.Column(db.Boolean, default=True)

class Carrito(BaseModel):
    __tablename__ = "carrito"
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("cliente.id"), nullable=False)
    activo = db.Column(db.Boolean, default=True)

class CarritoDetalle(BaseModel):
    __tablename__ = "carrito_detalle"
    id = db.Column(db.Integer, primary_key=True)
    carrito_id = db.Column(db.Integer, db.ForeignKey("carrito.id"), nullable=False)
    producto_variante_id = db.Column(db.Integer, db.ForeignKey("producto_variante.id"), nullable=False)
    cantidad = db.Column(db.Integer, default=1)

class Pedido(BaseModel):
    __tablename__ = "pedido"
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("cliente.id"), nullable=False)
    folio = db.Column(db.String(20), unique=True, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    subtotal = db.Column(db.Numeric(12, 2), default=0.00)
    costo_envio = db.Column(db.Numeric(10, 2), default=0.00)
    total = db.Column(db.Numeric(12, 2), default=0.00)
    estatus = db.Column(db.String(30), default='pendiente')
    direccion_envio = db.Column(db.String(255))

class PedidoDetalle(BaseModel):
    __tablename__ = "pedido_detalle"
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedido.id"), nullable=False)
    producto_variante_id = db.Column(db.Integer, db.ForeignKey("producto_variante.id"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)

# =====================================================
# MOVIMIENTOS E INVENTARIO
# =====================================================

class Inventario(BaseModel):
    __tablename__ = "inventarios"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)

    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    fecha_edicion = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    fecha_eliminacion = db.Column(db.DateTime, nullable=True)
    creado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    editado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    eliminado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    activo = db.Column(db.Boolean, default=True)

class TipoMovimiento(BaseModel):
    __tablename__ = "tipo_movimientos"
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(100), nullable=False)
    signo = db.Column(db.Integer, nullable=False) # 1 o -1

    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    fecha_edicion = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    fecha_eliminacion = db.Column(db.DateTime, nullable=True)
    creado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    editado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    eliminado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    activo = db.Column(db.Boolean, default=True)

class MovimientoInventario(BaseModel):
    __tablename__ = "movimientos_inventario"
    id = db.Column(db.Integer, primary_key=True)
    articulo_id = db.Column(db.Integer, db.ForeignKey("articulo.id"), nullable=False)
    tipo_mov_id = db.Column(db.Integer, db.ForeignKey("tipo_movimientos.id"), nullable=False)
    inv_id = db.Column(db.Integer, db.ForeignKey("inventarios.id"), nullable=False)
    cantidad = db.Column(db.Numeric(10, 2), nullable=False)
    unidad_id = db.Column(db.Integer, db.ForeignKey("unidad.id"))
    empaque_id = db.Column(db.Integer, db.ForeignKey("empaque.id"))
    signo = db.Column(db.Integer, nullable=False)
    existencia = db.Column(db.Numeric(10, 2))

# =====================================================
# MODELO COMPRA
# =====================================================
class Compra(BaseModel):
    __tablename__ = "compra"

    id = db.Column(db.Integer, primary_key=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey("proveedor.id"), nullable=False)
    
    fecha = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    total = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    estatus = db.Column(db.String(30), nullable=False, default='pendiente')
    observaciones = db.Column(db.Text)

    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    fecha_edicion = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    creado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    editado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"))

    # Relaciones
    proveedor = db.relationship("Proveedor", backref="compras")
    detalles = db.relationship("CompraDetalle", backref="compra", cascade="all, delete-orphan")

# =====================================================
# MODELO COMPRA DETALLE
# =====================================================
class CompraDetalle(BaseModel):
    __tablename__ = "compra_detalle"

    id = db.Column(db.Integer, primary_key=True)
    compra_id = db.Column(db.Integer, db.ForeignKey("compra.id"), nullable=False)
    materia_prima_id = db.Column(db.Integer, db.ForeignKey("materia_prima.id"), nullable=False)
    
    cantidad_empaque = db.Column(db.Numeric(10, 4), nullable=False)
    cantidad_unidad = db.Column(db.Numeric(10, 4), nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)

    materia_prima = db.relationship("MateriaPrima")

# =====================================================
# MODELO PAGO
# =====================================================
class Pago(BaseModel):
    __tablename__ = "pago"

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedido.id"), nullable=False)
    
    metodo = db.Column(db.String(50), nullable=False, default='simulado')
    referencia = db.Column(db.String(100))
    monto = db.Column(db.Numeric(12, 2), nullable=False)
    estatus = db.Column(db.String(30), nullable=False, default='pendiente')
    fecha = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    pedido = db.relationship("Pedido", backref=db.backref("pagos", lazy=True))

# =====================================================
# MODELO RESEÑA
# =====================================================
class Resenia(BaseModel):
    __tablename__ = "resenia"

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("cliente.id"), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey("producto.id"), nullable=False)
    
    calificacion = db.Column(db.SmallInteger, nullable=False) # Check 1 a 5
    comentario = db.Column(db.Text)
    verificada = db.Column(db.Boolean, default=False)
    fecha = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        db.CheckConstraint('calificacion >= 1 AND calificacion <= 5', name='resenia_chk_1'),
        BASE_ARGS
    )

    cliente = db.relationship("Cliente", backref="resenias")
    producto = db.relationship("Producto", backref="resenias")

# =====================================================
# MODELO SOLICITUD PRODUCCIÓN
# =====================================================
class SolicitudProduccion(BaseModel):
    __tablename__ = "solicitud_produccion"

    id = db.Column(db.Integer, primary_key=True)
    producto_variante_id = db.Column(db.Integer, db.ForeignKey("producto_variante.id"), nullable=False)
    
    cantidad = db.Column(db.Integer, nullable=False)
    estatus = db.Column(db.String(30), nullable=False, default='pendiente')
    observaciones = db.Column(db.Text)
    
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    fecha_edicion = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    
    solicitado_por = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    atendido_por = db.Column(db.Integer, db.ForeignKey("usuario.id"))

    # Relaciones
    variante = db.relationship("ProductoVariante", backref="solicitudes")
    solicitante = db.relationship("Usuario", foreign_keys=[solicitado_por])
    encargado = db.relationship("Usuario", foreign_keys=[atendido_por])