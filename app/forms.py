# app/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo
from app.models import User
from werkzeug.security import generate_password_hash
from .extensions import db


class AuthenticationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password1 = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password',
                              validators=[DataRequired(), EqualTo('password1', message='Passwords must match.')])

    def save(self):
        user = User(
            username=self.username.data,
            email=self.email.data,
            password=generate_password_hash(self.password1.data)
        )
        db.session.add(user)
        db.session.commit()
        return user
