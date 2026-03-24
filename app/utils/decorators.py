"""Reusable route decorators"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models import UserFamilyRole


def require_family_admin(f):
    """Decorator: erlaubt den Zugriff nur für den Familyadmin der angefragten Familie.

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
            return jsonify({'error': 'Nur der Familienadmin hat Zugriff'}), 403
        return f(family_id, *args, **kwargs)
    return decorated
