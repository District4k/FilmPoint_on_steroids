from flask import Flask
from .models import db
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)

    # Register Blueprints
    from .routes import main
    app.register_blueprint(main)

    return app
