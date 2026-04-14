import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()


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
    _register_cli_commands(app)

    return app


# ---------------------------------------------------------------------------
# Private configuration helpers
# ---------------------------------------------------------------------------

def _configure_cors(app: Flask) -> None:
    CORS(
        app,
        supports_credentials=True,
        origins=os.environ.get('FRONTEND_URL', 'http://localhost:3000'),
    )


def _configure_database(app: Flask) -> None:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


def _configure_jwt(app: Flask) -> None:
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_HTTPONLY'] = True
    app.config['JWT_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
    app.config['JWT_COOKIE_SAMESITE'] = 'Lax'
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    JWTManager(app)


def _register_blueprints(app: Flask) -> None:
    from app.routes import main_bp, example_bp, user_bp, family_bp, widget_bp, admin_bp
    for bp in (main_bp, example_bp, user_bp, family_bp, widget_bp, admin_bp):
        app.register_blueprint(bp)


def _register_widgets(app: Flask) -> None:
    # Importing these packages triggers their register() calls via __init__.py side effects.
    import app.widgets.todo  # noqa: F401
    import app.widgets.weather  # noqa: F401
    import app.widgets.timetable  # noqa: F401

    from app.widgets.registry import get_all
    for widget in get_all():
        widget.register_routes(app)


def _register_cli_commands(app: Flask) -> None:
    from app.widgets.registry import sync_to_db

    @app.cli.command('sync-widgets')
    def sync_widgets_command():
        """Sync widget types to DB."""
        sync_to_db()
        _seed_system_admin()


def _seed_system_admin():
    """Create an initial system-admin account if none exists.

    Reads credentials from ADMIN_USERNAME and ADMIN_PASSWORD env vars.
    Does nothing if either variable is unset.
    """
    admin_username = os.environ.get('ADMIN_USERNAME')
    admin_password = os.environ.get('ADMIN_PASSWORD')

    if not admin_username or not admin_password:
        return

    from app.models import User
    from werkzeug.security import generate_password_hash

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
