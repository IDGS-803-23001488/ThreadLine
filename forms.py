# forms.py
from wtforms import Form
from wtforms import StringField,TextAreaField, IntegerField, PasswordField
from wtforms import EmailField
from wtforms import validators

class UserForm(Form):
    id = IntegerField('id')
    usuario = StringField('Usuario', [validators.DataRequired()])
    correo = EmailField('Correo', [validators.DataRequired()])
    contrasenia = PasswordField('Contraseña', [validators.DataRequired()])
    
class RolForm(Form):
    nombre = StringField(
        "Nombre",
        [validators.DataRequired(), validators.Length(max=50)]
    )
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
    unidad_id = StringField('Unidad', [validators.DataRequired()])
    cantidad = IntegerField('Cantidad', [validators.DataRequired()])