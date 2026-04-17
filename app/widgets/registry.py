"""Widget Registry — in-memory store for all explicitly registered widgets.

Ablauf:
1. create_app() erstellt alle Widget-Instanzen und ruft register() explizit auf.
2. Anschließend werden die Widget-Routen am Flask-App-Objekt registriert.
3. sync_to_db() stellt sicher, dass alle registrierten Widgets als WidgetType
    in der DB existieren und für jede Familie FamilyWidget +
    WidgetUserPermission angelegt sind.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.widgets.base import BaseWidget

_registry: dict[str, BaseWidget] = {}


def register(widget: BaseWidget) -> None:
    _registry[widget.key] = widget


def get(key: str) -> BaseWidget | None:
    return _registry.get(key)


def get_all() -> list[BaseWidget]:
    return list(_registry.values())


def sync_to_db() -> None:
    """Synchronisiert WidgetTypes und legt FamilyWidget + Berechtigungen für alle Familien an."""
    from app import db
    from app.models import Family, FamilyWidget, UserFamilyRole, WidgetType
    from app.services.family_service import _create_family_widget, _create_widget_permission

    for widget in _registry.values():
        if not WidgetType.query.filter_by(key=widget.key).first():
            db.session.add(WidgetType(
                key=widget.key,
                display_name=widget.display_name,
                description=widget.description,
            ))
    db.session.flush()

    all_widget_types = WidgetType.query.all()
    for family in Family.query.all():
        existing_wt_ids = {
            fw.widget_type_id
            for fw in FamilyWidget.query.filter_by(family_id=family.id).all()
        }
        for wt in all_widget_types:
            if wt.id in existing_wt_ids:
                continue
            fw = _create_family_widget(family.id, wt)
            for member in UserFamilyRole.query.filter_by(family_id=family.id).all():
                role_name = member.role.name if member.role else 'Guest'
                _create_widget_permission(fw.id, member.user_id, role_name, wt.key)

    db.session.commit()
