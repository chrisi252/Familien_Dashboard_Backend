from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import CalendarService
from datetime import datetime

calendar_bp = Blueprint('calendar', __name__, url_prefix='/api/calendar')


def _parse_datetime(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid datetime format: '{value}'. Expected ISO 8601, e.g. '2026-04-01T10:00:00'")


@calendar_bp.route('/', methods=['POST'])
@jwt_required()
def create_event():
    """Create a new calendar event.

    Expected JSON body:
    {
        "family_id": 1,
        "title": "string",
        "start_datetime": "2026-04-01T10:00:00",
        "description": "string (optional)",
        "end_datetime": "2026-04-01T11:00:00 (optional)",
        "is_all_day": false,
        "is_public_to_family": false,
        "color": "#FF5733 (optional)"
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        family_id = data.get('family_id')
        title = data.get('title')
        start_datetime = data.get('start_datetime')

        if not family_id:
            return jsonify({'error': 'family_id is required'}), 400
        if not title:
            return jsonify({'error': 'title is required'}), 400
        if not start_datetime:
            return jsonify({'error': 'start_datetime is required'}), 400

        event = CalendarService.create_event(
            family_id=family_id,
            created_by=user_id,
            title=title,
            start_datetime=_parse_datetime(start_datetime),
            description=data.get('description'),
            end_datetime=_parse_datetime(data.get('end_datetime')),
            is_all_day=data.get('is_all_day', False),
            is_public_to_family=data.get('is_public_to_family', False),
            color=data.get('color'),
        )
        return jsonify(event.to_dict()), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to create event', 'details': str(e)}), 500


@calendar_bp.route('/family/<int:family_id>', methods=['GET'])
@jwt_required()
def get_events(family_id):
    """Get all visible calendar events for the current user in a family."""
    try:
        user_id = int(get_jwt_identity())
        events = CalendarService.get_events_for_user(family_id=family_id, user_id=user_id)
        return jsonify([e.to_dict() for e in events]), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get events', 'details': str(e)}), 500


@calendar_bp.route('/<int:event_id>', methods=['GET'])
@jwt_required()
def get_event(event_id):
    """Get a single calendar event by ID."""
    try:
        user_id = int(get_jwt_identity())
        event = CalendarService.get_event_by_id(event_id=event_id, user_id=user_id)
        if not event:
            return jsonify({'error': 'Event not found or access denied'}), 404
        return jsonify(event.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get event', 'details': str(e)}), 500


@calendar_bp.route('/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_event(event_id):
    """Update a calendar event (only the creator).

    JSON body fields (all optional):
    title, description, start_datetime, end_datetime,
    is_all_day, is_public_to_family, color
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        kwargs = {}
        for field in ('title', 'description', 'is_all_day', 'is_public_to_family', 'color'):
            if field in data:
                kwargs[field] = data[field]
        for dt_field in ('start_datetime', 'end_datetime'):
            if dt_field in data:
                kwargs[dt_field] = _parse_datetime(data[dt_field])

        event = CalendarService.update_event(event_id=event_id, user_id=user_id, **kwargs)
        return jsonify(event.to_dict()), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to update event', 'details': str(e)}), 500


@calendar_bp.route('/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_event(event_id):
    """Delete a calendar event (only the creator)."""
    try:
        user_id = int(get_jwt_identity())
        CalendarService.delete_event(event_id=event_id, user_id=user_id)
        return jsonify({'message': 'Event deleted'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to delete event', 'details': str(e)}), 500


@calendar_bp.route('/<int:event_id>/visibility', methods=['PUT'])
@jwt_required()
def set_visibility(event_id):
    """Set which users can see an event (only the creator).

    Expected JSON body:
    {
        "user_ids": [1, 2, 3]
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        if not data or 'user_ids' not in data:
            return jsonify({'error': 'user_ids is required'}), 400

        event = CalendarService.set_visibility(
            event_id=event_id,
            user_id=user_id,
            visible_user_ids=data['user_ids']
        )
        return jsonify(event.to_dict()), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to set visibility', 'details': str(e)}), 500
