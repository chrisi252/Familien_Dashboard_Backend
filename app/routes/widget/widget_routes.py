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


@widget_bp.route('/<int:family_id>/widgets', methods=['POST'])
@jwt_required()
@require_family_admin
def enable_widget(family_id):
    try:
        data = request.get_json()
        if not data or not data.get('widget_key'):
            return jsonify({'error': 'Feld "widget_key" ist erforderlich'}), 400

        family_widget = WidgetService.enable_widget(family_id, data['widget_key'])
        return jsonify(family_widget.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Widget konnte nicht aktiviert werden', 'details': str(e)}), 500


@widget_bp.route('/<int:family_id>/widgets/<int:family_widget_id>', methods=['DELETE'])
@jwt_required()
@require_family_admin
def disable_widget(family_id, family_widget_id):
    try:
        WidgetService.disable_widget(family_id, family_widget_id)
        return jsonify({'message': 'Widget deaktiviert'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'Widget konnte nicht deaktiviert werden', 'details': str(e)}), 500


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


@widget_bp.route('/<int:family_id>/widgets/<int:family_widget_id>/layout', methods=['PUT'])
@jwt_required()
@require_family_admin
def update_layout(family_id, family_widget_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Keine Daten übergeben'}), 400

        family_widget = WidgetService.update_layout(
            family_id=family_id,
            family_widget_id=family_widget_id,
            grid_col=data.get('grid_col', 1),
            grid_row=data.get('grid_row', 1),
            grid_pos_x=data.get('grid_pos_x', 0),
            grid_pos_y=data.get('grid_pos_y', 0),
        )
        return jsonify(family_widget.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'Layout konnte nicht aktualisiert werden', 'details': str(e)}), 500
