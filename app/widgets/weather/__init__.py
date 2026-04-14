from .widget import WeatherWidget
from app.widgets.registry import register

register(WeatherWidget())

__all__ = ['WeatherWidget']
