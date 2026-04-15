"""Tests for WidgetService"""
import pytest

from app.models import FamilyWidget, UserWidgetConfig, WidgetUserPermission
from app.services.family_service import FamilyService
from app.services.widget_service import WidgetService
from tests.conftest import (
    grant_permission,
    make_family,
    make_family_widget,
    make_user,
    make_widget_type,
)


class TestGetWidgetsForUser:

    def test_user_sees_widget_with_view_permission(self, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)

        widgets = WidgetService.get_widgets_for_user(family.id, admin.id)

        assert len(widgets) >= 1

    def test_user_does_not_see_widget_without_view_permission(self, db_transaction):
        user = make_user()
        family = make_family()
        wt = make_widget_type(key='hidden', display_name='Hidden')
        fw = make_family_widget(family, wt)
        grant_permission(user, fw, can_view=False, can_edit=False)

        widgets = WidgetService.get_widgets_for_user(family.id, user.id)

        assert len(widgets) == 0

    def test_can_edit_flag_is_correctly_passed_through(self, db_transaction):
        user = make_user()
        family = make_family()
        wt = make_widget_type(key='editable', display_name='Editable')
        fw = make_family_widget(family, wt)
        grant_permission(user, fw, can_view=True, can_edit=True)

        widgets = WidgetService.get_widgets_for_user(family.id, user.id)

        assert widgets[0]['can_edit'] is True

    def test_user_only_sees_own_family_widgets(self, db_transaction):
        admin = make_user(username='admin')
        other_user = make_user(username='other')
        FamilyService.create_family('FamilieA', admin.id)
        family_b = FamilyService.create_family('FamilieB', other_user.id)

        # admin hat keine Permissions in family_b
        widgets = WidgetService.get_widgets_for_user(family_b.id, admin.id)

        assert len(widgets) == 0


class TestUpdateUserPermission:

    def test_permission_change_is_persisted(self, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        fw = FamilyWidget.query.filter_by(family_id=family.id).first()

        WidgetService.update_user_permission(family.id, fw.id, admin.id, can_view=True, can_edit=True)

        perm = WidgetUserPermission.query.filter_by(
            family_widget_id=fw.id, user_id=admin.id
        ).first()
        assert perm.can_edit is True

    def test_widget_from_different_family_raises(self, db_transaction):
        admin = make_user(username='admin')
        other = make_user(username='other')
        family_a = FamilyService.create_family('FamilieA', admin.id)
        family_b = FamilyService.create_family('FamilieB', other.id)
        fw_b = FamilyWidget.query.filter_by(family_id=family_b.id).first()

        # Widget gehört zu family_b, aber wir fragen mit family_a
        with pytest.raises(ValueError, match='Widget'):
            WidgetService.update_user_permission(family_a.id, fw_b.id, admin.id, True, False)

    def test_user_without_permission_entry_raises(self, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        stranger = make_user(username='stranger')
        fw = FamilyWidget.query.filter_by(family_id=family.id).first()

        with pytest.raises(ValueError, match='Permission'):
            WidgetService.update_user_permission(family.id, fw.id, stranger.id, True, False)


class TestUpdateLayout:

    def test_layout_change_is_persisted(self, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        fw = FamilyWidget.query.filter_by(family_id=family.id).first()

        layout = [{'family_widget_id': fw.id, 'position': 0, 'grid_col': 2, 'grid_row': 3}]
        configs = WidgetService.update_layout(family.id, admin.id, layout)

        assert len(configs) == 1
        assert configs[0]['grid_col'] == 2
        assert configs[0]['grid_row'] == 3
        assert configs[0]['position'] == 0

        cfg = UserWidgetConfig.query.filter_by(
            user_id=admin.id, family_widget_id=fw.id
        ).first()
        assert cfg is not None
        assert cfg.grid_col == 2
        assert cfg.grid_row == 3

    def test_widget_from_different_family_raises(self, db_transaction):
        admin = make_user(username='admin')
        other = make_user(username='other')
        family_a = FamilyService.create_family('FamilieA', admin.id)
        family_b = FamilyService.create_family('FamilieB', other.id)
        fw_b = FamilyWidget.query.filter_by(family_id=family_b.id).first()

        layout = [{'family_widget_id': fw_b.id, 'position': 0, 'grid_col': 1, 'grid_row': 1}]
        with pytest.raises(ValueError, match='Widget'):
            WidgetService.update_layout(family_a.id, admin.id, layout)

    def test_layout_replaces_previous_config(self, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        fw = FamilyWidget.query.filter_by(family_id=family.id).first()

        WidgetService.update_layout(family.id, admin.id, [
            {'family_widget_id': fw.id, 'position': 0, 'grid_col': 1, 'grid_row': 1},
        ])
        WidgetService.update_layout(family.id, admin.id, [
            {'family_widget_id': fw.id, 'position': 5, 'grid_col': 4, 'grid_row': 2},
        ])

        configs = UserWidgetConfig.query.filter_by(user_id=admin.id).all()
        assert len(configs) == 1
        assert configs[0].position == 5
        assert configs[0].grid_col == 4

    def test_empty_layout_clears_configs(self, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        fw = FamilyWidget.query.filter_by(family_id=family.id).first()

        WidgetService.update_layout(family.id, admin.id, [
            {'family_widget_id': fw.id, 'position': 0, 'grid_col': 1, 'grid_row': 1},
        ])
        WidgetService.update_layout(family.id, admin.id, [])

        configs = UserWidgetConfig.query.filter_by(user_id=admin.id).all()
        assert len(configs) == 0

    def test_layout_defaults_for_missing_fields(self, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        fw = FamilyWidget.query.filter_by(family_id=family.id).first()

        configs = WidgetService.update_layout(family.id, admin.id, [
            {'family_widget_id': fw.id},
        ])

        assert configs[0]['position'] == 0
        assert configs[0]['grid_col'] == 1
        assert configs[0]['grid_row'] == 1

    def test_layout_per_user_isolation(self, db_transaction):
        admin = make_user(username='admin')
        family = FamilyService.create_family('Familie', admin.id)
        guest = make_user(username='guest')
        FamilyService.add_user_to_family(guest.id, family.id)
        fw = FamilyWidget.query.filter_by(family_id=family.id).first()

        WidgetService.update_layout(family.id, admin.id, [
            {'family_widget_id': fw.id, 'position': 0, 'grid_col': 3, 'grid_row': 3},
        ])
        WidgetService.update_layout(family.id, guest.id, [
            {'family_widget_id': fw.id, 'position': 1, 'grid_col': 1, 'grid_row': 1},
        ])

        admin_cfg = UserWidgetConfig.query.filter_by(user_id=admin.id, family_widget_id=fw.id).first()
        guest_cfg = UserWidgetConfig.query.filter_by(user_id=guest.id, family_widget_id=fw.id).first()
        assert admin_cfg.grid_col == 3
        assert guest_cfg.grid_col == 1
