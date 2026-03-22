from flask import Blueprint, request, jsonify
from app.services import FamilyService
from flask_jwt_extended import jwt_required, get_jwt_identity

family_bp = Blueprint('family', __name__, url_prefix='/api/families')


@family_bp.route('', methods=['POST'])
@jwt_required()
def create_family():
    """Create a new family
    
    Expected JSON body:
    {
        "name": "string"
    }
    
    Returns: Family object with creator as Familyadmin
    """
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        family_name = data.get('name')
        if not family_name:
            return jsonify({'error': 'Family name is required'}), 400
        
        family = FamilyService.create_family(family_name, current_user_id)
        
        return jsonify(family.to_dict()), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to create family', 'details': str(e)}), 500


@family_bp.route('/<int:family_id>/join', methods=['POST'])
@jwt_required()
def join_family(family_id):
    """Join an existing family
    
    The user is added with 'Guest' role by default
    
    Returns: UserFamilyRole object
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        # Add user with Guest role (default)
        user_family_role = FamilyService.add_user_to_family(
            current_user_id,
            family_id
        )
        
        return jsonify(user_family_role.to_dict()), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to join family', 'details': str(e)}), 500


@family_bp.route('', methods=['GET'])
@jwt_required()
def get_families():
    """Get all families of the current user"""
    try:
        current_user_id = int(get_jwt_identity())
        user_family_roles = FamilyService.get_user_families(current_user_id)
        
        families = [
            {
                'family': role.family.to_dict(),
                'role': role.role.to_dict(),
                'user_family_role': role.to_dict()
            }
            for role in user_family_roles
        ]
        
        return jsonify(families), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to get families', 'details': str(e)}), 500


@family_bp.route('/<int:family_id>', methods=['GET'])
@jwt_required()
def get_family(family_id):
    """Get family details with members"""
    try:
        current_user_id = int(get_jwt_identity())
        family = FamilyService.get_family_by_id(family_id)
        if not family:
            return jsonify({'error': 'Family not found'}), 404

        if not FamilyService.is_member(current_user_id, family_id):
            return jsonify({'error': 'Access denied'}), 403

        members = FamilyService.get_family_members(family_id)

        return jsonify({
            'family': family.to_dict(),
            'members': [member.to_dict() for member in members]
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to get family', 'details': str(e)}), 500


@family_bp.route('/<int:family_id>', methods=['DELETE'])
@jwt_required()
def delete_family(family_id):
    """Delete a family (admin only)"""
    try:
        family = FamilyService.get_family_by_id(family_id)
        if not family:
            return jsonify({'error': 'Family not found'}), 404
        
        FamilyService.delete_family(family_id)
        
        return jsonify({'message': 'Family deleted successfully'}), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to delete family', 'details': str(e)}), 500
