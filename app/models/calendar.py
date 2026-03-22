"""Calendar Models"""
from app import db
from datetime import datetime


class CalendarEvent(db.Model):
    """Calendar event model"""
    __tablename__ = 'calendar_events'

    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id', ondelete='CASCADE'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=True)
    is_all_day = db.Column(db.Boolean, default=False)
    is_public_to_family = db.Column(db.Boolean, default=False)
    color = db.Column(db.String(7), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    family = db.relationship('Family', backref=db.backref('calendar_events', cascade='all, delete-orphan'))
    creator = db.relationship('User', backref='created_events')
    visibility = db.relationship('CalendarEventVisibility', back_populates='event', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'family_id': self.family_id,
            'created_by': self.created_by,
            'title': self.title,
            'description': self.description,
            'start_datetime': self.start_datetime.isoformat(),
            'end_datetime': self.end_datetime.isoformat() if self.end_datetime else None,
            'is_all_day': self.is_all_day,
            'is_public_to_family': self.is_public_to_family,
            'color': self.color,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

    def __repr__(self):
        return f'<CalendarEvent {self.title}>'


class CalendarEventVisibility(db.Model):
    """Controls which users can see a calendar event"""
    __tablename__ = 'calendar_event_visibility'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('calendar_events.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    event = db.relationship('CalendarEvent', back_populates='visibility')
    user = db.relationship('User', backref='calendar_visibility')

    __table_args__ = (
        db.UniqueConstraint('event_id', 'user_id', name='uq_event_user_visibility'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'user_id': self.user_id,
        }
