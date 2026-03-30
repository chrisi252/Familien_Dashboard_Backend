"""Widget service"""
from app.models import FamilyWidget, WidgetType


class WidgetService:

    @staticmethod
    def get_all_widgets(family_id: int) -> list[dict]:
        """Gibt alle Widgets einer Familie zurück, inkl. Typ-Info und Rollenberechtigungen."""
        widgets = FamilyWidget.query.filter_by(family_id=family_id).all()
        result = []
        for widget in widgets:
            data = widget.to_dict()
            data['display_name'] = widget.widget_type.display_name if widget.widget_type else None
            data['description'] = widget.widget_type.description if widget.widget_type else None
            data['permissions'] = [p.to_dict() for p in widget.permissions]
            result.append(data)
        return result

    @staticmethod
    def get_all_widget_types() -> list[dict]:
        """Gibt alle verfügbaren Widget-Typen im System zurück."""
        return [wt.to_dict() for wt in WidgetType.query.all()]
