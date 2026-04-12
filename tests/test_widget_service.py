"""Tests for WidgetService"""
import pytest

from app.services.widget_service import WidgetService
from app.services.family_service import FamilyService
from app.models import FamilyWidget, WidgetUserPermission
from tests.conftest import make_user, make_family, make_widget_type, make_family_widget, grant_permission


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
        family_a = FamilyService.create_family('FamilieA', admin.id)
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

        WidgetService.update_layout(family.id, fw.id, grid_col=2, grid_row=3, grid_pos_x=1, grid_pos_y=0)

        updated = FamilyWidget.query.get(fw.id)
        assert updated.grid_col == 2
        assert updated.grid_row == 3
        assert updated.grid_pos_x == 1
        assert updated.grid_pos_y == 0

    def test_widget_from_different_family_raises(self, db_transaction):
        admin = make_user(username='admin')
        other = make_user(username='other')
        family_a = FamilyService.create_family('FamilieA', admin.id)
        family_b = FamilyService.create_family('FamilieB', other.id)
        fw_b = FamilyWidget.query.filter_by(family_id=family_b.id).first()

        with pytest.raises(ValueError, match='Widget'):
            WidgetService.update_layout(family_a.id, fw_b.id, 1, 1, 0, 0)
