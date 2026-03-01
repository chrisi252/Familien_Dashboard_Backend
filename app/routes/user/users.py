from flask import Blueprint, request, jsonify
from app.services import UserService
from flask_jwt_extended import create_access_token, jwt_required

user_bp = Blueprint('user', __name__, url_prefix='/api/users')


@user_bp.route('/', methods=['GET'])
def get_users():
    """Get all users"""
    try:
        users = UserService.get_all_users()
        return jsonify({
            'status': 'success',
            'data': [user.to_dict() for user in users]
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a single user by ID"""
    try:
        user = UserService.get_user_by_id(user_id)
        if not user:
            return jsonify({
                'status': 'error',
                'message': f'User with ID {user_id} not found'
            }), 404

        return jsonify({
            'status': 'success',
            'data': user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@user_bp.route('', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()

        # Validate input
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400

        name = data.get('name')
        email = data.get('email')

        if not name or not email:
            return jsonify({
                'status': 'error',
                'message': 'Name and email are required'
            }), 400

        user = UserService.create_user(name, email)
        return jsonify({
            'status': 'success',
            'data': user.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 409
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    # Validiere User (du brauchst password_hash im User-Model)
    access_token = create_access_token(identity=email)
    return jsonify({'access_token': access_token}), 200

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user = UserService.get_user(current_user_id)
    return jsonify(user.to_dict()), 200