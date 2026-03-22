"""Calendar Service"""
from app import db
from app.models import CalendarEvent, CalendarEventVisibility
from sqlalchemy import or_


class CalendarService:

    @staticmethod
    def create_event(family_id, created_by, title, start_datetime,
                     description=None, end_datetime=None, is_all_day=False,
                     is_public_to_family=False, color=None):
        try:
            event = CalendarEvent(
                family_id=family_id,
                created_by=created_by,
                title=title,
                description=description,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                is_all_day=is_all_day,
                is_public_to_family=is_public_to_family,
                color=color,
            )
            db.session.add(event)
            db.session.commit()
            return event
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def get_events_for_user(family_id, user_id):
        """Return all events the user is allowed to see in a family."""
        events = CalendarEvent.query.filter_by(family_id=family_id).filter(
            or_(
                CalendarEvent.is_public_to_family == True,
                CalendarEvent.created_by == user_id,
                CalendarEvent.visibility.any(CalendarEventVisibility.user_id == user_id),
            )
        ).order_by(CalendarEvent.start_datetime.asc()).all()
        return events

    @staticmethod
    def get_event_by_id(event_id, user_id):
        """Return event if user is allowed to see it."""
        event = CalendarEvent.query.get(event_id)
        if not event:
            return None
        can_see = (
            event.is_public_to_family
            or event.created_by == user_id
            or any(v.user_id == user_id for v in event.visibility)
        )
        if not can_see:
            return None
        return event

    @staticmethod
    def update_event(event_id, user_id, **kwargs):
        event = CalendarEvent.query.get(event_id)
        if not event:
            raise ValueError('Event not found')
        if event.created_by != user_id:
            raise ValueError('Only the creator can update this event')
        allowed_fields = {'title', 'description', 'start_datetime', 'end_datetime',
                          'is_all_day', 'is_public_to_family', 'color'}
        try:
            for key, value in kwargs.items():
                if key in allowed_fields:
                    setattr(event, key, value)
            db.session.commit()
            return event
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def delete_event(event_id, user_id):
        event = CalendarEvent.query.get(event_id)
        if not event:
            raise ValueError('Event not found')
        if event.created_by != user_id:
            raise ValueError('Only the creator can delete this event')
        try:
            db.session.delete(event)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def set_visibility(event_id, user_id, visible_user_ids):
        """Replace visibility list for an event (only creator can do this)."""
        event = CalendarEvent.query.get(event_id)
        if not event:
            raise ValueError('Event not found')
        if event.created_by != user_id:
            raise ValueError('Only the creator can set visibility')
        try:
            CalendarEventVisibility.query.filter_by(event_id=event_id).delete()
            for uid in visible_user_ids:
                entry = CalendarEventVisibility(event_id=event_id, user_id=uid)
                db.session.add(entry)
            db.session.commit()
            return event
        except Exception:
            db.session.rollback()
            raise
