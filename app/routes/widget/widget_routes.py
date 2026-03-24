from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.services import WidgetService
from app.utils import require_family_admin

widget_bp = Blueprint('widget', __name__, url_prefix='/api/families')


@widget_bp.route('/<int:family_id>/widgets', methods=['GET'])
@jwt_required()
@require_family_admin
def get_all_widgets(family_id):
    """Gibt alle Widgets der Familie zurück. Nur für Familyadmin.

    Returns:
        {
            "widgets": [
                {
                    "id", "family_id", "widget_type_id", "widget_key",
                    "display_name", "description", "is_enabled",
                    "permissions": [{ "role_name", "can_view", "can_edit" }, ...]
                },
                ...
            ]
        }
    """
    try:
        widgets = WidgetService.get_all_widgets(family_id)
        return jsonify({'widgets': widgets}), 200
    except Exception as e:
        return jsonify({'error': 'Widgets konnten nicht abgerufen werden', 'details': str(e)}), 500
