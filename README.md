# Familien_Dashboard_Backend

# 1. .env-Datei erstellen

cp .env

# 2. Datenbank starten

podman compose up -d

# 3. Anwendung starten

uv run python main.py

#

## Setup

### Voraussetzungen

- Python 3.14+
- Docker und Docker Compose
- uv (Python Package Manager)

### Installation

1. **Repository klonen**

   ```bash
   git clone <repository-url>
   cd Familien_Dashboard_Backend
   ```

2. **Umgebungsvariablen konfigurieren**

   ```bash
   cp .env.example .env
   ```

   Passe die Werte in der `.env`-Datei nach Bedarf an.

3. **Datenbank starten**

   ```bash
   docker-compose up -d
   ```

   Die PostgreSQL-Datenbank läuft nun auf Port 5432.

4. **Python Dependencies installieren**

   ```bash
   uv sync
   ```

5. **Anwendung starten**
   ```bash
   uv run python main.py
   ```
   Der Server läuft auf http://localhost:5000

### Docker Compose Befehle

- **Datenbank starten**: `docker-compose up -d`
- **Datenbank stoppen**: `docker-compose down`
- **Datenbank mit Daten löschen**: `docker-compose down -v`
- **Logs anzeigen**: `docker-compose logs -f postgres`
- **Status prüfen**: `docker-compose ps`

### Entwicklung

Die Datenbank-Verbindung wird über die `DATABASE_URL` Umgebungsvariable in der `.env`-Datei konfiguriert.

### Database Migrations

Das Projekt nutzt Flask-Migrate (Alembic) für Datenbank-Migrationen.

**Migration erstellen** (nach Model-Änderungen):

```bash
uv run flask db migrate -m "Beschreibung der Änderung"
```

**Migration anwenden**:

```bash
uv run flask db upgrade
```

**Migration rückgängig machen**:

```bash
uv run flask db downgrade
```

**Migrations-Historie anzeigen**:

```bash
uv run flask db history
```

## Neue Route anlegen

Um eine neue Ressource (z. B. `Task`) anzulegen, folgende Dateien erstellen/bearbeiten:

1. **Model erstellen**: `app/models/task.py`
2. **Model exportieren**: `app/models/__init__.py`
3. **Service erstellen**: `app/services/task_service.py`
4. **Service exportieren**: `app/services/__init__.py`
5. **Routes erstellen**: `app/routes/task/tasks.py`
6. **Blueprint exportieren**: `app/routes/task/__init__.py`
7. **Blueprint in App registrieren**: `app/__init__.py`
8. **Routes exportieren**: `app/routes/__init__.py`

Danach Migration erstellen und anwenden:

```bash
uv run flask db migrate -m "Add Task model"
uv run flask db upgrade
```


## Authorization:
- frontend -> Login Page -> backend schickt JWT Token zurück
- frontend speichert JWT Token (z.B. in localStorage)
- frontend sendet JWT Token in Authorization Header bei API Requests
- backend validiert JWT Token und gibt Zugriff auf geschützte Ressourcen

# auth
JWT als cookie schicken und auf strict setzen
- refresh token für access token

# deploy 
- docker image auf server (ssh)
https://flask.palletsprojects.com/en/stable/deploying/uwsgi/


