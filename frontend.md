# Familien-Dashboard Backend – Übersicht für das Frontend-Team

## Authentifizierung

Die API nutzt **JWT-Tokens in HTTP-Only-Cookies**. Nach Login/Registrierung wird das Token automatisch als Cookie gesetzt – das Frontend muss kein Token manuell speichern oder in Headern mitsenden. Wichtig: Requests müssen mit `credentials: 'include'` (fetch) bzw. `withCredentials: true` (axios) gesendet werden, damit der Browser die Cookies mitschickt.

CORS erlaubt nur die in `FRONTEND_URL` konfigurierte Origin.

---

## Rollen & Berechtigungen

| Rolle | Beschreibung |
|-------|-------------|
| **Familyadmin** | Ersteller der Familie. Kann Berechtigungen verwalten und Layout ändern. Hat immer `can_view = true`. |
| **Guest** | Tritt einer Familie bei. Standard: `can_view = true`, `can_edit = false`. |

### Widget-Berechtigungen (pro User, pro Widget)

- **`can_view`** – Darf das Widget sehen und Daten lesen.
- **`can_edit`** – Darf Daten im Widget erstellen/ändern/löschen.

Alle Widgets sind automatisch für jede Familie aktiv. Es gibt kein manuelles Aktivieren/Deaktivieren. Widgets, für die ein User kein `can_view` hat, tauchen in der Widget-Liste (`GET /api/families/<id>/widgets`) **gar nicht auf**.

---

## Fehlerformat

Alle Fehler folgen diesem Schema:

```json
{
  "error": "Fehlermeldung auf Deutsch",
  "details": "Technische Details (nur bei 500ern)"
}
```

| Status | Bedeutung |
|--------|-----------|
| 200 | Erfolg (GET/PUT) |
| 201 | Ressource erstellt (POST) |
| 400 | Fehlende/ungültige Felder |
| 401 | Falsche Zugangsdaten (nur Login) |
| 403 | Kein Zugriff (kein JWT, keine Rolle, keine Permission, Account inaktiv) |
| 404 | Ressource nicht gefunden |
| 500 | Serverfehler |
| 502 | Externe API nicht erreichbar (Wetter) |

---

## Routen

### Benutzer

#### `POST /api/users/register`
Registriert einen neuen User und setzt das JWT-Cookie.

**Body:**
```json
{
  "username": "string",
  "password": "string",
  "first_name": "string",
  "last_name": "string"
}
```

**Antwort (201):**
```json
{
  "message": "User registered successfully",
  "user": { "id", "username", "first_name", "last_name", "is_active", "created_at" }
}
```

---

#### `POST /api/users/login`
Login. Setzt JWT-Cookie und gibt Familien-Zugehörigkeiten zurück.

**Body:**
```json
{ "username": "string", "password": "string" }
```

**Antwort (200):**
```json
{
  "message": "Login successful",
  "user": { "id", "username", "first_name", "last_name", "is_active", "created_at" },
  "families": [
    { "family_id": 1, "is_admin": true },
    { "family_id": 2, "is_admin": false }
  ]
}
```

| Fehler | Status |
|--------|--------|
| Username/Passwort fehlt | 400 |
| Falsche Zugangsdaten | 401 |
| Account deaktiviert | 403 |

---

#### `GET /api/users/profile`
Gibt das Profil des eingeloggten Users zurück.

**Auth:** JWT erforderlich

**Antwort (200):**
```json
{ "id", "username", "first_name", "last_name", "is_active", "created_at" }
```

---

#### `POST /api/users/logout`
Löscht das JWT-Cookie.

**Auth:** JWT erforderlich

**Antwort (200):**
```json
{ "message": "Logout erfolgreich" }
```

---

### Familien

#### `POST /api/families`
Erstellt eine Familie. Der aufrufende User wird automatisch **Familyadmin**. Alle Widgets werden automatisch angelegt mit Berechtigungen für den Admin.

**Auth:** JWT erforderlich

**Body:**
```json
{ "name": "string" }
```

**Antwort (201):**
```json
{ "id", "name", "created_at" }
```

---

#### `GET /api/families`
Gibt alle Familien des eingeloggten Users mit Rollen zurück.

**Auth:** JWT erforderlich

