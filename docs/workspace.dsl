workspace "Familien-Dashboard" "C4-Architekturmodell des Familien-Dashboard Backends" {

    model {
        # Personen
        familyadmin = person "Familyadmin" "Erstellt und verwaltet eine Familie. Kann Berechtigungen und Layout ändern."
        guest = person "Gast" "Familienmitglied mit eingeschränkten Rechten (can_view, kein can_edit)."

        # Externe Systeme
        openweathermap = softwareSystem "OpenWeatherMap API" "Liefert Wetterdaten, Vorhersagen und Geocoding." "External"

        # Familien-Dashboard
        familienDashboard = softwareSystem "Familien-Dashboard" "Webbasiertes Dashboard für Familien mit Widgets (Todo, Wetter)." {

            # Container
            frontend = container "Frontend SPA" "Single Page Application für das Dashboard." "React / TypeScript" "Browser"

            backend = container "Backend API" "REST API mit JWT-Auth, Widget-System und Permissions." "Python / Flask" {
                # Routes
                userRoutes = component "User Routes" "Register, Login, Profile, Logout" "Flask Blueprint"
                familyRoutes = component "Family Routes" "Family CRUD, Join" "Flask Blueprint"
                widgetRoutes = component "Widget Routes" "Widget-Liste, Permissions, Layout" "Flask Blueprint"
                todoRoutes = component "Todo Routes" "Todo CRUD" "Flask Blueprint (Widget)"
                weatherRoutes = component "Weather Routes" "Wetter abrufen, Standort ändern" "Flask Blueprint (Widget)"

                # Decorators
                authDecorators = component "Auth & Permission Decorators" "JWT-Validierung, require_family_admin, require_widget_permission" "Python Decorators"

                # Services
                userService = component "UserService" "User-Erstellung, Passwort-Validierung" "Service Layer"
                familyService = component "FamilyService" "Family-Erstellung mit Auto-Widget-Provisioning, Mitgliederverwaltung" "Service Layer"
                widgetService = component "WidgetService" "Widget-Liste, Permission-Updates, Layout" "Service Layer"
                todoService = component "TodoService" "Todo CRUD" "Service Layer"
                weatherService = component "WeatherService" "Geocoding, Wetter-API-Aufrufe" "Service Layer"
                roleService = component "RoleService" "Rollenabfragen (Familyadmin, Guest)" "Service Layer"

                # Widget System
                widgetRegistry = component "Widget Registry" "In-Memory Registry + sync_to_db() provisioniert Widgets für alle Familien" "Python Module"
                baseWidget = component "BaseWidget" "Abstrakte Basisklasse mit get_default_permissions()" "ABC"

                # Models
                models = component "SQLAlchemy Models" "User, Family, Role, UserFamilyRole, WidgetType, FamilyWidget, WidgetUserPermission, Todo, FamilyWeatherConfig" "SQLAlchemy ORM"

                # JWT
                jwtManager = component "JWT Manager" "Cookie-basierte JWT-Authentifizierung" "Flask-JWT-Extended"
            }

            database = container "PostgreSQL" "Speichert User, Familien, Widgets, Permissions, Todos, Wetter-Konfiguration." "PostgreSQL 16" "Database"
        }

        # Beziehungen — Personen
        familyadmin -> frontend "Nutzt" "Browser"
        guest -> frontend "Nutzt" "Browser"
        frontend -> backend "API Requests" "HTTPS / JSON + JWT Cookie"

        # Beziehungen — Container
        backend -> database "Liest/Schreibt" "SQLAlchemy / PostgreSQL"
        backend -> openweathermap "Wetter + Geocoding" "HTTPS / JSON"

        # Beziehungen — Komponenten (Routes → Decorators)
        userRoutes -> jwtManager "JWT erstellen/löschen"
        familyRoutes -> authDecorators "JWT + Admin-Check"
        widgetRoutes -> authDecorators "JWT + Admin-Check"
        todoRoutes -> authDecorators "JWT + Widget-Permission-Check"
        weatherRoutes -> authDecorators "JWT + Widget-Permission-Check"

        # Beziehungen — Komponenten (Routes → Services)
        userRoutes -> userService "Delegiert an"
        userRoutes -> familyService "Familien bei Login laden"
        userRoutes -> roleService "Admin-Status prüfen"
        familyRoutes -> familyService "Delegiert an"
        widgetRoutes -> widgetService "Delegiert an"
        todoRoutes -> todoService "Delegiert an"
        weatherRoutes -> weatherService "Delegiert an"

        # Beziehungen — Services → Models/DB
        userService -> models "Liest/Schreibt User"
        familyService -> models "Liest/Schreibt Family, UserFamilyRole, FamilyWidget, WidgetUserPermission"
        widgetService -> models "Liest/Schreibt FamilyWidget, WidgetUserPermission"
        todoService -> models "Liest/Schreibt Todo"
        weatherService -> models "Liest/Schreibt FamilyWeatherConfig"
        roleService -> models "Liest UserFamilyRole"
        authDecorators -> models "Prüft Membership + Permissions"

        # Beziehungen — Services → Externe Systeme
        weatherService -> openweathermap "Current Weather, Forecast, Geocoding" "HTTPS"

        # Beziehungen — Widget System
        familyService -> widgetRegistry "get_default_permissions() bei Family-Erstellung"
        widgetRegistry -> baseWidget "Verwaltet registrierte Widgets"
        widgetRegistry -> models "sync_to_db() erstellt WidgetType + FamilyWidget + Permissions"

        # Beziehungen — Models → DB
        models -> database "ORM Queries"
    }

    views {
        # Level 1: System Context
        systemContext familienDashboard "SystemContext" {
            include *
            autoLayout
            description "Systemkontext: Familien-Dashboard mit Benutzern und externen Systemen"
        }

        # Level 2: Container
        container familienDashboard "Containers" {
            include *
            autoLayout
            description "Container-Sicht: Frontend, Backend API, Datenbank"
        }

        # Level 3: Components
        component backend "Components" {
            include *
            autoLayout
            description "Komponenten des Backend-API-Containers"
        }

        styles {
            element "Person" {
                shape Person
                background #08427B
                color #ffffff
            }
            element "Software System" {
                background #1168BD
                color #ffffff
            }
            element "External" {
                background #999999
                color #ffffff
            }
            element "Container" {
                background #438DD5
                color #ffffff
            }
            element "Browser" {
                shape WebBrowser
            }
            element "Database" {
                shape Cylinder
                background #438DD5
                color #ffffff
            }
            element "Component" {
                background #85BBF0
                color #000000
            }
        }
    }

}
