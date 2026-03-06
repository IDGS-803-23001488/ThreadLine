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