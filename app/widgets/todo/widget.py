"""Todo Widget"""
from app.widgets.base import BaseWidget


class TodoWidget(BaseWidget):
    key = 'todo'
    display_name = 'Aufgaben'
    description = 'Gemeinsame Todo-Liste für die Familie'

    def register_routes(self, flask_app) -> None:
        from .routes import bp
        flask_app.register_blueprint(bp)
