"""Stundenplan Model"""
from app import db
from datetime import datetime

DEFAULT_COLOR = '#3B82F6'


class TimetableEntry(db.Model):
    __tablename__ = 'timetable_entries'

    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey(
        'families.id', ondelete='CASCADE'), nullable=False)

    person_name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(7), nullable=False, default=DEFAULT_COLOR)

    weekday = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.String(5), nullable=False)
    end_time = db.Column(db.String(5), nullable=False)

    subject = db.Column(db.String(100), nullable=False)
    room = db.Column(db.String(50))
    teacher = db.Column(db.String(100))
    note = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    family = db.relationship('Family', backref=db.backref('timetable_entries', lazy=True, cascade='all, delete-orphan'))

    __table_args__ = (
        db.CheckConstraint('weekday >= 0 AND weekday <= 4', name='ck_timetable_weekday'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'family_id': self.family_id,
            'person_name': self.person_name,
            'color': self.color,
            'weekday': self.weekday,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'subject': self.subject,
            'room': self.room,
            'teacher': self.teacher,
            'note': self.note,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

    def __repr__(self):
        return f'<TimetableEntry {self.person_name} {self.weekday} {self.start_time} {self.subject}>'
