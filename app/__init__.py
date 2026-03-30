import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    load_dotenv()
    app = Flask(__name__)

    # CORS — credentials (cookies) erfordern eine explizite Origin, kein Wildcard
    CORS(app, supports_credentials=True, origins=os.environ.get('FRONTEND_URL', 'http://localhost:3000'))

    # Konfiguration laden (greift auf .env datei zurueck)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # JWT Konfiguration
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_HTTPONLY'] = True
    app.config['JWT_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
    app.config['JWT_COOKIE_SAMESITE'] = 'Lax'
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # kein separates CSRF-Token nötig
    jwt = JWTManager(app)

    # Extensions mit app verbinden
    db.init_app(app)
    migrate.init_app(app, db)

    # Blueprints registrieren
    from app.routes import (
        main_bp,
        example_bp,
        user_bp,
        family_bp,
        calendar_bp,
        weather_bp,
        widget_bp,
    )
    app.register_blueprint(main_bp)
    app.register_blueprint(example_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(family_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(widget_bp)

    return app
