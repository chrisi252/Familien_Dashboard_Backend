"""Chat Widget HTTP Routes — returns last 10 messages for initial load."""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.models import ChatMessage
from app.utils import require_widget_permission

bp = Blueprint('chat', __name__, url_prefix='/api/families')


@bp.route('/<int:family_id>/chat/messages', methods=['GET'])
@jwt_required()
@require_widget_permission('can_view')
def get_messages(family_id):
    messages = (
        ChatMessage.query
        .filter_by(family_id=family_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(10)
        .all()
    )
    return jsonify({'messages': [m.to_dict() for m in reversed(messages)]}), 200
