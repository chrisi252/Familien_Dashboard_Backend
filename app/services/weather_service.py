"""Weather service - handles geocoding and weather API calls (OpenWeatherMap)"""
import os
import time
import requests
from app import db
from app.models import FamilyWeatherConfig, UserFamilyRole


GEOCODING_URL = 'https://api.openweathermap.org/geo/1.0/direct'
CURRENT_WEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather'
FORECAST_URL = 'https://api.openweathermap.org/data/2.5/forecast'

# Cache TTL in seconds — 60s = max 60 API calls/hour per family (free tier limit)
CACHE_TTL = int(os.environ.get('WEATHER_CACHE_TTL', 60))

# In-memory cache: { family_id: {'data': dict, 'ts': float} }
_weather_cache: dict[int, dict] = {}


def _api_key() -> str:
    key = os.environ.get('OPENWEATHER_API_KEY', '')
    if not key:
        raise RuntimeError('OPENWEATHER_API_KEY ist nicht gesetzt')
    return key


class WeatherService:
    """Handles weather config storage and API calls"""

    @staticmethod
    def geocode_city(city_name: str) -> dict:
        """Resolve a city name to lat/lon via OpenWeatherMap Geocoding API.

        Returns dict with keys: city_name, latitude, longitude
        Raises ValueError if city not found.
        """
        resp = requests.get(
            GEOCODING_URL,
            params={'q': city_name, 'limit': 1, 'appid': _api_key()},
            timeout=5
        )
        resp.raise_for_status()
        results = resp.json()
        if not results:
            raise ValueError(f'Stadt "{city_name}" nicht gefunden')
        result = results[0]
        return {
            'city_name': result.get('local_names', {}).get('de') or result.get('name', city_name),
            'latitude': result['lat'],
            'longitude': result['lon'],
        }

    @staticmethod
    def get_or_create_config(family_id: int) -> FamilyWeatherConfig:
        """Return existing config or create default one for the family."""
        config = FamilyWeatherConfig.query.filter_by(family_id=family_id).first()
        if not config:
            config = FamilyWeatherConfig(family_id=family_id)
            db.session.add(config)
            db.session.commit()
        return config

    @staticmethod
    def update_location(family_id: int, city_name: str) -> FamilyWeatherConfig:
        """Geocode city_name and persist the new location for the family."""
        geo = WeatherService.geocode_city(city_name)
        config = WeatherService.get_or_create_config(family_id)
        config.city_name = geo['city_name']
        config.latitude = geo['latitude']
        config.longitude = geo['longitude']
        try:
            db.session.commit()
            _weather_cache.pop(family_id, None)  # invalidate cache on location change
            return config
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def fetch_weather(family_id: int) -> dict:
        """Fetch current weather + 5-day forecast for the family's configured location.

        Results are cached in memory for CACHE_TTL seconds to stay within the
        OpenWeatherMap free-tier limit of 60 calls/hour.
        """
        cached = _weather_cache.get(family_id)
        if cached and (time.monotonic() - cached['ts']) < CACHE_TTL:
            return cached['data']

        config = WeatherService.get_or_create_config(family_id)
        api_key = _api_key()
        params = {
            'lat': config.latitude,
            'lon': config.longitude,
            'appid': api_key,
            'units': 'metric',
            'lang': 'de',
        }

        current_resp = requests.get(CURRENT_WEATHER_URL, params=params, timeout=5)
        current_resp.raise_for_status()
        current_data = current_resp.json()

        forecast_resp = requests.get(FORECAST_URL, params={**params, 'cnt': 40}, timeout=5)
        forecast_resp.raise_for_status()
        forecast_data = forecast_resp.json()

        # Current weather
        weather = current_data.get('weather', [{}])[0]
        main = current_data.get('main', {})
        wind = current_data.get('wind', {})

        current = {
            'temperature': main.get('temp'),
            'apparent_temperature': main.get('feels_like'),
            'humidity': main.get('humidity'),
            'wind_speed': wind.get('speed'),
            'weather_code': weather.get('id'),
            'weather_description': weather.get('description', '').capitalize(),
            'icon': weather.get('icon'),
        }

        # Build daily forecast by grouping 3h entries per day
        daily_map: dict[str, dict] = {}
        for entry in forecast_data.get('list', []):
            date = entry['dt_txt'][:10]
            w = entry.get('weather', [{}])[0]
            m = entry.get('main', {})
            temp = m.get('temp')
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

        result = {
            'location': config.to_dict(),
            'current': current,
            'forecast': forecast,
        }
        _weather_cache[family_id] = {'data': result, 'ts': time.monotonic()}
        return result

    @staticmethod
    def is_family_admin(user_id: int, family_id: int) -> bool:
        """Return True if the user has the Familyadmin role in the given family."""
        membership = UserFamilyRole.query.filter_by(
            user_id=user_id, family_id=family_id
        ).first()
        if not membership:
            return False
        return membership.role.name == 'Familyadmin'
