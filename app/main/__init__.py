from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

from .config import Config

db = SQLAlchemy()
flask_bcrypt = Bcrypt()
migrate = Migrate()

from .model import user

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    flask_bcrypt.init_app(app)
    migrate.init_app(app, db)

    return app