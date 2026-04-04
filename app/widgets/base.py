"""Abstrakte Basisklasse für alle Widgets"""
from abc import ABC, abstractmethod


class BaseWidget(ABC):
    """Basisklasse für alle Widgets.

    Jedes Widget muss key, display_name und description setzen
    sowie register_routes implementieren.

    get_default_permissions kann überschrieben werden, um
    rollenabhängige Startwerte für WidgetUserPermission zu liefern.
    Diese Methode wird ausschließlich beim Anlegen von Einträgen aufgerufen
    (User tritt bei / Admin aktiviert Widget) — nie zur Laufzeit.
    """

    key: str
    display_name: str
    description: str

    @abstractmethod
    def register_routes(self, flask_app) -> None:
        """Meldet den Blueprint des Widgets an der Flask-App an.

        Beispiel:
            def register_routes(self, flask_app):
                from .routes import bp
                flask_app.register_blueprint(bp)
        """
        pass

    def get_default_permissions(self, role_name: str) -> dict:
        """Gibt Default-Permissions für eine Rolle zurück.

        Kann pro Widget überschrieben werden.
        role_name: 'Familyadmin' oder 'Guest'

        Hinweis: Für 'Familyadmin' wird can_view serverseitig immer
        auf True erzwungen (in family_service / widget_service),
        unabhängig vom Rückgabewert dieser Methode.
        """
        if role_name == 'Familyadmin':
            return {'can_view': True, 'can_edit': True}
        return {'can_view': True, 'can_edit': False}
