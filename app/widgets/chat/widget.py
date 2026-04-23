"""Chat Widget"""
from app.widgets.base import BaseWidget


class ChatWidget(BaseWidget):
    key = 'chat'
    display_name = 'Familien-Chat'
    description = 'Live-Chat für alle Familienmitglieder'

    def get_default_permissions(self, role_name: str) -> dict:
        return {'can_view': True, 'can_edit': True}

    def register_routes(self, flask_app) -> None:
        from .routes import bp
        flask_app.register_blueprint(bp)
