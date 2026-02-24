from flask import Blueprint, jsonify

# Blueprint für Example/Health Routes
example_bp = Blueprint('example', __name__, url_prefix='/api/example')


@example_bp.route('/health', methods=['GET'])
def health_check():
    """Health Check Endpunkt"""
    return jsonify({
        "status": "success",
        "message": "Familien-Dashboard API läuft einwandfrei!"
    }), 200
