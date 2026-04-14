"""Abstrakte Basisklasse für alle Widgets"""
from abc import ABC, abstractmethod


class BaseWidget(ABC):

    key: str
    display_name: str
    description: str

    @abstractmethod
    def register_routes(self, flask_app) -> None:
        pass

    def get_default_permissions(self, role_name: str) -> dict:
        from app.services.family_service import ROLE_ADMIN
        if role_name == ROLE_ADMIN:
            return {'can_view': True, 'can_edit': True}
        return {'can_view': True, 'can_edit': False}
