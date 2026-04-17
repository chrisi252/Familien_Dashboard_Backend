"""Shared test fixtures"""
import os

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app import db as _db
from app.models import (
    Family,
    FamilyWidget,
    Role,
    User,
    UserFamilyRole,
    WidgetType,
    WidgetUserPermission,
)
from app.widgets.registry import sync_to_db


def create_app_for_testing():
    os.environ.setdefault('FRONTEND_URL', 'http://localhost:3000')
    app = create_app(test_config={
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret',
        'JWT_COOKIE_CSRF_PROTECT': False,
    })
    return app


@pytest.fixture(scope='session')
def app():
    application = create_app_for_testing()
    with application.app_context():
        _db.create_all()
        sync_to_db()
        _seed_roles()
        yield application
        _db.drop_all()


@pytest.fixture(autouse=True)
def db_transaction(app):
    """Clear all non-seed data after each test."""
    with app.app_context():
        yield _db
        _db.session.rollback()
        for table in reversed(_db.metadata.sorted_tables):
            if table.name not in ('roles', 'widget_types'):
                _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture
def client(app):
    return app.test_client()


# ---------------------------------------------------------------------------
# Helpers available to all tests
# ---------------------------------------------------------------------------

def _seed_roles():
    for name in ('Familyadmin', 'Guest'):
        if not Role.query.filter_by(name=name).first():
            _db.session.add(Role(name=name))
    _db.session.commit()


def make_user(username='testuser', password='password123',
              first_name='Test', last_name='User', is_system_admin=False):
    user = User(
        username=username,
        password_hash=generate_password_hash(password),
        first_name=first_name,
        last_name=last_name,
        is_system_admin=is_system_admin,
    )
    _db.session.add(user)
    _db.session.flush()
    return user


def make_family(name='Musterfamilie'):
    family = Family(name=name)
    _db.session.add(family)
    _db.session.flush()
    return family


def make_widget_type(key='todo', display_name='Aufgaben'):
    wt = WidgetType.query.filter_by(key=key).first()
    if not wt:
        wt = WidgetType(key=key, display_name=display_name, description='')
        _db.session.add(wt)
        _db.session.flush()
    return wt


def assign_role(user, family, role_name='Familyadmin'):
    role = Role.query.filter_by(name=role_name).first()
    ufr = UserFamilyRole(user_id=user.id, family_id=family.id, role_id=role.id)
    _db.session.add(ufr)
    _db.session.flush()
    return ufr


def make_family_widget(family, widget_type):
    fw = FamilyWidget(family_id=family.id, widget_type_id=widget_type.id)
    _db.session.add(fw)
    _db.session.flush()
    return fw


def grant_permission(user, family_widget, can_view=True, can_edit=False):
    perm = WidgetUserPermission(
        family_widget_id=family_widget.id,
        user_id=user.id,
        can_view=can_view,
        can_edit=can_edit,
    )
    _db.session.add(perm)
    _db.session.flush()
    return perm
