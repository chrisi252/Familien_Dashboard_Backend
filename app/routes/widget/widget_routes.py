from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import WidgetService
from app.utils import require_family_admin

widget_bp = Blueprint('widget', __name__, url_prefix='/api/families')


@widget_bp.route('/<int:family_id>/widgets', methods=['GET'])
@jwt_required()
def get_widgets(family_id):
    try:
        user_id = int(get_jwt_identity())
        widgets = WidgetService.get_widgets_for_user(family_id, user_id)
        return jsonify({'widgets': widgets}), 200
    except Exception as e:
        return jsonify({'error': 'Widgets konnten nicht abgerufen werden', 'details': str(e)}), 500


@widget_bp.route('/<int:family_id>/widgets/<int:family_widget_id>/permissions', methods=['GET'])
@jwt_required()
@require_family_admin
def get_widget_permissions(family_id, family_widget_id):
    try:
        permissions = WidgetService.get_widget_permissions(family_id, family_widget_id)
        return jsonify({'permissions': permissions}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'Berechtigungen konnten nicht abgerufen werden', 'details': str(e)}), 500


@widget_bp.route('/<int:family_id>/widgets/<int:family_widget_id>/permissions/<int:user_id>', methods=['PUT'])
@jwt_required()
@require_family_admin
def update_user_permission(family_id, family_widget_id, user_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Keine Daten übergeben'}), 400

        perm = WidgetService.update_user_permission(
            family_id=family_id,
            family_widget_id=family_widget_id,
            user_id=user_id,
            can_view=data.get('can_view', True),
            can_edit=data.get('can_edit', False),
        )
        return jsonify(perm.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'Permission konnte nicht aktualisiert werden', 'details': str(e)}), 500


@widget_bp.route('/<int:family_id>/widgets/layout', methods=['PUT'])
@jwt_required()
def update_layout(family_id):
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        if not data or 'layout' not in data:
            return jsonify({'error': 'Keine Layout-Daten übergeben'}), 400

        configs = WidgetService.update_layout(
            family_id=family_id,
            user_id=user_id,
            layout=data['layout'],
        )
        return jsonify({'configs': configs}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'Layout konnte nicht aktualisiert werden', 'details': str(e)}), 500
