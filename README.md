# Familien-Dashboard Backend

REST API für das Familien-Dashboard. Gebaut mit Flask, PostgreSQL und JWT-Authentifizierung über HTTP-only Cookies.

## Technologie-Stack

| Komponente | Technologie |
|---|---|
| Framework | Flask 3.x + Flask-SocketIO |
| Datenbank | PostgreSQL (via SQLAlchemy + psycopg) |
| Migrationen | Flask-Migrate (Alembic) |
| Authentifizierung | JWT in HTTP-only Cookies |
| Echtzeit | SocketIO (Gevent) |
| Validierung | Marshmallow |
| Package Manager | [uv](https://docs.astral.sh/uv/) |

## Projektstruktur

```
app/
├── __init__.py          # App-Factory (create_app)
├── models/              # SQLAlchemy-Modelle
├── schemas/             # Marshmallow-Validierungsschemas
├── services/            # Business-Logik
├── routes/              # Blueprint-Router
│   ├── user/            # /api/users
│   ├── family/          # /api/families
│   ├── widget/          # /api/families (Widget-Layout & Berechtigungen)
│   └── admin/           # /api/admin
├── widgets/             # Widget-System
│   ├── base.py          # Abstrakte Basisklasse
│   ├── registry.py      # Widget-Registrierung & DB-Sync
│   ├── __init__.py      # Widget-Instanzen (hier neue Widgets eintragen)
│   ├── chat/
│   ├── todo/
│   ├── weather/
│   └── timetable/
└── utils/
    └── decorators.py    # @require_family_admin, @require_widget_permission, @validate_schema
```

---

## Lokaler Start

### Voraussetzungen

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) (`pip install uv` oder `brew install uv`)
- Docker oder Podman

### 1. Umgebungsvariablen konfigurieren

`.env`-Datei aus der Vorlage erstellen:

```bash
cp .env.example .env
```

Dann `.env` anpassen:

```env
# Datenbank
POSTGRES_USER=dashboard
POSTGRES_PASSWORD=password
POSTGRES_DB=dashboard
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg://dashboard:password@localhost:5432/dashboard

# JWT — langen zufälligen String verwenden: openssl rand -hex 32
JWT_SECRET_KEY=dein-geheimer-schluessel

# Frontend-URL (für CORS)
FRONTEND_URL=http://localhost:3000

# Wetter-Widget (optional)
OPENWEATHER_API_KEY=

# Initialer Systemadmin (wird beim ersten `sync-widgets` angelegt)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=Admin1234!
```

### 2. Datenbank starten

```bash
docker compose up -d
```

### 3. Dependencies installieren

```bash
uv sync
```

### 4. Datenbank-Schema anlegen

```bash
uv run flask db upgrade
```

### 5. Widgets initialisieren & Systemadmin anlegen

```bash
uv run flask sync-widgets
```

Dieser Befehl:
- Trägt alle Widget-Typen in die Datenbank ein
- Erstellt für jede Familie die zugehörigen Widget-Einträge und Berechtigungen
- Legt den initialen Systemadmin-Account an (sofern `ADMIN_USERNAME` und `ADMIN_PASSWORD` gesetzt sind)

> Muss erneut ausgeführt werden wenn neue Widgets hinzugefügt werden.

### 6. Server starten

```bash
uv run python main.py
```

Die API ist unter `http://localhost:5000` erreichbar.

---

## Datenbank-Migrationen

```bash
# Migration nach Model-Änderungen erstellen
uv run flask db migrate -m "Beschreibung"

# Migration anwenden
uv run flask db upgrade

# Migration rückgängig machen
uv run flask db downgrade

# Aktuellen Stand prüfen
uv run flask db current
```

---

## Tests

```bash
uv run pytest

# Mit Coverage
uv run pytest --cov=app
```

## Linting

