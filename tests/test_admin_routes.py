"""Tests für Systemadmin-Route: GET /api/admin/users"""
import pytest
from flask_jwt_extended import create_access_token

from app.services.family_service import FamilyService
from tests.conftest import make_user


def _auth_headers(app, user_id):
    with app.app_context():
        token = create_access_token(identity=str(user_id))
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture(autouse=True)
def _use_header_jwt(app):
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    yield
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']


class TestListUsers:

    def test_system_admin_gets_all_users(self, app, client, db_transaction):
        admin = make_user(username='sysadmin', is_system_admin=True)
        make_user(username='alice')
        make_user(username='bob')

        resp = client.get('/api/admin/users', headers=_auth_headers(app, admin.id))

        assert resp.status_code == 200
        usernames = [u['username'] for u in resp.get_json()['users']]
        assert 'alice' in usernames
        assert 'bob' in usernames
        assert 'sysadmin' in usernames

    def test_normal_user_gets_403(self, app, client, db_transaction):
        user = make_user(username='normaluser', is_system_admin=False)

        resp = client.get('/api/admin/users', headers=_auth_headers(app, user.id))

        assert resp.status_code == 403

    def test_unauthenticated_gets_401(self, client, db_transaction):
        resp = client.get('/api/admin/users')

        assert resp.status_code == 401

    def test_user_includes_families_with_role(self, app, client, db_transaction):
        admin = make_user(username='sysadmin', is_system_admin=True)
        user = make_user(username='member')
        FamilyService.create_family('Musterfamilie', user.id)

        resp = client.get('/api/admin/users', headers=_auth_headers(app, admin.id))

        users = resp.get_json()['users']
        member = next(u for u in users if u['username'] == 'member')
        assert len(member['families']) == 1
        assert member['families'][0]['family']['name'] == 'Musterfamilie'
        assert member['families'][0]['role'] == 'Familyadmin'

    def test_user_in_multiple_families(self, app, client, db_transaction):
        admin = make_user(username='sysadmin', is_system_admin=True)
        user = make_user(username='member')
        FamilyService.create_family('Familie A', user.id)
        other = make_user(username='other')
        family_b = FamilyService.create_family('Familie B', other.id)
        FamilyService.add_user_to_family(user.id, family_b.id, role_name='Guest')

        resp = client.get('/api/admin/users', headers=_auth_headers(app, admin.id))

        users = resp.get_json()['users']
        member = next(u for u in users if u['username'] == 'member')
        family_names = [e['family']['name'] for e in member['families']]
        assert 'Familie A' in family_names
        assert 'Familie B' in family_names

    def test_user_without_family_has_empty_list(self, app, client, db_transaction):
        admin = make_user(username='sysadmin', is_system_admin=True)
        make_user(username='loner')

        resp = client.get('/api/admin/users', headers=_auth_headers(app, admin.id))

        users = resp.get_json()['users']
        loner = next(u for u in users if u['username'] == 'loner')
        assert loner['families'] == []
