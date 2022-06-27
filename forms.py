from flask_wtf import FlaskForm
from wtforms import StringField,SelectField,SubmitField,BooleanField,PasswordField
from wtforms.validators import DataRequired,Email,Length,EqualTo

class LoginForm(FlaskForm):
    email = StringField("Email: " , validators=[Email()])
    psw = PasswordField("Password: " , validators=[DataRequired(), Length(max=100,min=4)])
    remember = BooleanField("Remember", default=False)
    submit = SubmitField("Enter")

class RegistarationForm(FlaskForm):
    name = StringField("Name: ", validators=[Length(max=100, min=4)])
    email = StringField("Email: " , validators=[Email()])
    psw = PasswordField("Password: " , validators=[DataRequired(), Length(max=100,min=4)])
    psw2 = PasswordField("Password again: ", validators=[DataRequired(),EqualTo("psw",message="Passwords should be matched")])
    submit = SubmitField("Registration")