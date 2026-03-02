# models.py
import datetime
import uuid
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# =====================================================
# TABLAS INTERMEDIAS (DEBEN IR PRIMERO)
# =====================================================

usuario_rol = db.Table(
    "usuario_rol",
    db.Column("usuario_id", db.Integer, db.ForeignKey("usuario.id"), primary_key=True),
    db.Column("rol_id", db.Integer, db.ForeignKey("rol.id"), primary_key=True)
)

rol_permiso = db.Table(
    "rol_permiso",
    db.Column("rol_id", db.Integer, db.ForeignKey("rol.id"), primary_key=True),
    db.Column("permiso_id", db.Integer, db.ForeignKey("permiso.id"), primary_key=True)
)

# =====================================================
# MODELO USUARIO
# =====================================================

class Usuario(db.Model):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)

    # Datos principales
    usuario = db.Column(db.String(50), nullable=False, unique=True)
    correo = db.Column(db.String(100), nullable=False, unique=True)
    contrasenia = db.Column(db.String(255), nullable=False)

    # ==========================
    # RELACIONES RBAC (Rol-Based Access Control)
    # ==========================
    roles = db.relationship(
        "Rol",
        secondary=usuario_rol,
        backref="usuarios"
    )

    # ==========================
    # CONTROL DE AUDITORÍA
    # ==========================
    fecha_creacion = db.Column(
        db.DateTime,
        default=datetime.datetime.utcnow
    )

    fecha_edicion = db.Column(
        db.DateTime,
        onupdate=datetime.datetime.utcnow
    )

    fecha_eliminacion = db.Column(
        db.DateTime,
        nullable=True
    )

    creado_por = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id"),
        nullable=True
    )

    editado_por = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id"),
        nullable=True
    )

    eliminado_por = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id"),
        nullable=True
    )

    # Relaciones autorreferenciadas
    creador = db.relationship(
        "Usuario",
        remote_side=[id],
        foreign_keys=[creado_por],
        post_update=True
    )

    editor = db.relationship(
        "Usuario",
        remote_side=[id],
        foreign_keys=[editado_por],
        post_update=True
    )

    eliminador = db.relationship(
        "Usuario",
        remote_side=[id],
        foreign_keys=[eliminado_por],
        post_update=True
    )

    # Soft delete
    activo = db.Column(db.Boolean, default=True)

    # ==========================
    # MÉTODO DE PERMISOS
    # ==========================
    def tiene_permiso(self, modulo, accion):
        for rol in self.roles:
            for permiso in rol.permisos:
                if permiso.modulo == modulo and permiso.accion == accion:
                    return True
        return False

    def __repr__(self):
        return f"<Usuario {self.usuario}>"

# =====================================================
# MODELO ROL
# =====================================================

class Rol(db.Model):
    __tablename__ = "rol"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.String(255))

    permisos = db.relationship(
        "Permiso",
        secondary=rol_permiso,
        backref="roles"
    )

    def __repr__(self):
        return f"<Rol {self.nombre}>"

# =====================================================
# MODELO PERMISO
# =====================================================

class Permiso(db.Model):
    __tablename__ = "permiso"

    id = db.Column(db.Integer, primary_key=True)

    modulo = db.Column(db.String(50), nullable=False)
    accion = db.Column(db.String(50), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("modulo", "accion", name="uq_modulo_accion"),
    )

    def __repr__(self):
        return f"<Permiso {self.modulo}/{self.accion}>"

# =====================================================
# MODELO TOKEN
# =====================================================

class Token(db.Model):
    __tablename__ = "token"

    id = db.Column(db.Integer, primary_key=True)

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id"),
        nullable=False
    )

    token = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4())
    )

    # login, recuperacion, verificacion, api
    tipo = db.Column(
        db.String(50),
        nullable=False
    )

    fecha_creacion = db.Column(
        db.DateTime,
        default=datetime.datetime.utcnow
    )

    fecha_expiracion = db.Column(
        db.DateTime,
        nullable=False
    )

    usado = db.Column(
        db.Boolean,
        default=False
    )

    usuario = db.relationship("Usuario", backref="tokens")

    def esta_expirado(self):
        return datetime.datetime.utcnow() > self.fecha_expiracion

    def __repr__(self):
        return f"<Token {self.tipo} - {self.usuario_id}>"
