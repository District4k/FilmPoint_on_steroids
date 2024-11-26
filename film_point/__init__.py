from flask import Flask
from .models import User, SurveyQuestion
from .routes import main
from .api import api
from .extensions import db, login_manager, migrate
from flask_mail import Mail


# Create the Flask application
def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')  # Load configuration

    # Initialize the mail extension
    mail = Mail(app)  # Instantiate the Mail object here
    app.mail = mail
    # Initialize extensions
    db.init_app(app)
    print(db.session.query)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register Blueprints
    app.register_blueprint(main)
    app.register_blueprint(api, url_prefix='/api')

    return app  # Return the film_point at the end of the function


# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
