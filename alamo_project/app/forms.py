from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired


class LoginForm(Form):
    # DataRequired ensures the field is not empty
    email = StringField('email', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])
