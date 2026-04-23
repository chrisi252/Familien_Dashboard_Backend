"""Widget-System Package."""

from app.widgets.base import BaseWidget
from app.widgets.chat.widget import ChatWidget
from app.widgets.timetable.widget import TimetableWidget
from app.widgets.todo.widget import TodoWidget
from app.widgets.weather.widget import WeatherWidget


def get_widget_instances() -> list[BaseWidget]:
    """Returns all widget instances that should be registered at app startup."""
    return [
        TimetableWidget(),
        TodoWidget(),
        WeatherWidget(),
        ChatWidget(),
    ]


__all__ = ["get_widget_instances"]
