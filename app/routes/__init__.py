from flask import Blueprint, jsonify

from .admin import admin_bp
from .family import family_bp
from .user import user_bp
from .widget import widget_bp

main_bp = Blueprint('main', __name__)


@main_bp.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'success', 'message': 'Familien-Dashboard API aktiv'}), 200


@main_bp.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'success', 'message': 'Familien-Dashboard API läuft einwandfrei'}), 200


__all__ = [
    'main_bp',
    'user_bp',
    'family_bp',
    'widget_bp',
    'admin_bp',
]
