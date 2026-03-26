# database/seed.py
from database.mysql import db, Usuario, Rol, Permiso
from utils.security import hash_password
from sqlalchemy.exc import IntegrityError

def seed_data():
    try:
        # =========================================
        # PERMISOS (DINÁMICO)
        # =========================================
        PERMISOS = {
            "usuarios": ["ver", "crear", "editar", "eliminar", "exportar"],
            "roles": ["ver", "crear", "editar", "eliminar", "exportar"],
            "unidad": ["ver", "crear", "editar", "eliminar", "exportar"],
            "empaque": ["ver", "crear", "editar", "eliminar", "exportar"],
            "color": ["ver", "crear", "editar", "eliminar", "exportar"],
            "proveedor": ["ver", "crear", "editar", "eliminar", "exportar"],
            "categoria": ["ver", "crear", "editar", "eliminar", "exportar"],
            "inventario": ["ver", "crear", "editar", "eliminar", "exportar"],
            "talla": ["ver", "crear", "editar", "eliminar", "exportar"],
            "cliente": ["ver", "crear", "editar", "eliminar", "exportar"],
            "recetas": ["ver", "crear", "editar", "eliminar", "exportar"],
            "materia_prima": ["ver", "crear", "editar", "eliminar", "exportar"],
            "explosion": ["ver", "crear","editar"],    
            "productosVariantes": ["buscador","productosVariantes"],
        }

        permisos_db = []

        for modulo, acciones in PERMISOS.items():
            for accion in acciones:
                permiso = Permiso.query.filter_by(modulo=modulo, accion=accion).first()
                if not permiso:
                    permiso = Permiso(modulo=modulo, accion=accion)
                    db.session.add(permiso)
                permisos_db.append(permiso)

        db.session.flush()

        # =========================================
        # ROL ADMIN
        # =========================================
        admin_role = Rol.query.filter_by(nombre="Administrador").first()
        if not admin_role:
            admin_role = Rol(
                nombre="Administrador",
                descripcion="Rol con todos los permisos del sistema"
            )
            db.session.add(admin_role)
            db.session.flush()

        # Asignar permisos
        for permiso in permisos_db:
            if permiso not in admin_role.permisos:
                admin_role.permisos.append(permiso)

        # =========================================
        # USUARIO ADMIN
        # =========================================
        admin_user = Usuario.query.filter_by(usuario="admin").first()
        if not admin_user:
            admin_user = Usuario(
                usuario="admin",
                correo="admin@example.com",
                contrasenia=hash_password("admin123"),
                activo=True
            )
            db.session.add(admin_user)
            db.session.flush()

        if admin_role not in admin_user.roles:
            admin_user.roles.append(admin_role)

        db.session.commit()
        print("✅ Base de datos poblada exitosamente.")

    except IntegrityError as e:
        db.session.rollback()
        print(f"❌ Error de integridad: {e}")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error inesperado: {e}")