## Was macht `entrypoint.sh`?

```sh
#!/bin/sh
set -e

uv run flask db upgrade
uv run flask sync-widgets

exec uv run gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

Das Script wird beim Container-Start ausgeführt und macht drei Dinge:

1. **`flask db upgrade`** — wendet alle ausstehenden Datenbank-Migrationen an. Dadurch muss man nach einem Deployment nie manuell Migrationen ausführen.
2. **`flask sync-widgets`** — synchronisiert die registrierten Widget-Typen in die DB und legt den initialen Systemadmin an (falls Credentials in den Env-Vars gesetzt sind).
3. **`exec gunicorn ...`** — startet den Production-Server mit 4 Worker-Prozessen. `exec` ersetzt den Shell-Prozess durch gunicorn, damit Docker-Signale (SIGTERM etc.) direkt bei gunicorn ankommen.

**Brauchen wir das?** Ja. Ohne das Script müsste man Migrationen und Widget-Sync manuell nach jedem Deployment ausführen. Die Alternative wäre, diese Schritte in die `Dockerfile` (`RUN`) zu verschieben — aber das geht nicht, weil die Datenbank zur Build-Zeit noch nicht erreichbar ist. Das Script muss zur Laufzeit ausgeführt werden.

---

## Was macht `.flaskenv`?

```
FLASK_APP=app:create_app
```

Diese Datei setzt die Umgebungsvariable `FLASK_APP`, damit Flask weiß, wo die App-Factory liegt. Flask + `python-dotenv` liest `.flaskenv` automatisch beim Start.

**Wer braucht das?** Nur die lokale Entwicklung. Im Docker-Container ist `FLASK_APP` bereits als `ENV` im Dockerfile gesetzt. Lokal braucht man `.flaskenv`, damit Befehle wie `uv run flask db upgrade` oder `uv run flask sync-widgets` funktionieren, ohne jedes Mal `FLASK_APP=app:create_app` voranstellen zu müssen.

**Brauchen wir das?** Ja, für lokale Entwicklung. Die Datei enthält nur eine Zeile und spart bei jedem Flask-CLI-Aufruf das manuelle Setzen der Variable.

---

## Unnötige Dependencies?

| Package | Nötig? | Grund |
|---------|--------|-------|
| `psycopg>=3.3.3` | **Nein** | psycopg 3 wird nicht genutzt. `DATABASE_URL` in `.env` und `docker-compose.yml` nutzt `postgresql://` — das ist der `psycopg2`-Driver. |
| `pyjwt>=2.11.0` | **Nein** | `flask-jwt-extended` bringt PyJWT bereits als transitive Dependency mit. Manuell listen ist redundant. |
| `python-dotenv>=1.2.1` | **Nein** | Flask lädt `python-dotenv` automatisch wenn es installiert ist. Aber: es ist eine transitive Dependency von Flask selbst (optional). Explizit zu listen schadet nicht, ist aber streng genommen unnötig, da Flask es als Extra mitbringt. Kann bleiben. |
| Alle anderen | **Ja** | Werden direkt genutzt. |

**Fazit:** `psycopg` und `pyjwt` können entfernt werden.
