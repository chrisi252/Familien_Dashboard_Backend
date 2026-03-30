import requests
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import WeatherService
from app.services.family_service import FamilyService

weather_bp = Blueprint('weather', __name__, url_prefix='/api/weather')


@weather_bp.route('/<int:family_id>', methods=['GET'])
@jwt_required()
def get_weather(family_id):
    """Get current weather and 7-day forecast for the family's configured location.

    Every family member can call this endpoint.

    Returns:
        {
            "location": { "city_name", "latitude", "longitude", ... },
            "current":  { "temperature", "apparent_temperature", "humidity",
                          "wind_speed", "weather_code", "weather_description" },
            "forecast": [ { "date", "weather_code", "weather_description",
                            "temperature_max", "temperature_min" }, ... ]
        }
    """
    try:
        current_user_id = int(get_jwt_identity())

        # Verify the user is a member of this family
        families = FamilyService.get_user_families(current_user_id)
        family_ids = [ufr.family_id for ufr in families]
        if family_id not in family_ids:
            return jsonify({'error': 'Kein Zugriff auf diese Familie'}), 403

        weather_data = WeatherService.fetch_weather(family_id)
        return jsonify(weather_data), 200

    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Wetter-API nicht erreichbar', 'details': str(e)}), 502
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Wetterdaten konnten nicht abgerufen werden', 'details': str(e)}), 500


@weather_bp.route('/<int:family_id>/location', methods=['PUT'])
@jwt_required()
def update_location(family_id):
    """Update the weather location for the family. Admin only.

    Expected JSON body:
    {
        "city": "Mannheim"
    }

    Returns:
        { "message": "...", "location": { ... } }
    """
    try:
        current_user_id = int(get_jwt_identity())

        if not WeatherService.is_family_admin(current_user_id, family_id):
            return jsonify({'error': 'Nur der Familienadmin kann den Ort ändern'}), 403

        data = request.get_json()
        if not data or not data.get('city'):
            return jsonify({'error': 'Feld "city" ist erforderlich'}), 400

        config = WeatherService.update_location(family_id, data['city'].strip())
        return jsonify({
            'message': 'Ort erfolgreich aktualisiert',
            'location': config.to_dict()
        }), 200

    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Geocoding-API nicht erreichbar', 'details': str(e)}), 502
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Ort konnte nicht aktualisiert werden', 'details': str(e)}), 500


@weather_bp.route('/<int:family_id>/location', methods=['GET'])
@jwt_required()
def get_location(family_id):
    """Get the currently configured weather location for the family.

    Every family member can call this endpoint.
    """
    try:
        current_user_id = int(get_jwt_identity())

        families = FamilyService.get_user_families(current_user_id)
        family_ids = [ufr.family_id for ufr in families]
        if family_id not in family_ids:
            return jsonify({'error': 'Kein Zugriff auf diese Familie'}), 403

        config = WeatherService.get_or_create_config(family_id)
        return jsonify({'location': config.to_dict()}), 200

    except Exception as e:
        return jsonify({'error': 'Konfiguration konnte nicht abgerufen werden', 'details': str(e)}), 500
