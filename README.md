# Familien-Dashboard Backend

REST API für das Familien-Dashboard. Gebaut mit Flask, PostgreSQL und JWT-Authentifizierung über HTTP-only Cookies.

## Technologie-Stack

| Komponente | Technologie |
|---|---|
| Framework | Flask 3.x |
| Datenbank | PostgreSQL (via SQLAlchemy + psycopg) |
| Migrationen | Flask-Migrate (Alembic) |
| Authentifizierung | JWT in HTTP-only Cookies |
| Package Manager | [uv](https://docs.astral.sh/uv/) |

## Projektstruktur

```
app/
├── __init__.py          # App-Factory (create_app)
├── models/              # SQLAlchemy-Modelle
├── services/            # Business-Logik
├── routes/              # Blueprint-Router
│   ├── user/            # /api/users
│   ├── family/          # /api/families
│   ├── widget/          # /api/families (Widget-Endpoints)
│   └── admin/           # /api/admin
├── widgets/             # Widget-System
│   ├── base.py          # Abstrakte Basisklasse
│   ├── registry.py      # Widget-Registrierung & DB-Sync
│   ├── todo/
│   ├── weather/
│   └── timetable/
└── utils/
    └── decorators.py
```

## Lokaler Start

### Voraussetzungen

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) (`pip install uv` oder `brew install uv`)
- Docker oder Podman

### 1. Umgebungsvariablen konfigurieren

Erstelle eine `.env`-Datei im Backend-Verzeichnis:

```env
# Datenbank
POSTGRES_USER=dashboard
POSTGRES_PASSWORD=password
POSTGRES_DB=dashboard
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg://dashboard:password@localhost:5432/dashboard

# JWT
JWT_SECRET_KEY=dein-geheimer-schluessel

# Optionale Widgets
OPENWEATHER_API_KEY=

# Initialer Systemadmin (wird beim ersten `sync-widgets` angelegt)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin
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

## Tests

```bash
uv run pytest

# Mit Coverage
uv run pytest --cov=app
```

## Neue Ressource anlegen

1. Model → `app/models/<name>.py` + Export in `app/models/__init__.py`
2. Service → `app/services/<name>_service.py` + Export in `app/services/__init__.py`
3. Routes → `app/routes/<name>/<name>_routes.py` + Blueprint registrieren in `app/__init__.py`
4. Migration erstellen und anwenden

## Authentifizierung

Login gibt ein JWT als HTTP-only Cookie zurück. Das Cookie wird bei allen folgenden Requests automatisch mitgeschickt — kein manuelles Setzen von Headern nötig.

## Docker Compose

```bash
docker compose up -d          # Datenbank starten
docker compose down           # Datenbank stoppen
docker compose down -v        # Datenbank inkl. Daten löschen
docker compose logs -f        # Logs verfolgen
```
