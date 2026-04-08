"""Tests for RoleService"""
from app.services.role_service import RoleService
from app.services.family_service import FamilyService
from tests.conftest import make_user


class TestGetUserRole:

    def test_creator_has_familyadmin_role(self, db_transaction):
        user = make_user()
        family = FamilyService.create_family('Familie', user.id)
        assert RoleService.get_user_role(user.id, family.id) == 'Familyadmin'

    def test_added_user_has_guest_role(self, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        guest = make_user(username='guest')
        FamilyService.add_user_to_family(guest.id, family.id)

        assert RoleService.get_user_role(guest.id, family.id) == 'Guest'

    def test_non_member_returns_none(self, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        stranger = make_user(username='stranger')

        assert RoleService.get_user_role(stranger.id, family.id) is None


class TestIsFamilyAdmin:

    def test_guest_is_not_admin(self, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        guest = make_user(username='guest')
        FamilyService.add_user_to_family(guest.id, family.id)

        assert RoleService.is_family_admin(guest.id, family.id) is False

    def test_non_member_is_not_admin(self, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        stranger = make_user(username='stranger')

        assert RoleService.is_family_admin(stranger.id, family.id) is False
