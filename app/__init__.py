# app/__init__.py
from flask import Flask
from .models import User
from .routes import main
from .api import api
from .extensions import db, login_manager, migrate  # Import from extensions


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register Blueprints
    app.register_blueprint(main)
    app.register_blueprint(api, url_prefix='/api')

    return app  # Return the app at the end of the function


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