**Antwort (200):**
```json
[
  {
    "family": { "id", "name", "created_at" },
    "role": { "id", "name" },
    "user_family_role": { "id", "user_id", "family_id", "role_id", "role_name", "user_username" }
  }
]
```

---

#### `GET /api/families/<family_id>`
Details einer Familie inkl. aller Mitglieder.

**Auth:** JWT erforderlich (muss Mitglied sein)

**Antwort (200):**
```json
{
  "family": { "id", "name", "created_at" },
  "members": [
    { "id", "user_id", "family_id", "role_id", "role_name", "user_username" }
  ]
}
```

---

#### `POST /api/families/<family_id>/join`
User tritt einer Familie als **Guest** bei. Bekommt automatisch Widget-Berechtigungen für alle Widgets.

**Auth:** JWT erforderlich

**Antwort (200):**
```json
{ "id", "user_id", "family_id", "role_id", "role_name", "user_username" }
```

---

#### `DELETE /api/families/<family_id>`
Löscht eine Familie samt aller Daten (Mitglieder, Widgets, Todos).

**Auth:** JWT + Familyadmin

**Antwort (200):**
```json
{ "message": "Family deleted successfully" }
```

---

### Widgets

#### `GET /api/families/<family_id>/widgets`
Gibt alle Widgets zurück, für die der User `can_view` hat. Enthält Layout-Konfiguration des eingeloggten Users (`position`, `grid_col`, `grid_row`) sowie ein `can_edit`-Flag.

`position`, `grid_col` und `grid_row` sind `null`, wenn der User das Widget noch nicht zu seinem Dashboard hinzugefügt hat. Die Widgets sind bereits nach `position` aufsteigend sortiert (Widgets ohne Konfiguration am Ende).

**Auth:** JWT erforderlich

**Antwort (200):**
```json
{
  "widgets": [
    {
      "id": 1,
      "family_id": 1,
      "widget_type_id": 1,
      "widget_key": "todo",
      "display_name": "Aufgaben",
      "description": "Gemeinsame Todo-Liste für die Familie",
      "position": 0,
      "grid_col": 2,
      "grid_row": 1,
      "can_edit": true
    }
  ]
}
```

Das Frontend sollte anhand von `can_edit` entscheiden, ob Bearbeitungs-Buttons angezeigt werden.

---

#### `GET /api/families/<family_id>/widgets/<family_widget_id>/permissions`
Gibt die Berechtigungen aller Familienmitglieder für ein Widget zurück.

**Auth:** JWT + Familyadmin

**Antwort (200):**
```json
{
  "permissions": [
    { "id": 1, "family_widget_id": 2, "user_id": 3, "can_view": true, "can_edit": false }
  ]
}
```

---

#### `PUT /api/families/<family_id>/widgets/<family_widget_id>/permissions/<user_id>`
Überschreibt die Berechtigungen eines Users für ein Widget.

**Auth:** JWT + Familyadmin

**Body:**
```json
{ "can_view": true, "can_edit": false }
```

**Antwort (200):**
```json
{ "id", "family_widget_id", "user_id", "can_view", "can_edit" }
```

---

#### `PUT /api/families/<family_id>/widgets/layout`
Speichert das komplette Dashboard-Layout des eingeloggten Users. Ersetzt alle bisherigen Layout-Einträge für diese Familie atomisch.

Beim Drag & Drop oder Resize das gesamte aktuelle `addedWidgets`-Array als `layout` schicken.

**Auth:** JWT erforderlich (kein Admin nötig)

**Body:**
```json
{
  "layout": [
    { "family_widget_id": 1, "position": 0, "grid_col": 2, "grid_row": 1 },
    { "family_widget_id": 3, "position": 1, "grid_col": 1, "grid_row": 1 }
  ]
}
```

**Antwort (200):**
```json
{
  "configs": [
    { "id": 1, "user_id": 5, "family_widget_id": 1, "position": 0, "grid_col": 2, "grid_row": 1 },
    { "id": 2, "user_id": 5, "family_widget_id": 3, "position": 1, "grid_col": 1, "grid_row": 1 }
  ]
}
```

---

### Todo-Widget

Alle Todo-Routen prüfen automatisch, ob der User die entsprechende Widget-Berechtigung hat (`can_view` für Lesen, `can_edit` für Schreiben).

