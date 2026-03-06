from flask import Blueprint, jsonify
from app.services import WidgetService

widget_bp = Blueprint('widget', __name__, url_prefix='/api/widgets')


@widget_bp.route('/family/<int:family_id>', methods=['GET'])
def get_family_widgets(family_id):
    """ 
    Get all widgets for a family with permissions for a specific role.
    Query parameters:
        - role_id (required): The role ID to check permissions for
    """
    try:
        # get role via JWT Token later on
        role_id = "user"

        if not role_id:
            return jsonify({
                'status': 'error',
                'message': 'role_id query parameter is required'
            }), 400

        widgets = WidgetService.get_widgets_with_role_permissions(
            family_id, role_id)

        return jsonify({
            'status': 'success',
            'data': [widget.to_dict() for widget in widgets]
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
