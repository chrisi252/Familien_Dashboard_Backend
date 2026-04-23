"""Chat Widget"""
from app.widgets.base import BaseWidget


class ChatWidget(BaseWidget):
    key = 'chat'
    display_name = 'Familien-Chat'
    description = 'Live-Chat für alle Familienmitglieder'

    def register_routes(self, flask_app) -> None:
        from .routes import bp
        flask_app.register_blueprint(bp)
