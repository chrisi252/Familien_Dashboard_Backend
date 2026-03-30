from flask import Blueprint, jsonify
from .example import example_bp
from .user import user_bp
from .familiy import family_bp
from .weather import weather_bp
from .widget import widget_bp
from .calendar import calendar_bp

# Hauptrouten Blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route("/", methods=['GET'])
def home():
    """Hauptseite / Home-Route"""
    return jsonify({
        "status": "success",
        "message": "Familien-Dashboard API aktiv"
    }), 200


__all__ = [
    'main_bp',
    'example_bp',
    'user_bp',
    'family_bp',
    'calendar_bp',
    'weather_bp',
    'widget_bp',
]
