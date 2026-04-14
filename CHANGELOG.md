# Backend Changelog

## Breaking Changes for Frontend

### Weather Widget URL Change

The weather widget URLs have moved from a standalone prefix to the `/api/families` namespace for consistency with all other widgets.

| Old URL | New URL |
|---------|---------|
| `GET /api/weather/{familyId}` | `GET /api/families/{familyId}/weather` |
| `GET /api/weather/{familyId}/location` | `GET /api/families/{familyId}/weather/location` |
| `PUT /api/weather/{familyId}/location` | `PUT /api/families/{familyId}/weather/location` |

**Action required:** Update `weather-service.ts`:

```ts
// Before
this.http.get<WeatherResponse>(`${this.apiUrl}/weather/${familyId}`);
this.http.get<...>(`${this.apiUrl}/weather/${familyId}/location`);
this.http.put<void>(`${this.apiUrl}/weather/${familyId}/location`, { city });

// After
this.http.get<WeatherResponse>(`${this.apiUrl}/families/${familyId}/weather`);
this.http.get<...>(`${this.apiUrl}/families/${familyId}/weather/location`);
this.http.put<void>(`${this.apiUrl}/families/${familyId}/weather/location`, { city });
```

### Health Check URL Change

| Old URL | New URL |
|---------|---------|
| `GET /api/example/health` | `GET /api/health` |

### Error Messages — All English

All API error messages are now consistently in English. If the frontend displays `error` strings directly or matches on them, they need to be updated.

| Before | After |
|--------|-------|
| `Keine Daten übergeben` | `No data provided` |
| `Benutzername oder Passwort ungültig` | `Invalid username or password` |
| `Kein Familienmitglied` | `Not a family member` |
| `Keine Berechtigung` | `Permission denied` |
| `Widget nicht aktiv` | `Widget not active` |
| `Nur der Familienadmin hat Zugriff` | `Only the family admin has access` |
| `Todo gelöscht` | `Todo deleted` |
| `Eintrag gelöscht` | `Entry deleted` |
| `Logout erfolgreich` | `Logout successful` |
| `Registrierung erfolgreich` | `User registered successfully` |
| `Login erfolgreich` | `Login successful` |
| `Ort erfolgreich aktualisiert` | `Location updated successfully` |
| `Admin-Account erstellt` | `Admin account created` |
| `Familie erfolgreich gelöscht` | `Family deleted successfully` |

---

## Internal Refactoring (no frontend impact)

### Clean Code

- **Duplicate widget permission logic** extracted into `_create_widget_permission()` and `_create_family_widget()` in `family_service.py`, reused by `registry.py`
- **Long functions split**: `create_family()`, `add_user_to_family()`, `fetch_weather()`, `sync_to_db()`, `create_app()`
- **Widget registration** moved from `widget.py` side-effect to explicit `register()` call in each widget's `__init__.py`
- **`example/` route directory removed** — health check integrated into `main_bp`
- **Dead exports removed** — `TodoService`, `WeatherService`, `TimetableService` no longer exported from widget `__init__.py`
- **Loose docs removed** — `database.md`, `frontend.md` deleted from project root
- **Redundant `can_view=True` override** removed from `_create_widget_permission()` (already returned by `get_default_permissions`)
- **`UserService.create_user()`** now accepts `is_system_admin` parameter — `admin_routes.py` no longer bypasses the service layer
- **Decorator imports** moved to module level in `decorators.py`
- **`registry.py` simplified** — 4 helper functions with model parameters collapsed into a flat `sync_to_db()`
- **Variable shadowing fix** — `_register_widgets(app)` renamed parameter to `flask_app` to avoid `import app.widgets.*` overwriting the Flask instance

### Build & Deployment

- **`.dockerignore` added** — excludes `.venv/`, `.git/`, `tests/`, `__pycache__/`, `*.md` from image
- **Dockerfile optimized** — `pip install uv` replaced with `COPY --from=ghcr.io/astral-sh/uv:latest` (faster, no pip needed). `FLASK_APP` set as ENV. Healthcheck added
- **`pyproject.toml` cleaned** — `pytest` moved from production to dev dependencies. Unused `postgres` package removed
- **`docker-compose.yml`** — healthcheck added for backend service (`/api/health`, 30s interval, 15s start period)

### Tests

- All error message assertions updated to match new English messages
- Weather tests now mock `OPENWEATHER_API_KEY` environment variable
