"""Tests for FamilyService — fokus auf Berechtigungslogik und Invarianten"""
import pytest

from app.models import FamilyWidget, UserFamilyRole, UserWidgetConfig, WidgetUserPermission
from app.services.family_service import FamilyService
from tests.conftest import make_user


class TestCreateFamily:

    def test_creates_family_with_name(self, db_transaction):
        user = make_user()
        family = FamilyService.create_family('Musterfamilie', user.id)
        assert family.id is not None
        assert family.name == 'Musterfamilie'

    def test_creator_becomes_familyadmin(self, db_transaction):
        user = make_user()
        family = FamilyService.create_family('Musterfamilie', user.id)
        membership = UserFamilyRole.query.filter_by(
            user_id=user.id, family_id=family.id
        ).first()
        assert membership is not None
        assert membership.role.name == 'Familyadmin'

    def test_all_widget_types_get_family_widget(self, db_transaction):
        user = make_user()
        family = FamilyService.create_family('Musterfamilie', user.id)
        widgets = FamilyWidget.query.filter_by(family_id=family.id).all()
        # Mindestens die registrierten Widgets (todo, weather) müssen vorhanden sein
        assert len(widgets) >= 1

    def test_admin_gets_can_view_true_on_all_widgets(self, db_transaction):
        user = make_user()
        family = FamilyService.create_family('Musterfamilie', user.id)
        widgets = FamilyWidget.query.filter_by(family_id=family.id).all()
        for fw in widgets:
            perm = WidgetUserPermission.query.filter_by(
                family_widget_id=fw.id, user_id=user.id
            ).first()
            assert perm is not None, f'Keine Permission für Widget {fw.id}'
            assert perm.can_view is True, 'Familyadmin muss immer can_view=True haben'

    def test_empty_name_raises(self, db_transaction):
        user = make_user()
        with pytest.raises(ValueError):
            FamilyService.create_family('', user.id)

    def test_whitespace_name_raises(self, db_transaction):
        user = make_user()
        with pytest.raises(ValueError):
            FamilyService.create_family('   ', user.id)

    def test_unknown_user_raises(self, db_transaction):
        with pytest.raises(ValueError, match='User not found'):
            FamilyService.create_family('Familie', 99999)


class TestAddUserToFamily:

    def test_adds_user_as_guest_by_default(self, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        guest = make_user(username='guest')

        FamilyService.add_user_to_family(guest.id, family.id)

        membership = UserFamilyRole.query.filter_by(
            user_id=guest.id, family_id=family.id
        ).first()
        assert membership is not None
        assert membership.role.name == 'Guest'

    def test_guest_gets_widget_permissions(self, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        guest = make_user(username='guest')

        FamilyService.add_user_to_family(guest.id, family.id)

        widgets = FamilyWidget.query.filter_by(family_id=family.id).all()
        for fw in widgets:
            perm = WidgetUserPermission.query.filter_by(
                family_widget_id=fw.id, user_id=guest.id
            ).first()
            assert perm is not None, f'Guest hat keine Permission für Widget {fw.id}'

    def test_adding_duplicate_member_raises(self, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)

        with pytest.raises(ValueError, match='already a member'):
            FamilyService.add_user_to_family(admin.id, family.id)

    def test_unknown_user_raises(self, db_transaction):
        admin = make_user()
        family = FamilyService.create_family('Familie', admin.id)
        with pytest.raises(ValueError, match='User not found'):
            FamilyService.add_user_to_family(99999, family.id)

    def test_unknown_family_raises(self, db_transaction):
        user = make_user()
        with pytest.raises(ValueError, match='Family not found'):
            FamilyService.add_user_to_family(user.id, 99999)


class TestRemoveUserFromFamily:

    def test_removes_member(self, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        guest = make_user(username='guest')
        FamilyService.add_user_to_family(guest.id, family.id)

        FamilyService.remove_user_from_family(guest.id, family.id)

        membership = UserFamilyRole.query.filter_by(
            user_id=guest.id, family_id=family.id
        ).first()
        assert membership is None

    def test_remove_non_member_raises(self, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        stranger = make_user(username='stranger')

        with pytest.raises(ValueError, match='not a member'):
            FamilyService.remove_user_from_family(stranger.id, family.id)

    def test_removes_widget_permissions(self, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        guest = make_user(username='guest')
        FamilyService.add_user_to_family(guest.id, family.id)

        family_widget_ids = [fw.id for fw in FamilyWidget.query.filter_by(family_id=family.id).all()]
        perms_before = WidgetUserPermission.query.filter(
            WidgetUserPermission.user_id == guest.id,
            WidgetUserPermission.family_widget_id.in_(family_widget_ids),
        ).count()
        assert perms_before > 0

        FamilyService.remove_user_from_family(guest.id, family.id)

        perms_after = WidgetUserPermission.query.filter(
            WidgetUserPermission.user_id == guest.id,
            WidgetUserPermission.family_widget_id.in_(family_widget_ids),
        ).count()
        assert perms_after == 0

    def test_removes_widget_configs(self, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        guest = make_user(username='guest')
        FamilyService.add_user_to_family(guest.id, family.id)

        fw = FamilyWidget.query.filter_by(family_id=family.id).first()
        db_transaction.session.add(UserWidgetConfig(
            user_id=guest.id, family_widget_id=fw.id, position=0, grid_col=1, grid_row=1,
        ))
        db_transaction.session.flush()

        FamilyService.remove_user_from_family(guest.id, family.id)

        configs = UserWidgetConfig.query.filter_by(user_id=guest.id, family_widget_id=fw.id).count()
        assert configs == 0

    def test_does_not_remove_other_family_permissions(self, db_transaction):
        admin_a = make_user(username='admin_a')
        admin_b = make_user(username='admin_b')
        family_a = FamilyService.create_family('FamilieA', admin_a.id)
        family_b = FamilyService.create_family('FamilieB', admin_b.id)
        guest = make_user(username='guest')
        FamilyService.add_user_to_family(guest.id, family_a.id)
        FamilyService.add_user_to_family(guest.id, family_b.id)

        FamilyService.remove_user_from_family(guest.id, family_a.id)

        family_b_widget_ids = [fw.id for fw in FamilyWidget.query.filter_by(family_id=family_b.id).all()]
        perms_b = WidgetUserPermission.query.filter(
            WidgetUserPermission.user_id == guest.id,
            WidgetUserPermission.family_widget_id.in_(family_b_widget_ids),
        ).count()
        assert perms_b > 0


class TestIsMember:

    def test_member_returns_true(self, db_transaction):
        admin = make_user()
        family = FamilyService.create_family('Familie', admin.id)
        assert FamilyService.is_member(admin.id, family.id) is True

    def test_non_member_returns_false(self, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        stranger = make_user(username='stranger')
        assert FamilyService.is_member(stranger.id, family.id) is False
