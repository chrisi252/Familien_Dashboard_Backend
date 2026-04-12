"""System Admin Routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.utils import require_system_admin
from app.models import Family, User
from app.services import UserService

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/families', methods=['GET'])
@jwt_required()
@require_system_admin
def list_families():
    try:
        families = Family.query.order_by(Family.created_at.desc()).all()
        return jsonify({'families': [f.to_dict() for f in families]}), 200
    except Exception as e:
        return jsonify({'error': 'Familien konnten nicht abgerufen werden', 'details': str(e)}), 500


@admin_bp.route('/accounts', methods=['POST'])
@jwt_required()
@require_system_admin
def create_admin_account():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Keine Daten übergeben'}), 400

        user = UserService.create_user(
            username=data.get('username'),
            password=data.get('password'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
        )

        from app import db
        user.is_system_admin = True
        db.session.commit()

        return jsonify({'message': 'Admin-Account erstellt', 'user': user.to_dict()}), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Admin-Account konnte nicht erstellt werden', 'details': str(e)}), 500
