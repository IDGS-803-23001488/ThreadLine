# forms.py
from wtforms import Form
from wtforms import StringField,TextAreaField, IntegerField, PasswordField, EmailField, BooleanField, SelectField
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
    hex = StringField('Codigo Hexadecimal'), [validators.optional(),validators.length(min=7, max=7)]
    
    