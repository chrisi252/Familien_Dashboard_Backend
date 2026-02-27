"""Todo Model"""
from app import db
from datetime import datetime


class Todo(db.Model):
    """Todo model - Task list for families"""
    __tablename__ = 'todos'

    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey(
        'families.id', ondelete='CASCADE'), nullable=False)

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    family = db.relationship('Family', back_populates='todos')

    def to_dict(self):
        """Convert todo to dictionary"""
        return {
            'id': self.id,
            'family_id': self.family_id,
            'title': self.title,
            'description': self.description,
            'is_completed': self.is_completed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Todo {self.title}>'
