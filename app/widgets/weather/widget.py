"""Wetter Widget"""
from app.widgets.base import BaseWidget


class WeatherWidget(BaseWidget):
    key = 'weather'
    display_name = 'Wetter'
    description = 'Aktuelles Wetter'

    def register_routes(self, flask_app) -> None:
        from .routes import bp
        flask_app.register_blueprint(bp)
