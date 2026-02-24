import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    load_dotenv()
    app = Flask(__name__)

    # CORS aktivieren
    CORS(app)

    # Konfiguration laden (greift auf .env datei zurueck)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Extensions mit app verbinden
    db.init_app(app)
    migrate.init_app(app, db)

    # Blueprints registrieren
    from app.routes import main_bp, example_bp, user_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(example_bp)
    app.register_blueprint(user_bp)

    return app
