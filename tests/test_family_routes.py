"""Tests for family member management routes (DELETE member, PUT change role)"""
import pytest
from flask_jwt_extended import create_access_token

from app.models import FamilyWidget, UserFamilyRole, WidgetUserPermission
from app.services.family_service import FamilyService
from tests.conftest import make_user


def _auth_headers(app, user_id):
    with app.app_context():
        token = create_access_token(identity=str(user_id))
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture(autouse=True)
def _jwt_headers(app):
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    yield
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']


class TestRemoveMember:

    def test_admin_removes_guest(self, app, client, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        guest = make_user(username='guest')
        FamilyService.add_user_to_family(guest.id, family.id)

        resp = client.delete(
            f'/api/families/{family.id}/members/{guest.id}',
            headers=_auth_headers(app, admin.id),
        )

        assert resp.status_code == 200
        assert UserFamilyRole.query.filter_by(user_id=guest.id, family_id=family.id).first() is None

    def test_removes_widget_permissions(self, app, client, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        guest = make_user(username='guest')
        FamilyService.add_user_to_family(guest.id, family.id)

        fw_ids = [fw.id for fw in FamilyWidget.query.filter_by(family_id=family.id).all()]

        client.delete(
            f'/api/families/{family.id}/members/{guest.id}',
            headers=_auth_headers(app, admin.id),
        )

        perms = WidgetUserPermission.query.filter(
            WidgetUserPermission.user_id == guest.id,
            WidgetUserPermission.family_widget_id.in_(fw_ids),
        ).count()
        assert perms == 0

    def test_admin_cannot_remove_self(self, app, client, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)

        resp = client.delete(
            f'/api/families/{family.id}/members/{admin.id}',
            headers=_auth_headers(app, admin.id),
        )

        assert resp.status_code == 400
        assert 'Cannot remove yourself' in resp.get_json()['error']

    def test_guest_cannot_remove_member(self, app, client, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        guest = make_user(username='guest')
        FamilyService.add_user_to_family(guest.id, family.id)
        other = make_user(username='other')
        FamilyService.add_user_to_family(other.id, family.id)

        resp = client.delete(
            f'/api/families/{family.id}/members/{other.id}',
            headers=_auth_headers(app, guest.id),
        )

        assert resp.status_code == 403

    def test_non_member_cannot_remove(self, app, client, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        guest = make_user(username='guest')
        FamilyService.add_user_to_family(guest.id, family.id)
        stranger = make_user(username='stranger')

        resp = client.delete(
            f'/api/families/{family.id}/members/{guest.id}',
            headers=_auth_headers(app, stranger.id),
        )

        assert resp.status_code == 403

    def test_remove_non_member_returns_400(self, app, client, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        stranger = make_user(username='stranger')

        resp = client.delete(
            f'/api/families/{family.id}/members/{stranger.id}',
            headers=_auth_headers(app, admin.id),
        )

        assert resp.status_code == 400
        assert 'not a member' in resp.get_json()['error']

    def test_unauthenticated_returns_401(self, app, client, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)

        resp = client.delete(f'/api/families/{family.id}/members/{admin.id}')

        assert resp.status_code == 401


class TestChangeMemberRole:

    def test_admin_promotes_guest(self, app, client, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        guest = make_user(username='guest')
        FamilyService.add_user_to_family(guest.id, family.id)

        resp = client.put(
            f'/api/families/{family.id}/members/{guest.id}/role',
            headers=_auth_headers(app, admin.id),
            json={'role_name': 'Familyadmin'},
        )

        assert resp.status_code == 200
        data = resp.get_json()
        assert data['role_name'] == 'Familyadmin'

    def test_admin_demotes_to_guest(self, app, client, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        other = make_user(username='other')
        FamilyService.add_user_to_family(other.id, family.id, role_name='Familyadmin')

        resp = client.put(
            f'/api/families/{family.id}/members/{other.id}/role',
            headers=_auth_headers(app, admin.id),
            json={'role_name': 'Guest'},
        )

        assert resp.status_code == 200
        assert resp.get_json()['role_name'] == 'Guest'

    def test_rebuilds_widget_permissions(self, app, client, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        guest = make_user(username='guest')
        FamilyService.add_user_to_family(guest.id, family.id)

        fw_ids = [fw.id for fw in FamilyWidget.query.filter_by(family_id=family.id).all()]

        client.put(
            f'/api/families/{family.id}/members/{guest.id}/role',
            headers=_auth_headers(app, admin.id),
            json={'role_name': 'Familyadmin'},
        )

        perms = WidgetUserPermission.query.filter(
            WidgetUserPermission.user_id == guest.id,
            WidgetUserPermission.family_widget_id.in_(fw_ids),
        ).all()
        assert len(perms) == len(fw_ids)

    def test_cannot_change_own_role(self, app, client, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)

        resp = client.put(
            f'/api/families/{family.id}/members/{admin.id}/role',
            headers=_auth_headers(app, admin.id),
            json={'role_name': 'Guest'},
        )

        assert resp.status_code == 400
        assert 'Cannot change your own role' in resp.get_json()['error']

    def test_missing_role_name_returns_400(self, app, client, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        guest = make_user(username='guest')
        FamilyService.add_user_to_family(guest.id, family.id)

        resp = client.put(
            f'/api/families/{family.id}/members/{guest.id}/role',
            headers=_auth_headers(app, admin.id),
            json={},
        )

        assert resp.status_code == 400
        assert 'role_name' in resp.get_json()['error']

    def test_invalid_role_name_returns_400(self, app, client, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        guest = make_user(username='guest')
        FamilyService.add_user_to_family(guest.id, family.id)

        resp = client.put(
            f'/api/families/{family.id}/members/{guest.id}/role',
            headers=_auth_headers(app, admin.id),
            json={'role_name': 'Superadmin'},
        )

        assert resp.status_code == 400
        assert 'Invalid role' in resp.get_json()['error']

    def test_guest_cannot_change_roles(self, app, client, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        guest = make_user(username='guest')
        FamilyService.add_user_to_family(guest.id, family.id)
        other = make_user(username='other')
        FamilyService.add_user_to_family(other.id, family.id)

        resp = client.put(
            f'/api/families/{family.id}/members/{other.id}/role',
            headers=_auth_headers(app, guest.id),
            json={'role_name': 'Familyadmin'},
        )

        assert resp.status_code == 403

    def test_non_member_cannot_change_roles(self, app, client, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        guest = make_user(username='guest')
        FamilyService.add_user_to_family(guest.id, family.id)
        stranger = make_user(username='stranger')

        resp = client.put(
            f'/api/families/{family.id}/members/{guest.id}/role',
            headers=_auth_headers(app, stranger.id),
            json={'role_name': 'Familyadmin'},
        )

        assert resp.status_code == 403

    def test_unauthenticated_returns_401(self, app, client, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)

        resp = client.put(
            f'/api/families/{family.id}/members/{admin.id}/role',
            json={'role_name': 'Guest'},
        )

        assert resp.status_code == 401
