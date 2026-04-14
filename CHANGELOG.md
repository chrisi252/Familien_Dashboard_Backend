# Backend API Changes — Breaking Changes for Frontend

## Weather Widget URL Change

The weather widget URLs have moved from a standalone prefix to the `/api/families` namespace for consistency with all other widgets.

| Old URL | New URL |
|---------|---------|
| `GET /api/weather/{familyId}` | `GET /api/families/{familyId}/weather` |
| `GET /api/weather/{familyId}/location` | `GET /api/families/{familyId}/weather/location` |
| `PUT /api/weather/{familyId}/location` | `PUT /api/families/{familyId}/weather/location` |

**Action required:** Update `weather-service.ts` to use the new paths:

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

## Health Check URL Change

| Old URL | New URL |
|---------|---------|
| `GET /api/example/health` | `GET /api/health` |

If the frontend calls the health endpoint, update the path.

## Error Messages — All English

All API error messages are now in English. If the frontend displays error strings from the `error` field directly to the user, they will now appear in English instead of the previous German/English mix.

Examples:

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

If the frontend matches on specific error strings (e.g. to show translated messages), those need to be updated.

## No Other Route Changes

All other endpoints remain unchanged. Request/response schemas are identical.
