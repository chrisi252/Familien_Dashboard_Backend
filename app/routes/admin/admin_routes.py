"""Systemadmin Routen"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.models import Family, User, UserFamilyRole
from app.services import UserService
from app.utils import require_system_admin

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/families', methods=['GET'])
@jwt_required()
@require_system_admin
def list_families():
    try:
        families = Family.query.order_by(Family.created_at.desc()).all()
        return jsonify({'families': [f.to_dict() for f in families]}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get families', 'details': str(e)}), 500


@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@require_system_admin
def list_users():
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        result = []
        for user in users:
            memberships = UserFamilyRole.query.filter_by(user_id=user.id).all()
            families = [
                {
                    'family': m.family.to_dict(),
                    'role': m.role.name if m.role else None,
                }
                for m in memberships
            ]
            result.append({**user.to_dict(), 'families': families})
        return jsonify({'users': result}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get users', 'details': str(e)}), 500


@admin_bp.route('/accounts', methods=['POST'])
@jwt_required()
@require_system_admin
def create_admin_account():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        user = UserService.create_user(
            username=data.get('username'),
            password=data.get('password'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            is_system_admin=True,
        )

        return jsonify({'message': 'Admin account created', 'user': user.to_dict()}), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to create admin account', 'details': str(e)}), 500
