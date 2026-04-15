"""Stundenplan Widget Routen"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.widgets.timetable.service import TimetableService
from app.utils import require_widget_permission

bp = Blueprint('timetable', __name__, url_prefix='/api/families')


@bp.route('/<int:family_id>/timetable/persons', methods=['GET'])
@jwt_required()
@require_widget_permission('can_view')
def get_persons(family_id):
    try:
        return jsonify({'persons': TimetableService.get_persons(family_id)}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get persons', 'details': str(e)}), 500


@bp.route('/<int:family_id>/timetable/<string:person_name>/entries', methods=['GET'])
@jwt_required()
@require_widget_permission('can_view')
def get_entries(family_id, person_name):
    try:
        return jsonify({'entries': TimetableService.get_entries(family_id, person_name)}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get entries', 'details': str(e)}), 500


@bp.route('/<int:family_id>/timetable/entries', methods=['POST'])
@jwt_required()
@require_widget_permission('can_edit')
def create_entry(family_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        entry = TimetableService.create_entry(family_id, data)
        return jsonify(entry.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to create entry', 'details': str(e)}), 500


@bp.route('/<int:family_id>/timetable/entries/<int:entry_id>', methods=['PUT'])
@jwt_required()
@require_widget_permission('can_edit')
def update_entry(family_id, entry_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        entry = TimetableService.update_entry(entry_id, family_id, data)
        return jsonify(entry.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'Failed to update entry', 'details': str(e)}), 500


@bp.route('/<int:family_id>/timetable/entries/<int:entry_id>', methods=['DELETE'])
@jwt_required()
@require_widget_permission('can_edit')
def delete_entry(family_id, entry_id):
    try:
        TimetableService.delete_entry(entry_id, family_id)
        return jsonify({'message': 'Entry deleted'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'Failed to delete entry', 'details': str(e)}), 500
