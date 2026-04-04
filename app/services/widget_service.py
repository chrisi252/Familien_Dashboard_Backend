"""Widget service"""
from app import db
from app.models import FamilyWidget, WidgetType, WidgetUserPermission, UserFamilyRole


class WidgetService:

    @staticmethod
    def get_widgets_for_user(family_id: int, user_id: int) -> list[dict]:
        """Gibt alle aktiven Widgets zurück, für die der User can_view hat.

        Enthält can_edit damit das Frontend Bearbeitungsoptionen anzeigen kann.
        """
        perms = (
            WidgetUserPermission.query
            .join(FamilyWidget)
            .join(WidgetType)
            .filter(
                FamilyWidget.family_id == family_id,
                FamilyWidget.is_enabled,
                WidgetUserPermission.user_id == user_id,
                WidgetUserPermission.can_view,
            )
            .all()
        )
        result = []
        for perm in perms:
            data = perm.family_widget.to_dict()
            data['display_name'] = perm.family_widget.widget_type.display_name
            data['description'] = perm.family_widget.widget_type.description
            data['can_edit'] = perm.can_edit
            result.append(data)
        return result

    @staticmethod
    def enable_widget(family_id: int, widget_type_key: str) -> FamilyWidget:
        """Aktiviert ein Widget für eine Familie und legt User-Permissions an.

        Für alle Familienmitglieder werden WidgetUserPermission-Einträge
        mit den Widget-Defaults (BaseWidget.get_default_permissions) angelegt.
        """
        from app.widgets import registry

        widget_type = WidgetType.query.filter_by(key=widget_type_key).first()
        if not widget_type:
            raise ValueError(f'Widget-Typ "{widget_type_key}" nicht gefunden')

        existing = FamilyWidget.query.filter_by(
            family_id=family_id, widget_type_id=widget_type.id
        ).first()
        if existing:
            raise ValueError('Widget ist bereits aktiv')

        family_widget = FamilyWidget(family_id=family_id, widget_type_id=widget_type.id)
        db.session.add(family_widget)
        db.session.flush()

        widget_instance = registry.get(widget_type_key)
        members = UserFamilyRole.query.filter_by(family_id=family_id).all()

        for member in members:
            role_name = member.role.name if member.role else 'Guest'
            defaults = widget_instance.get_default_permissions(role_name) if widget_instance else {
                'can_view': True, 'can_edit': False
            }
            if role_name == 'Familyadmin':
                defaults['can_view'] = True
            db.session.add(WidgetUserPermission(
                family_widget_id=family_widget.id,
                user_id=member.user_id,
                can_view=defaults['can_view'],
                can_edit=defaults['can_edit'],
            ))

        db.session.commit()
        return family_widget

    @staticmethod
    def disable_widget(family_id: int, family_widget_id: int) -> None:
        """Deaktiviert ein Widget (löscht es samt User-Permissions)."""
        family_widget = FamilyWidget.query.filter_by(
            id=family_widget_id, family_id=family_id
        ).first()
        if not family_widget:
            raise ValueError('Widget nicht gefunden')
        db.session.delete(family_widget)
        db.session.commit()

    @staticmethod
    def update_user_permission(
        family_id: int,
        family_widget_id: int,
        user_id: int,
        can_view: bool,
        can_edit: bool,
    ) -> WidgetUserPermission:
        """Überschreibt die Permission eines Users für ein Widget."""
        family_widget = FamilyWidget.query.filter_by(
            id=family_widget_id, family_id=family_id
        ).first()
        if not family_widget:
            raise ValueError('Widget nicht gefunden')

        perm = WidgetUserPermission.query.filter_by(
            family_widget_id=family_widget_id, user_id=user_id
        ).first()
        if not perm:
            raise ValueError('Permission-Eintrag nicht gefunden')

        perm.can_view = can_view
        perm.can_edit = can_edit
        db.session.commit()
        return perm

    @staticmethod
    def update_layout(
        family_id: int,
        family_widget_id: int,
        grid_col: int,
        grid_row: int,
        grid_pos_x: int,
        grid_pos_y: int,
    ) -> FamilyWidget:
        """Speichert das Grid-Layout eines Widgets."""
        family_widget = FamilyWidget.query.filter_by(
            id=family_widget_id, family_id=family_id
        ).first()
        if not family_widget:
            raise ValueError('Widget nicht gefunden')

        family_widget.grid_col = grid_col
        family_widget.grid_row = grid_row
        family_widget.grid_pos_x = grid_pos_x
        family_widget.grid_pos_y = grid_pos_y
        db.session.commit()
        return family_widget
