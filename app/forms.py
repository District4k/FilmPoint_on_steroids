# app/forms.py

from flask_wtf import FlaskForm
from app.models import User
from werkzeug.security import generate_password_hash
from .extensions import db
from sqlalchemy.exc import IntegrityError
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class AuthenticationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=5,
                                                                          message='Username must be at least 5 characters long.')])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password1 = PasswordField('Password', validators=[DataRequired(), Length(min=5,
                                                                             message='Password must be at least 5 characters long.')])
    password2 = PasswordField('Confirm Password',
                              validators=[DataRequired(), EqualTo('password1', message='Passwords must match.')])

    def save(self):
        # Check if username or email already exists
        if User.query.filter_by(email=self.email.data).first():
            raise ValueError("A user with this email already exists.")
        if User.query.filter_by(username=self.username.data).first():
            raise ValueError("This username is already taken.")

        # Create and save the new user
        user = User(
            username=self.username.data,
            email=self.email.data,
            password=generate_password_hash(self.password1.data)
        )
        try:
            db.session.add(user)
            db.session.commit()
            return user
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError("An error occurred while saving the user. Please try again.") from e
