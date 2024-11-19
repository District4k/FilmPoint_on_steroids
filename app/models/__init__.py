from flask_sqlalchemy import SQLAlchemy
from .user import *
from ..extensions import db

# Initialize the database
db = SQLAlchemy()