#### `GET /api/families/<family_id>/todos`
Gibt alle Todos der Familie zurück (neueste zuerst).

**Auth:** JWT + `can_view` auf Todo-Widget

**Antwort (200):**
```json
{
  "todos": [
    { "id", "family_id", "title", "description", "is_completed", "created_at", "updated_at" }
  ]
}
```

---

#### `POST /api/families/<family_id>/todos`
Erstellt ein neues Todo.

**Auth:** JWT + `can_edit` auf Todo-Widget

**Body:**
```json
{ "title": "Einkaufen", "description": "Milch, Brot, Käse" }
```

`description` ist optional.

**Antwort (201):**
```json
{ "id", "family_id", "title", "description", "is_completed", "created_at", "updated_at" }
```

---

#### `PUT /api/families/<family_id>/todos/<todo_id>`
Aktualisiert ein Todo. Nur übergebene Felder werden geändert.

**Auth:** JWT + `can_edit` auf Todo-Widget

**Body (alle optional):**
```json
{ "title": "Neuer Titel", "description": "Neue Beschreibung", "is_completed": true }
```

**Antwort (200):**
```json
{ "id", "family_id", "title", "description", "is_completed", "created_at", "updated_at" }
```

---

#### `DELETE /api/families/<family_id>/todos/<todo_id>`
Löscht ein Todo.

**Auth:** JWT + `can_edit` auf Todo-Widget

**Antwort (200):**
```json
{ "message": "Todo gelöscht" }
```

---

### Wetter-Widget

#### `GET /api/weather/<family_id>`
Gibt aktuelles Wetter und 5-Tage-Vorhersage zurück.

**Auth:** JWT + `can_view` auf Wetter-Widget

**Antwort (200):**
```json
{
  "location": {
    "id", "family_id", "city_name", "latitude", "longitude", "updated_at"
  },
  "current": {
    "temperature": 18.5,
    "apparent_temperature": 16.2,
    "humidity": 65,
    "wind_speed": 12.3,
    "weather_code": 802,
    "weather_description": "Wolkenfelder",
    "icon": "03d"
  },
  "forecast": [
    {
      "date": "2026-04-05",
      "weather_code": 500,
      "weather_description": "Leichter Regen",
      "icon": "10d",
      "temperature_max": 20.1,
      "temperature_min": 12.3
    }
  ]
}
```

Icons: OpenWeatherMap-Icon-IDs, verwendbar als `https://openweathermap.org/img/wn/{icon}@2x.png`

---

#### `GET /api/weather/<family_id>/location`
Gibt den konfigurierten Ort zurück. Standard: Berlin.

**Auth:** JWT + `can_view` auf Wetter-Widget

**Antwort (200):**
```json
{
  "location": { "id", "family_id", "city_name", "latitude", "longitude", "updated_at" }
}
```

---

#### `PUT /api/weather/<family_id>/location`
Ändert den Wetter-Standort. Löst Geocoding aus.

**Auth:** JWT + `can_edit` auf Wetter-Widget

**Body:**
```json
{ "city": "Mannheim" }
```

**Antwort (200):**
```json
{
  "message": "Ort erfolgreich aktualisiert",
  "location": { "id", "family_id", "city_name", "latitude", "longitude", "updated_at" }
}
```

---

## Typischer Ablauf

```
1. Register/Login  →  JWT-Cookie wird gesetzt
2. GET /api/families  →  Familien des Users laden
3. GET /api/families/<id>  →  Mitglieder einer Familie laden
4. GET /api/families/<id>/widgets  →  Widgets laden (gefiltert nach can_view)
5. Je nach Widget:
   - Todo:    GET /api/families/<id>/todos
   - Wetter:  GET /api/weather/<id>
6. Logout  →  Cookie wird gelöscht
```

### Admin-Aktionen
```
- Berechtigung ändern:  PUT /api/families/<id>/widgets/<widget_id>/permissions/<user_id>
- Wetter-Ort ändern:    PUT /api/weather/<id>/location
- Familie löschen:      DELETE /api/families/<id>
```

### User-Aktionen
```
- Dashboard-Layout speichern:  PUT /api/families/<id>/widgets/layout
```

---

## Health-Check

`GET /api/example/health` – Kein Auth nötig. Gibt `{"status": "success"}` zurück.
