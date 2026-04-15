from app.widgets.registry import register

from .widget import WeatherWidget

register(WeatherWidget())

__all__ = ['WeatherWidget']
