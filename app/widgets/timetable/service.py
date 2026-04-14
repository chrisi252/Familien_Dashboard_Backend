"""Stundenplan Widget Service"""
import re
from app import db
from app.models import TimetableEntry
from app.models.timetable import DEFAULT_COLOR

_TIME_RE = re.compile(r'^\d{2}:\d{2}$')
_COLOR_RE = re.compile(r'^#[0-9A-Fa-f]{6}$')
_VALID_WEEKDAYS = range(0, 5)


def _validate_time(value: str, field: str) -> None:
    if not _TIME_RE.match(value):
        raise ValueError(f'{field} muss im Format HH:MM sein')


def _validate_color(value: str) -> None:
    if not _COLOR_RE.match(value):
        raise ValueError('color muss ein gültiger Hex-Farbwert sein (z.B. #3B82F6)')


class TimetableService:

    @staticmethod
    def get_persons(family_id: int) -> list[dict]:
        """Gibt alle eindeutigen Personen (name + color) der Familie zurück."""
        rows = (
            db.session.query(TimetableEntry.person_name, TimetableEntry.color)
            .filter_by(family_id=family_id)
            .distinct()
            .all()
        )
        return [{'person_name': r.person_name, 'color': r.color} for r in rows]

    @staticmethod
    def get_entries(family_id: int, person_name: str) -> list[dict]:
        entries = (
            TimetableEntry.query
            .filter_by(family_id=family_id, person_name=person_name)
            .order_by(TimetableEntry.weekday, TimetableEntry.start_time)
            .all()
        )
        return [e.to_dict() for e in entries]

    @staticmethod
    def create_entry(family_id: int, data: dict) -> TimetableEntry:
        person_name = (data.get('person_name') or '').strip()
        subject = (data.get('subject') or '').strip()
        start_time = data.get('start_time', '')
        end_time = data.get('end_time', '')
        weekday = data.get('weekday')
        color = data.get('color', DEFAULT_COLOR)

        if not person_name:
            raise ValueError('person_name ist erforderlich')
        if not subject:
            raise ValueError('subject ist erforderlich')
        if weekday is None or weekday not in _VALID_WEEKDAYS:
            raise ValueError('weekday muss 0 (Mo) bis 4 (Fr) sein')
        _validate_time(start_time, 'start_time')
        _validate_time(end_time, 'end_time')
        if start_time >= end_time:
            raise ValueError('start_time muss vor end_time liegen')
        _validate_color(color)

        entry = TimetableEntry(
            family_id=family_id,
            person_name=person_name,
            color=color,
            weekday=weekday,
            start_time=start_time,
            end_time=end_time,
            subject=subject,
            room=data.get('room'),
            teacher=data.get('teacher'),
            note=data.get('note'),
        )
        db.session.add(entry)
        db.session.commit()
        return entry

    @staticmethod
    def update_entry(entry_id: int, family_id: int, data: dict) -> TimetableEntry:
        entry = TimetableEntry.query.filter_by(id=entry_id, family_id=family_id).first()
        if not entry:
            raise ValueError('Eintrag nicht gefunden')

        if 'person_name' in data:
            person_name = data['person_name'].strip()
            if not person_name:
                raise ValueError('person_name darf nicht leer sein')
            entry.person_name = person_name

        if 'color' in data:
            _validate_color(data['color'])
            entry.color = data['color']

        if 'weekday' in data:
            if data['weekday'] not in _VALID_WEEKDAYS:
                raise ValueError('weekday muss 0 (Mo) bis 4 (Fr) sein')
            entry.weekday = data['weekday']

        if 'start_time' in data:
            _validate_time(data['start_time'], 'start_time')
            entry.start_time = data['start_time']

        if 'end_time' in data:
            _validate_time(data['end_time'], 'end_time')
            entry.end_time = data['end_time']

        if entry.start_time >= entry.end_time:
            raise ValueError('start_time muss vor end_time liegen')

        for field in ('subject', 'room', 'teacher', 'note'):
            if field in data:
                setattr(entry, field, data[field])

        db.session.commit()
        return entry

    @staticmethod
    def delete_entry(entry_id: int, family_id: int) -> None:
        entry = TimetableEntry.query.filter_by(id=entry_id, family_id=family_id).first()
        if not entry:
            raise ValueError('Eintrag nicht gefunden')
        db.session.delete(entry)
        db.session.commit()
