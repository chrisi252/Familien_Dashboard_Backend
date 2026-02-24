from flask import Flask, Blueprint, jsonify

app = Flask(__name__)
# Erstelle einen Blueprint für die Hauptrouten
main_bp = Blueprint('main', __name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@main_bp.route('/api/health', methods=['GET'])
def health_check():
    """Ein einfacher Endpunkt, um zu testen, ob die API erreichbar ist."""
    return jsonify({
        "status": "success",
        "message": "Familien-Dashboard API läuft einwandfrei!"
    }), 200