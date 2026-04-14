"""Wetter-Service — kapselt Geocoding und Wetter-API-Aufrufe (OpenWeatherMap)"""
import os

import requests

from app import db
from app.models import FamilyWeatherConfig

GEOCODING_URL = 'https://api.openweathermap.org/geo/1.0/direct'
CURRENT_WEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather'
FORECAST_URL = 'https://api.openweathermap.org/data/2.5/forecast'

_WEATHER_UNITS = 'metric'
_WEATHER_LANG = 'de'
_FORECAST_ENTRIES = 40  # 5 Tage × 8 Einträge pro Tag (3-Stunden-Intervall)
_REQUEST_TIMEOUT = 5


def _api_key() -> str:
    key = os.environ.get('OPENWEATHER_API_KEY', '')
    if not key:
        raise RuntimeError('OPENWEATHER_API_KEY is not set')
    return key


class WeatherService:

    @staticmethod
    def geocode_city(city_name: str) -> dict:
        """Löst einen Stadtnamen in Koordinaten auf (OpenWeatherMap Geocoding API).

        Gibt ein Dict mit city_name, latitude, longitude zurück.
        Wirft ValueError wenn die Stadt nicht gefunden wurde.
        """
        resp = requests.get(
            GEOCODING_URL,
            params={'q': city_name, 'limit': 1, 'appid': _api_key()},
            timeout=_REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        results = resp.json()
        if not results:
            raise ValueError(f'City "{city_name}" not found')
        result = results[0]
        return {
            'city_name': result.get('local_names', {}).get('de') or result.get('name', city_name),
            'latitude': result['lat'],
            'longitude': result['lon'],
        }

    @staticmethod
    def get_or_create_config(family_id: int) -> FamilyWeatherConfig:
        """Gibt die bestehende Wetterkonfiguration zurück oder legt eine Standardkonfiguration an."""
        config = FamilyWeatherConfig.query.filter_by(family_id=family_id).first()
        if not config:
            config = FamilyWeatherConfig(family_id=family_id)
            db.session.add(config)
            db.session.commit()
        return config

    @staticmethod
    def update_location(family_id: int, city_name: str) -> FamilyWeatherConfig:
        geo = WeatherService.geocode_city(city_name)
        config = WeatherService.get_or_create_config(family_id)
        config.city_name = geo['city_name']
        config.latitude = geo['latitude']
        config.longitude = geo['longitude']
        try:
            db.session.commit()
            return config
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def fetch_weather(family_id: int) -> dict:
        config = WeatherService.get_or_create_config(family_id)
        params = {
            'lat': config.latitude,
            'lon': config.longitude,
            'appid': _api_key(),
            'units': _WEATHER_UNITS,
            'lang': _WEATHER_LANG,
        }
        current_data = _fetch_current_weather(params)
        forecast_data = _fetch_forecast(params)

        return {
            'location': config.to_dict(),
            'current': _parse_current_weather(current_data),
            'forecast': _build_daily_forecast(forecast_data.get('list', [])),
        }


# ---------------------------------------------------------------------------
# Private Hilfsfunktionen
# ---------------------------------------------------------------------------

def _fetch_current_weather(params: dict) -> dict:
    resp = requests.get(CURRENT_WEATHER_URL, params=params, timeout=_REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def _fetch_forecast(params: dict) -> dict:
    resp = requests.get(
        FORECAST_URL,
        params={**params, 'cnt': _FORECAST_ENTRIES},
        timeout=_REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def _parse_current_weather(data: dict) -> dict:
    weather = data.get('weather', [{}])[0]
    main = data.get('main', {})
    wind = data.get('wind', {})
    return {
        'temperature': main.get('temp'),
        'apparent_temperature': main.get('feels_like'),
        'humidity': main.get('humidity'),
        'wind_speed': wind.get('speed'),
        'weather_code': weather.get('id'),
        'weather_description': weather.get('description', '').capitalize(),
        'icon': weather.get('icon'),
    }


def _build_daily_forecast(entries: list) -> list:
    """Gruppiert 3-Stunden-Einträge nach Tag und berechnet Tages-Min/Max."""
    daily_map: dict[str, dict] = {}
    for entry in entries:
        date = entry['dt_txt'][:10]
        w = entry.get('weather', [{}])[0]
        temp = entry.get('main', {}).get('temp')

        if date not in daily_map:
            daily_map[date] = {
                'date': date,
                'weather_code': w.get('id'),
                'weather_description': w.get('description', '').capitalize(),
                'icon': w.get('icon'),
                'temps': [],
            }
        if temp is not None:
            daily_map[date]['temps'].append(temp)

    forecast = []
    for day in daily_map.values():
        temps = day.pop('temps')
        day['temperature_max'] = round(max(temps), 1) if temps else None
        day['temperature_min'] = round(min(temps), 1) if temps else None
        forecast.append(day)
    return forecast
