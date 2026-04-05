workspace "Familien-Dashboard" "C4-Architekturmodell des Familien-Dashboard Systems" {

    model {
        # Personen
        familyadmin = person "Familyadmin" "Erstellt und verwaltet eine Familie. Kann Berechtigungen verwalten."
        guest = person "Gast" "Familienmitglied mit eingeschränkten Rechten (can_view, kein can_edit)."

        # Externe Systeme
        openweathermap = softwareSystem "OpenWeatherMap API" "Liefert Wetterdaten, Vorhersagen und Geocoding." "External"

        # Familien-Dashboard
        familienDashboard = softwareSystem "Familien-Dashboard" "Webbasiertes Dashboard für Familien mit Widgets (Todo, Wetter)." {

            # Container
            frontend = container "Frontend SPA" "Single Page Application für das Dashboard." "Angular / TypeScript" "Browser" {

                # State & Services
                dashboardService = component "DashboardService" "Zentrales Signal-basiertes State-Management: addedWidgets, widgets, widgetsToAdd. Lädt Widgets vom Backend, persistiert Layout." "Angular Service (Signal)"
                familyServiceFE = component "FamilyService" "API-Calls: Widgets laden, Permissions updaten, Layout speichern (Bulk)." "Angular Service"
                userStateService = component "UserStateService" "Hält aktuellen User und ausgewählte familyId als Signals." "Angular Service (Signal)"

                # Widget Registry
                widgetRegistry = component "Widget Registry" "Statisches Mapping: widget_key → Angular Component + Default-Größe (WIDGET_REGISTRY)." "TypeScript Constant"

                # Routing & Guards
                authGuard = component "Auth Guard" "Schützt Routen — leitet zu Login weiter wenn kein JWT vorhanden." "Angular Guard"

                # Components
                dashboardComponent = component "Dashboard Component" "Haupt-View: rendert addedWidgets-Array, CDK Drag & Drop, Drawer für Widget-Auswahl." "Angular Component"
                widgetComponent = component "Widget Component" "Wrapper für ein einzelnes Widget: Label, NgComponentOutlet, Options-Overlay, cdkDrag." "Angular Component"
                widgetOptions = component "Widget Options" "Overlay zum Ändern von Größe (cols/rows) und Entfernen des Widgets." "Angular Component"
                headerComponent = component "Header Component" "Navigation, User-Info, Family-Auswahl." "Angular Component"
                adminComponent = component "Admin Component" "Verwaltung von Widget-Berechtigungen pro User (nur Familyadmin)." "Angular Component"

                # Widgets
                notesWidget = component "Notes Widget" "Widget für Familiennotizen." "Angular Standalone Component"
                todoWidget = component "Todo Widget" "Widget für die gemeinsame Todo-Liste." "Angular Standalone Component"
                weatherWidget = component "Weather Widget" "Widget für Wetterdaten inkl. Standort-Konfiguration." "Angular Standalone Component"
                scheduleWidget = component "Schedule Widget" "Widget für Termine." "Angular Standalone Component"
                calendarWidget = component "Calendar Widget" "Widget für Google Kalender-Integration." "Angular Standalone Component"
            }

            backend = container "Backend API" "REST API mit JWT-Auth, Widget-System und Permissions." "Python / Flask" {
                # Routes
                userRoutes = component "User Routes" "Register, Login, Profile, Logout" "Flask Blueprint"
                familyRoutes = component "Family Routes" "Family CRUD, Join" "Flask Blueprint"
                widgetRoutes = component "Widget Routes" "Widget-Liste, Permissions, User-Layout" "Flask Blueprint"
                todoRoutes = component "Todo Routes" "Todo CRUD" "Flask Blueprint (Widget)"
                weatherRoutes = component "Weather Routes" "Wetter abrufen, Standort ändern" "Flask Blueprint (Widget)"

                # Decorators
                authDecorators = component "Auth & Permission Decorators" "JWT-Validierung, require_family_admin, require_widget_permission" "Python Decorators"

                # Services
                userService = component "UserService" "User-Erstellung, Passwort-Validierung" "Service Layer"
                familyService = component "FamilyService" "Family-Erstellung mit Auto-Widget-Provisioning, Mitgliederverwaltung" "Service Layer"
                widgetService = component "WidgetService" "Widget-Liste, Permission-Updates, User-Layout (Bulk)" "Service Layer"
                todoService = component "TodoService" "Todo CRUD" "Service Layer"
                weatherService = component "WeatherService" "Geocoding, Wetter-API-Aufrufe" "Service Layer"
                roleService = component "RoleService" "Rollenabfragen (Familyadmin, Guest)" "Service Layer"

                # Widget System
                widgetRegistryBE = component "Widget Registry" "In-Memory Registry + sync_to_db() provisioniert Widgets für alle Familien" "Python Module"
                baseWidget = component "BaseWidget" "Abstrakte Basisklasse mit get_default_permissions()" "ABC"

                # Models
                models = component "SQLAlchemy Models" "User, Family, Role, UserFamilyRole, WidgetType, FamilyWidget, WidgetUserPermission, UserWidgetConfig, Todo, FamilyWeatherConfig" "SQLAlchemy ORM"

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

        # Beziehungen — Frontend-Komponenten (intern)
        dashboardComponent -> dashboardService "Liest addedWidgets, widgetsToAdd; ruft add/remove/updatePosition"
        dashboardComponent -> widgetComponent "Rendert pro Widget"
        widgetComponent -> widgetOptions "Zeigt Options-Overlay"
        widgetComponent -> widgetRegistry "Lookup: widget_key → Component"
        dashboardService -> familyServiceFE "getFamilyWidgets(), updateWidgetLayout()"
        dashboardService -> userStateService "currentUser(), currentFamilyId()"
        dashboardService -> widgetRegistry "mapBackendWidget()"
        adminComponent -> familyServiceFE "updateWidgetUserPermission()"
        headerComponent -> userStateService "Zeigt User + Family"

        # Beziehungen — Widget-Komponenten → Services
        todoWidget -> familyServiceFE "GET/POST/PUT/DELETE todos"
        weatherWidget -> familyServiceFE "GET weather, PUT location"

        # Beziehungen — Frontend → Backend (API-Calls via FamilyService)
        familyServiceFE -> widgetRoutes "GET /widgets, PUT /widgets/layout" "HTTPS/JSON"
        familyServiceFE -> todoRoutes "GET/POST/PUT/DELETE /todos" "HTTPS/JSON"
        familyServiceFE -> weatherRoutes "GET /weather, PUT /weather/location" "HTTPS/JSON"
        familyServiceFE -> familyRoutes "GET /families, POST /families, JOIN" "HTTPS/JSON"
        familyServiceFE -> userRoutes "Login, Register, Logout, Profile" "HTTPS/JSON"

        # Beziehungen — Backend-Komponenten (Routes → Decorators)
        userRoutes -> jwtManager "JWT erstellen/löschen"
        familyRoutes -> authDecorators "JWT + Admin-Check"
        widgetRoutes -> authDecorators "JWT-Check (Admin nur bei Permissions)"
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
        familyService -> models "Liest/Schreibt Family, UserFamilyRole, FamilyWidget, WidgetUserPermission, UserWidgetConfig"
        widgetService -> models "Liest/Schreibt FamilyWidget, WidgetUserPermission, UserWidgetConfig"
        todoService -> models "Liest/Schreibt Todo"
        weatherService -> models "Liest/Schreibt FamilyWeatherConfig"
        roleService -> models "Liest UserFamilyRole"
        authDecorators -> models "Prüft Membership + Permissions"

        # Beziehungen — Services → Externe Systeme
        weatherService -> openweathermap "Current Weather, Forecast, Geocoding" "HTTPS"

        # Beziehungen — Widget System
        familyService -> widgetRegistryBE "get_default_permissions() bei Family-Erstellung"
        widgetRegistryBE -> baseWidget "Verwaltet registrierte Widgets"
        widgetRegistryBE -> models "sync_to_db() erstellt WidgetType + FamilyWidget + Permissions"

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
            description "Container-Sicht: Frontend SPA, Backend API, Datenbank"
        }

        # Level 3: Components — Frontend
        component frontend "ComponentsFrontend" {
            include *
            autoLayout
            description "Komponenten der Angular Frontend SPA"
        }

        # Level 3: Components — Backend
        component backend "ComponentsBackend" {
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
