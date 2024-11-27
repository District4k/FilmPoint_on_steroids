# film_point/forms.py
from .models import User
from werkzeug.security import generate_password_hash
from .extensions import db
from sqlalchemy.exc import IntegrityError
from wtforms import StringField, PasswordField, EmailField, HiddenField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask import current_app, url_for
from flask_mail import Message
import jwt
from datetime import datetime, timedelta
from flask_wtf import FlaskForm
from wtforms.widgets import HiddenInput


class AddToWatchlistForm(FlaskForm):
    name = IntegerField(widget=HiddenInput())


class SurveyForm(FlaskForm):
    csrf_token = HiddenField()


class ResetPasswordForm(FlaskForm):
    password1 = PasswordField('New Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm New Password',
                              validators=[DataRequired(), EqualTo('password1', message='Passwords must match.')])


class ForgotPasswordForm(FlaskForm):
    email = EmailField('Email',
                       validators=[DataRequired(), Email()])


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


def generate_token(user, secret_key):
    expiration = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
    token = jwt.encode({'user_id': user.id, 'exp': expiration}, secret_key, algorithm='HS256')
    return token


def verify_token(token):
    try:
        secret_key = current_app.config['SECRET_KEY']
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        user_id = payload["user_id"]
        return user_id
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None  # Token is invalid


def send_reset_email(user, token, mail):
    reset_url = url_for('main.reset_password', token=token, _external=True)
    msg = Message('Password Reset Request', sender='film_point@artify.ee', recipients=[user.email])
    msg.body = f'Click the link to reset your password: {reset_url}'
    mail.send(msg)


def send_confirm_email(user, token, mail):
    confirm_url = url_for('main.confirm_email', token=token, _external=True)
    msg = Message('Account confirmation', sender='film_point@artify.ee', recipients=[user.email])
    msg.body = f'Click the link to confirm account: {confirm_url}'
    mail.send(msg)
