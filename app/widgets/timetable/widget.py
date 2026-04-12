"""Timetable Widget"""
from app.widgets.base import BaseWidget
from app.widgets.registry import register


class TimetableWidget(BaseWidget):
    key = 'timetable'
    display_name = 'Stundenplan'
    description = 'Wochenstundenpläne für Kinder mit Zeitangaben und Farbzuweisung'

    def register_routes(self, flask_app) -> None:
        from .routes import bp
        flask_app.register_blueprint(bp)


register(TimetableWidget())
