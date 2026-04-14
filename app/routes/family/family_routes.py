from flask import Blueprint, request, jsonify
from app.services import FamilyService
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils import require_family_admin

family_bp = Blueprint('family', __name__, url_prefix='/api/families')


@family_bp.route('', methods=['POST'])
@jwt_required()
def create_family():
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Keine Daten übergeben'}), 400

        family_name = data.get('name')
        if not family_name:
            return jsonify({'error': 'Familienname ist erforderlich'}), 400

        family = FamilyService.create_family(family_name, current_user_id)

        return jsonify(family.to_dict()), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Familie konnte nicht erstellt werden', 'details': str(e)}), 500


@family_bp.route('/<int:family_id>/join', methods=['POST'])
@jwt_required()
def join_family(family_id):
    try:
        current_user_id = int(get_jwt_identity())

        user_family_role = FamilyService.add_user_to_family(
            current_user_id,
            family_id
        )

        return jsonify(user_family_role.to_dict()), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Beitritt fehlgeschlagen', 'details': str(e)}), 500


@family_bp.route('', methods=['GET'])
@jwt_required()
def get_families():
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
        return jsonify({'error': 'Familien konnten nicht abgerufen werden', 'details': str(e)}), 500


@family_bp.route('/<int:family_id>', methods=['GET'])
@jwt_required()
def get_family(family_id):
    try:
        current_user_id = int(get_jwt_identity())
        family = FamilyService.get_family_by_id(family_id)
        if not family:
            return jsonify({'error': 'Familie nicht gefunden'}), 404

        if not FamilyService.is_member(current_user_id, family_id):
            return jsonify({'error': 'Zugriff verweigert'}), 403

        members = FamilyService.get_family_members(family_id)

        return jsonify({
            'family': family.to_dict(),
            'members': [member.to_dict() for member in members]
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Familie konnte nicht abgerufen werden', 'details': str(e)}), 500


@family_bp.route('/<int:family_id>', methods=['DELETE'])
@jwt_required()
@require_family_admin
def delete_family(family_id):
    try:
        FamilyService.delete_family(family_id)

        return jsonify({'message': 'Familie erfolgreich gelöscht'}), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Familie konnte nicht gelöscht werden', 'details': str(e)}), 500


@family_bp.route('/<int:family_id>/invite-code', methods=['POST'])
@jwt_required()
@require_family_admin
def generate_invite_code(family_id):
    try:
        invite = FamilyService.generate_invite_code(family_id)
        return jsonify(invite.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Einladungscode konnte nicht erstellt werden', 'details': str(e)}), 500


@family_bp.route('/join-by-code', methods=['POST'])
@jwt_required()
def join_family_by_code():
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()

        if not data or not data.get('code'):
            return jsonify({'error': 'Einladungscode ist erforderlich'}), 400

        user_family_role = FamilyService.join_family_by_code(current_user_id, data['code'])
        return jsonify(user_family_role.to_dict()), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Beitritt fehlgeschlagen', 'details': str(e)}), 500
