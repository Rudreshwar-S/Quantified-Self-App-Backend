from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_cors import CORS
from flask_redis import FlaskRedis
from celery import Celery
from flask_mail import Mail

from .config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
redis_client = FlaskRedis(app)
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
mail = Mail(app)
CORS(app, resources={r"*": {"origins": "*"}})


from .utils import send_reminder_emails

@app.cli.command("send-reminders")
def _():
    send_reminder_emails()

from qs_app.auth.routes import auth
from qs_app.main.routes import main

app.register_blueprint(main)
app.register_blueprint(auth, url_prefix='/auth')
