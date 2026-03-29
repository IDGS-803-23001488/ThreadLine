# forms.py
from wtforms import Form
from wtforms import StringField,TextAreaField, IntegerField, PasswordField, EmailField, BooleanField, SelectField, HiddenField, DecimalField
from wtforms import validators

class UserForm(Form):
    id = IntegerField('id')
    usuario = StringField('Usuario', [validators.DataRequired()])
    correo = EmailField('Correo', [validators.DataRequired()])
    rol = SelectField(
        "Rol",
        coerce=int,
        validators=[validators.DataRequired()]
    )
    cambiar_contrasenia = BooleanField("Cambiar contraseña")
    contrasenia = PasswordField('Contraseña',[validators.Optional(), validators.Length(min=8, max=128)])

class RolForm(Form):
    nombre = StringField("Nombre",[validators.DataRequired(), validators.Length(max=50)])
    descripcion = TextAreaField("Descripción",[validators.Optional(), validators.Length(max=255)])
    descripcion = TextAreaField(
        "Descripción",
        [validators.Optional(), validators.Length(max=255)]
    )

class UnidadForm(Form):
    id = IntegerField('id')
    unidad = StringField('Unidad', [validators.DataRequired()])
    sigla = StringField('Sigla', [validators.DataRequired()])
    cantidad = IntegerField('Cantidad', [validators.DataRequired()])

class EmpaqueForm(Form):
    id = IntegerField('id')
    paquete = StringField('Paquete', [validators.DataRequired()])
    unidad_id = SelectField(
        "Unidad",
        coerce=int,
        validators=[validators.DataRequired()]
    )
    cantidad = IntegerField('Cantidad', [validators.DataRequired()])

#Formulario de Color 
class ColorForm(Form):
    id = IntegerField('id')
    nombre = StringField('Nombre',[validators.DataRequired("Coloca el nombre del color"), validators.length(min=3 , max=50)])
    hex = StringField('Codigo Hexadecimal', [validators.optional(),validators.length(min=7, max=7)])
    
class CategoriaForm(Form):
    id = IntegerField('id')
    nombre = StringField('Nombre',[validators.DataRequired("Coloca el nombre de la categoria"), validators.length(min=3 , max=100)])
    descripcion = StringField('Descripcion', [validators.optional(),validators.length(min=3, max=255)])
    
class InventarioForm(Form):
    id = IntegerField('id')
    nombre = StringField('Nombre',[validators.DataRequired("Coloca el nombre del inventario"), validators.length(min=3 , max=50)])
    tipo = SelectField ("Tipo", choices=[(0 ,'Materia Prima'),(1,'Producto Terminado')], coerce=int)

class TallaForm(Form):
    id = IntegerField('id')
    nombre = StringField('Nombre',[validators.DataRequired("Coloca el nombre de la Talla"), validators.length(min=3 , max=20)])
    orden = IntegerField('Orden', [validators.DataRequired("Coloca la orden de la Talla"),validators.number_range(min = 1)])
    
class ClienteForm(Form):
    nombre = StringField('Nombre', [validators.DataRequired(message="El nombre es obligatorio"),validators.Length(min=3, max=100)])
    correo = StringField('Correo electrónico', [validators.DataRequired(message="El correo es obligatorio"),validators.Email(message="Ingresa un correo válido"),validators.Length(max=100)])
    contrasenia = PasswordField('Contraseña', [validators.DataRequired(message="La contraseña es obligatoria"),validators.Length(min=6, message="Debe tener al menos 6 caracteres")])
    telefono = StringField('Teléfono', [validators.Optional(),validators.Regexp(r'^[0-9]+$', message="El teléfono solo debe contener números"),validators.Length(min=10, max=10, message="El teléfono debe tener exactamente 10 caracteres")])
    cambiar_contrasenia = BooleanField("Cambiar contraseña")
    direccion = StringField('Dirección', [validators.Optional(), validators.Length(max=255)])


class ProveedorForm(Form):
    id = IntegerField('id')
    nombre = StringField('Nombre', [validators.DataRequired()])
    rfc = StringField('RFC', [validators.DataRequired(),validators.length(min=12, max=13)])
    correo = EmailField('Correo', [validators.DataRequired()])


class RecetaForm(Form):
    id = IntegerField('id')
    producto_variante_id = HiddenField(
        validators=[validators.DataRequired()]
    )
    cantidad_base = IntegerField(
        'Cantidad', 
        [
            validators.DataRequired("Coloca la cantidad del producto"),
            validators.number_range(min = 1)
        ]
    )
    
class MateriaPrimaForm(Form):
    id = IntegerField('id')
    nombre = StringField('Nombre',[validators.DataRequired()])
    unidad_id = SelectField('Unidad',[validators.DataRequired()])
    empaque_id = SelectField('Empaque')
    proveedor_id = SelectField('Proveedor')
    stock_minimo = DecimalField('Stock mínimo',[validators.Optional(),validators.DataRequired("Coloca el maximo de stock"),validators.number_range(min=0,max=200)])
    stock_maximo = DecimalField('Stock máximo',[validators.Optional(), validators.DataRequired("Coloca el maximo de stock"), validators.number_range(min=0, max=200)])

class ProductoForm(Form):
    id = IntegerField('id')

    nombre = StringField(
        'Nombre',
        [validators.DataRequired(), validators.Length(min=3, max=100)]
    )

    categoria_id = SelectField(
        "Categoría",
        coerce=int,
        validators=[validators.DataRequired()]
    )

    color_id = SelectField(
        "Color",
        coerce=int,
        validators=[validators.DataRequired()]
    )

    descripcion = TextAreaField(
        'Descripción',
        [validators.Optional(), validators.Length(max=255)]
    )

class ProductoVarianteForm(Form):
    id = IntegerField('id')

    producto_id = SelectField(
        "Producto",
        coerce=int,
        validators=[validators.DataRequired()]
    )

    talla_id = SelectField(
        "Talla",
        coerce=int,
        validators=[validators.DataRequired()]
    )

    precio_venta = DecimalField(
        "Precio",
        [
            validators.DataRequired(),
            validators.NumberRange(min=0)
        ]
    )