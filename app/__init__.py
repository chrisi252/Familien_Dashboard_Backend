import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()


def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__)
    _configure_cors(app)
    _configure_database(app)
    _configure_jwt(app)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    _register_blueprints(app)
    _register_widgets(app)
    _register_socketio(app)
    _register_cli_commands(app)

    return app


# ---------------------------------------------------------------------------
# Private Konfigurationshelferfunktionen
# ---------------------------------------------------------------------------

def _configure_cors(app: Flask) -> None:
    frontend_url = os.environ.get('FRONTEND_URL')
    if not frontend_url:
        raise RuntimeError('FRONTEND_URL environment variable is not set')
    CORS(
        app,
        supports_credentials=True,
        origins=frontend_url,
    )


def _configure_database(app: Flask) -> None:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


def _configure_jwt(app: Flask) -> None:
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_HTTPONLY'] = True
    app.config['JWT_COOKIE_SECURE'] = os.environ.get('PRODUCTION', '').lower() in ('1', 'true')
    app.config['JWT_COOKIE_SAMESITE'] = 'Strict'
    app.config['JWT_COOKIE_CSRF_PROTECT'] = True
    JWTManager(app)


def _register_blueprints(app: Flask) -> None:
    from app.routes import admin_bp, family_bp, main_bp, user_bp, widget_bp
    for bp in (main_bp, user_bp, family_bp, widget_bp, admin_bp):
        app.register_blueprint(bp)


def _register_widgets(flask_app: Flask) -> None:
    from app.widgets import get_widget_instances
    from app.widgets.registry import get_all, register

    for widget in get_widget_instances():
        register(widget)

    for widget in get_all():
        widget.register_routes(flask_app)


def _register_socketio(flask_app: Flask) -> None:
    from app.widgets.chat.events import register_events

    frontend_url = os.environ.get('FRONTEND_URL', '*')
    socketio.init_app(
        flask_app,
        cors_allowed_origins=frontend_url,
        async_mode='gevent',
        manage_session=False,
    )
    register_events(socketio)


def _register_cli_commands(app: Flask) -> None:
    from app.widgets.registry import sync_to_db

    @app.cli.command('sync-widgets')
    def sync_widgets_command():
        """Widget-Typen mit der Datenbank synchronisieren."""
        sync_to_db()
        _seed_system_admin()


def _seed_system_admin():
    """Legt einen initialen Systemadmin-Account an, falls noch keiner existiert.

    Liest Zugangsdaten aus den Umgebungsvariablen ADMIN_USERNAME und ADMIN_PASSWORD.
    Ist eine der Variablen nicht gesetzt, wird kein Account angelegt.
    """
    admin_username = os.environ.get('ADMIN_USERNAME')
    admin_password = os.environ.get('ADMIN_PASSWORD')

    if not admin_username or not admin_password:
        return

    from werkzeug.security import generate_password_hash

    from app.models import User

    if User.query.filter_by(username=admin_username).first():
        return

    db.session.add(User(
        username=admin_username,
        password_hash=generate_password_hash(admin_password),
        first_name='System',
        last_name='Admin',
        is_system_admin=True,
    ))
    db.session.commit()
