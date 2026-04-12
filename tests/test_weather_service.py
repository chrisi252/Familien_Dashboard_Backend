"""Tests for WeatherService"""
import pytest
from unittest.mock import patch, MagicMock

from app.widgets.weather.service import WeatherService
from app.models import FamilyWeatherConfig
from tests.conftest import make_family


def _mock_geocode_response(name='Berlin', lat=52.52, lon=13.405):
    mock_resp = MagicMock()
    mock_resp.json.return_value = [{'name': name, 'local_names': {}, 'lat': lat, 'lon': lon}]
    mock_resp.raise_for_status.return_value = None
    return mock_resp


class TestGetOrCreateConfig:

    def test_creates_default_config_for_new_family(self, db_transaction):
        family = make_family()

        config = WeatherService.get_or_create_config(family.id)

        assert config.family_id == family.id
        assert config.city_name == 'Berlin'

    def test_returns_existing_config(self, db_transaction):
        family = make_family()
        WeatherService.get_or_create_config(family.id)

        # zweiter Aufruf darf keinen neuen Eintrag anlegen
        config = WeatherService.get_or_create_config(family.id)
        count = FamilyWeatherConfig.query.filter_by(family_id=family.id).count()

        assert count == 1
        assert config.family_id == family.id


class TestUpdateLocation:

    def test_saves_geocoded_location(self, db_transaction):
        family = make_family()

        with patch('app.widgets.weather.service.requests.get') as mock_get:
            mock_get.return_value = _mock_geocode_response('München', 48.137, 11.576)
            config = WeatherService.update_location(family.id, 'München')

        assert config.city_name == 'München'
        assert config.latitude == 48.137
        assert config.longitude == 11.576

    def test_unknown_city_raises(self, db_transaction):
        family = make_family()

        with patch('app.widgets.weather.service.requests.get') as mock_get:
            empty_resp = MagicMock()
            empty_resp.json.return_value = []
            empty_resp.raise_for_status.return_value = None
            mock_get.return_value = empty_resp

            with pytest.raises(ValueError, match='nicht gefunden'):
                WeatherService.update_location(family.id, 'Nichtexistenz')

    def test_location_is_persisted(self, db_transaction):
        family = make_family()

        with patch('app.widgets.weather.service.requests.get') as mock_get:
            mock_get.return_value = _mock_geocode_response('Hamburg', 53.55, 10.0)
            WeatherService.update_location(family.id, 'Hamburg')

        saved = FamilyWeatherConfig.query.filter_by(family_id=family.id).first()
        assert saved is not None
        assert saved.city_name == 'Hamburg'


class TestGeocodeCity:

    def test_returns_lat_lon_for_known_city(self, db_transaction):
        with patch('app.widgets.weather.service.requests.get') as mock_get:
            mock_get.return_value = _mock_geocode_response('Berlin', 52.52, 13.405)
            result = WeatherService.geocode_city('Berlin')

        assert result['latitude'] == 52.52
        assert result['longitude'] == 13.405
        assert result['city_name'] == 'Berlin'

    def test_prefers_german_local_name(self, db_transaction):
        mock_resp = MagicMock()
        mock_resp.json.return_value = [{
            'name': 'Vienna',
            'local_names': {'de': 'Wien'},
            'lat': 48.2, 'lon': 16.37,
        }]
        mock_resp.raise_for_status.return_value = None

        with patch('app.widgets.weather.service.requests.get', return_value=mock_resp):
            result = WeatherService.geocode_city('Vienna')

        assert result['city_name'] == 'Wien'

    def test_missing_api_key_raises(self, db_transaction):
        with patch.dict('os.environ', {'OPENWEATHER_API_KEY': ''}):
            with pytest.raises(RuntimeError, match='OPENWEATHER_API_KEY'):
                WeatherService.geocode_city('Berlin')