[Ruff](https://docs.astral.sh/ruff/) ist als Dev-Dependency konfiguriert.

```bash
# Linting
uv run ruff check .

# Auto-fix (Import-Sortierung, unused imports, etc.)
uv run ruff check . --fix

# Formatierung
uv run ruff format .
```

---

## Neuen Widget-Typ integrieren

Das Widget-System ist plugin-artig aufgebaut. Ein neues Widget besteht aus einer Widget-Klasse, eigenen Routes und optional einem Service. Alle fünf Schritte sind nötig.

### Schritt 1 — Verzeichnis anlegen

```
app/widgets/
└── meinwidget/
    ├── __init__.py   (leer)
    ├── widget.py     (Widget-Klasse)
    ├── routes.py     (Flask-Blueprint)
    └── service.py    (Business-Logik, optional)
```

### Schritt 2 — Widget-Klasse erstellen


```python
from app.widgets.base import BaseWidget


class MeinWidget(BaseWidget):
    key = 'meinwidget'           # eindeutiger Bezeichner, wird als Blueprint-Name verwendet
    display_name = 'Mein Widget'
    description = 'Kurze Beschreibung was das Widget tut'

    def register_routes(self, flask_app) -> None:
        from .routes import bp
        flask_app.register_blueprint(bp)
```

`key` muss eindeutig sein und darf nur Kleinbuchstaben und Bindestriche enthalten. Er wird als Blueprint-Name registriert — der `@require_widget_permission`-Decorator liest darüber den Widget-Typ.

### Schritt 3 — Routes erstellen

`app/widgets/meinwidget/routes.py`:

```python
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.utils import require_widget_permission, validate_schema
from app.widgets.meinwidget.service import MeinWidgetService

# Blueprint-Name MUSS mit widget.key übereinstimmen
bp = Blueprint('meinwidget', __name__, url_prefix='/api/families')


@bp.route('/<int:family_id>/meinwidget', methods=['GET'])
@jwt_required()
@require_widget_permission('can_view')
def get_data(family_id):
    return jsonify({'data': MeinWidgetService.get_data(family_id)}), 200


@bp.route('/<int:family_id>/meinwidget', methods=['POST'])
@jwt_required()
@require_widget_permission('can_edit')
def create_entry(family_id):
    data = request.get_json()
    entry = MeinWidgetService.create_entry(family_id, data)
    return jsonify(entry.to_dict()), 201
```

> Der Blueprint-Name (`Blueprint('meinwidget', ...)`) **muss** mit `widget.key` übereinstimmen, damit `@require_widget_permission` den richtigen Widget-Typ aus der Datenbank laden kann.

### Schritt 4 — Widget registrieren

In `app/widgets/__init__.py` das neue Widget importieren und zur Liste hinzufügen:

```python
from app.widgets.meinwidget.widget import MeinWidget

def get_widget_instances() -> list[BaseWidget]:
    return [
        TimetableWidget(),
        TodoWidget(),
        WeatherWidget(),
        ChatWidget(),
        MeinWidget(),   # <-- neu
    ]
```

### Schritt 5 — DB synchronisieren

```bash
uv run flask sync-widgets
```

Dieser Befehl trägt den neuen `WidgetType` in die Datenbank ein und erstellt für alle bestehenden Familien automatisch die Widget-Einträge und Standard-Berechtigungen.

### Standard-Berechtigungen anpassen (optional)

`BaseWidget.get_default_permissions` bestimmt welche Berechtigungen neue Familienmitglieder beim Beitritt bekommen. Standard: Familyadmin bekommt `can_view + can_edit`, Guest nur `can_view`. Überschreiben in der Widget-Klasse:

```python
def get_default_permissions(self, role_name: str) -> dict:
    # Beispiel: alle dürfen bearbeiten
    return {'can_view': True, 'can_edit': True}
```

---

## Authentifizierung

Login gibt ein JWT als HTTP-only Cookie zurück. Das Cookie wird bei allen folgenden Requests automatisch mitgeschickt — kein manuelles Setzen von Headern nötig.

## Docker Compose

```bash
docker compose up -d          # Datenbank starten
docker compose down           # Stoppen
docker compose down -v        # Stoppen inkl. Daten löschen
docker compose logs -f        # Logs verfolgen
```
