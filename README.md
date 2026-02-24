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