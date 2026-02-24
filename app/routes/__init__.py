from flask import Blueprint, jsonify
from .example import example_bp
from .user import user_bp

# Hauptrouten Blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route("/", methods=['GET'])
def home():
    """Hauptseite / Home-Route"""
    return jsonify({
        "status": "success",
        "message": "Familien-Dashboard API aktiv"
    }), 200


__all__ = ['main_bp', 'example_bp', 'user_bp']
