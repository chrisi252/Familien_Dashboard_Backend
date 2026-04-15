from app.widgets.registry import register

from .widget import TimetableWidget

register(TimetableWidget())

__all__ = ['TimetableWidget']
