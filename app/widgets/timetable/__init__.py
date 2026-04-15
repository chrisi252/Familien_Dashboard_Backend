from .widget import TimetableWidget
from app.widgets.registry import register

register(TimetableWidget())

__all__ = ['TimetableWidget']
