import os
from flask import Flask
from flask_cors import CORS
from .extensions import db
from .routes import main_bp

def create_app():
    app = Flask(__name__)
    
    # CORS aktivieren 
    CORS(app)
    
    # konfiguration laden (greift auf .env datei zurück)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # extensions mit app verbinden
    db.init_app(app)
    
    # blueprints (routen) registrieren
    app.register_blueprint(main_bp)
    
    return app