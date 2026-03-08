from flask import Blueprint, request, jsonify
from app.services import UserService
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

user_bp = Blueprint('user', __name__, url_prefix='/api/users')


@user_bp.route('/register', methods=['POST'])
def register():
    """Register a new user
    
    Expected JSON body:
    {
        "username": "string",
        "password": "string",
        "first_name": "string",
        "last_name": "string"
    }
    
    Returns: User object with JWT token
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        
        # Validate required fields
        if not username:
            return jsonify({'error': 'Username is required'}), 400
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        if not first_name:
            return jsonify({'error': 'First name is required'}), 400
        if not last_name:
            return jsonify({'error': 'Last name is required'}), 400
        
        # Create user
        user = UserService.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Generate JWT token
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500


@user_bp.route('/login', methods=['POST'])
def login():
    """Login user
    
    Expected JSON body:
    {
        "username": "string",
        "password": "string"
    }
    
    Returns: JWT token and user data
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        # Validate required fields
        if not username:
            return jsonify({'error': 'Username is required'}), 400
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        # Get user and verify password
        user = UserService.get_user_by_username(username)
        if not user:
            return jsonify({'error': 'Invalid username or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is inactive'}), 403
        
        if not UserService.verify_password(user, password):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Generate JWT token
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500


@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile (requires JWT token)
    
    Returns: Current user data
    """
    try:
        current_user_id = int(get_jwt_identity())
        user = UserService.get_user_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get profile', 'details': str(e)}), 500

