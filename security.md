# Security Issues

## Critical

### 1. Exception Details in API-Responses

Alle Routes geben `'details': str(e)` an den Client zurück. Das leakt interne Implementierungsdetails (DB-Struktur, Stacktraces).

**Betrifft:** Jede Route-Datei mit `except Exception as e`.

**Fix:** `details` aus allen Error-Responses entfernen. Exceptions serverseitig loggen.

---

### 2. Kein JWT Token Expiry

`app/__init__.py` — Kein `JWT_ACCESS_TOKEN_EXPIRES` konfiguriert. Default ist kein Ablauf. Ein kompromittierter Token ist ewig gültig.

**Fix:**
```python
from datetime import timedelta
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
```

---

### 3. CSRF-Schutz deaktiviert

`app/__init__.py:57` — `JWT_COOKIE_CSRF_PROTECT = False`. In Kombination mit `SameSite=Lax` sind POST-Requests von externen Seiten über Top-Level-Navigationen möglich.

**Fix:** `JWT_COOKIE_CSRF_PROTECT = True` und `SameSite=Strict` setzen. Frontend muss CSRF-Token mitsenden.

---

### 4. Kein Rate Limiting auf Login/Register

`/api/users/login` und `/api/users/register` haben kein Rate Limiting. Brute-Force auf Passwörter und Massen-Account-Erstellung sind möglich.

**Fix:** `flask-limiter` einführen, z.B. 5 Login-Versuche pro Minute.

---

## High

### 5. Keine Passwort-Validierung

`user_service.py:16` — Prüft nur `if not password`. Passwörter wie `"a"` oder `"123"` sind erlaubt.

**Fix:** Mindestlänge (z.B. 8 Zeichen) und Komplexitätsregeln einführen.

---

### 6. Default Admin-Credentials in docker-compose.yml

```yaml
ADMIN_USERNAME: ${ADMIN_USERNAME:-admin}
ADMIN_PASSWORD: ${ADMIN_PASSWORD:-Admin1234!}
```

Ohne gesetzte Env-Vars läuft die App mit bekannten Default-Credentials.

**Fix:** Defaults entfernen, Variablen als required behandeln.

---

### 7. Fehlende Membership-Prüfung auf GET /widgets

`widget_routes.py:9-17` — `get_widgets` prüft nicht ob der User Mitglied der Familie ist. Der Service gibt zwar nur Widgets mit `can_view=true` zurück (leeres Array für Nicht-Mitglieder), aber die Route sollte Zugriff explizit verweigern.

**Fix:** `FamilyService.is_member()` Check vor dem Service-Aufruf.

---

## Medium

### 8. Keine Security Headers

Keine `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security` oder `Content-Security-Policy` Header gesetzt.

**Fix:** `@app.after_request` Handler mit Security Headers.

---

### 9. Kein Audit-Logging

Kein Logging von Login-Versuchen, Admin-Aktionen, Familien-Löschungen oder Permission-Änderungen.

**Fix:** `logging` in Services und Routes einführen.

---

### 10. Request Size nicht limitiert

Kein `MAX_CONTENT_LENGTH` konfiguriert. Große Payloads können den Server belasten.

**Fix:**
```python
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1 MB
```

---

## Low

### 11. Invite-Code Brute-Force

6 Zeichen aus 32 Zeichen = ~1 Milliarde Kombinationen. Ohne Rate Limiting auf `/join-by-code` theoretisch durchsuchbar. Die 2-Minuten-Expiry hilft, aber Rate Limiting fehlt.

**Fix:** Code-Länge auf 8 erhöhen und/oder Rate Limiting auf den Endpoint.

---

### 12. Gunicorn ohne Timeout

`entrypoint.sh` — Gunicorn läuft ohne `--timeout`. Hängende Requests blockieren Worker dauerhaft.

**Fix:**
```sh
exec uv run gunicorn -w 4 -b 0.0.0.0:5000 --timeout 30 "app:create_app()"
```
