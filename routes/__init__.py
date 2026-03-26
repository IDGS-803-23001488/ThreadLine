# routes/__init__.py
from .main import main
from .usuarios import usuarios
from .auth import auth
from .roles import roles
from .unidad import unidad
from .empaque import empaque
from .color import color
from .proveedores import proveedor
from .categoria import categoria
from .inventario import inventario
from .talla import talla
from .cliente import cliente
from .recetas import recetas, apiRecetas
from .productosVariantes import productosVariantes, apiProductosVariantes
from .materiaPrima import materia_prima
from .explosion_materiales.explosion import explosion
from .explosion_materiales.api_explosion import apiExplosion

all_blueprints = [
    main,
    usuarios,
    auth,
    roles,
    unidad,
    empaque,
    color,
    proveedor,
    categoria,
    inventario,
    talla,
    cliente,
    recetas,
    apiRecetas,
    productosVariantes,
    materia_prima,
    explosion,
    
    apiExplosion,
    apiProductosVariantes
]

def register_blueprints(app):
    for blueprint in all_blueprints:
        app.register_blueprint(blueprint)
