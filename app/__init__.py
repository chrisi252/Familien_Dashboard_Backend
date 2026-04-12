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

    CORS(app, supports_credentials=True, origins=os.environ.get('FRONTEND_URL', 'http://localhost:3000'))

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_HTTPONLY'] = True
    app.config['JWT_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
    app.config['JWT_COOKIE_SAMESITE'] = 'Lax'
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    jwt = JWTManager(app)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import (
        main_bp,
        example_bp,
        user_bp,
        family_bp,
        widget_bp,
        admin_bp,
    )
    app.register_blueprint(main_bp)
    app.register_blueprint(example_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(family_bp)
    app.register_blueprint(widget_bp)
    app.register_blueprint(admin_bp)

    import app.widgets.todo as _todo_widget
    import app.widgets.weather as _weather_widget
    import app.widgets.timetable as _timetable_widget


    from app.widgets.registry import get_all, sync_to_db
    for widget in get_all():
        widget.register_routes(app)

    with app.app_context():
        sync_to_db()
        _seed_system_admin()

    return app


def _seed_system_admin():
    """Legt einen initialen Systemadmin-Account an, falls noch keiner existiert.
    Credentials werden aus den Umgebungsvariablen ADMIN_USERNAME und ADMIN_PASSWORD gelesen.
    Sind diese nicht gesetzt, wird kein Account angelegt.
    """
    admin_username = os.environ.get('ADMIN_USERNAME')
    admin_password = os.environ.get('ADMIN_PASSWORD')

    if not admin_username or not admin_password:
        return

    from app.models import User
    from werkzeug.security import generate_password_hash

    if User.query.filter_by(username=admin_username).first():
        return

    admin = User(
        username=admin_username,
        password_hash=generate_password_hash(admin_password),
        first_name='System',
        last_name='Admin',
        is_system_admin=True,
    )
    db.session.add(admin)
    db.session.commit()
