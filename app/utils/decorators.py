"""Wiederverwendbare Routen-Dekoratoren"""
from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from app.models import UserFamilyRole, User


def require_family_admin(f):
    """Dekorator: erlaubt den Zugriff nur für den Familyadmin der angefragten Familie.

    Muss nach @jwt_required() stehen, da get_jwt_identity() einen aktiven JWT voraussetzt.
    Die Route muss family_id als URL-Parameter haben.

    Beispiel:
        @bp.route('/<int:family_id>/widgets')
        @jwt_required()
        @require_family_admin
        def get_widgets(family_id):
            ...
    """
    @wraps(f)
    def decorated(family_id, *args, **kwargs):
        user_id = int(get_jwt_identity())
        membership = UserFamilyRole.query.filter_by(
            user_id=user_id, family_id=family_id
        ).first()
        if not membership or membership.role.name != 'Familyadmin':
            return jsonify({'error': 'Only the family admin has access'}), 403
        return f(family_id, *args, **kwargs)
    return decorated


def require_widget_permission(permission: str):
    """Dekorator-Factory: prüft ob der User can_view oder can_edit für das Widget hat.

    Liest den Widget-Key aus request.blueprint — daher muss der Blueprint-Name
    mit BaseWidget.key übereinstimmen.

    Muss nach @jwt_required() stehen. Die Route muss family_id als URL-Parameter haben.

    Args:
        permission: 'can_view' oder 'can_edit'

    Beispiel:
        @bp.route('/<int:family_id>/todos')
        @jwt_required()
        @require_widget_permission('can_view')
        def get_todos(family_id):
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(family_id, *args, **kwargs):
            from app.models import FamilyWidget, WidgetType, WidgetUserPermission

            user_id = int(get_jwt_identity())

            membership = UserFamilyRole.query.filter_by(
                user_id=user_id, family_id=family_id
            ).first()
            if not membership:
                return jsonify({'error': 'Not a family member'}), 403

            widget_key = request.blueprint
            family_widget = (
                FamilyWidget.query
                .join(WidgetType)
                .filter(
                    FamilyWidget.family_id == family_id,
                    WidgetType.key == widget_key,
                )
                .first()
            )
            if not family_widget:
                return jsonify({'error': 'Widget not active'}), 404

            perm = WidgetUserPermission.query.filter_by(
                family_widget_id=family_widget.id,
                user_id=user_id,
            ).first()
            if not perm or not getattr(perm, permission):
                return jsonify({'error': 'Permission denied'}), 403

            return f(family_id, *args, **kwargs)
        return decorated
    return decorator


def require_system_admin(f):
    """Dekorator: erlaubt den Zugriff nur für Systemadministratoren (user.is_system_admin).

    Muss nach @jwt_required() stehen.

    Beispiel:
        @bp.route('/registry')
        @jwt_required()
        @require_system_admin
        def get_registry():
            ...
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user or not user.is_system_admin:
            return jsonify({'error': 'Only system administrators have access'}), 403
        return f(*args, **kwargs)
    return decorated
