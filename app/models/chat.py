"""Chat Message Model"""
from datetime import datetime

from app import db


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey(
        'families.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=False)

    text = db.Column(db.String(1000), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    family = db.relationship('Family', backref=db.backref('chat_messages', lazy=True))
    user = db.relationship('User', backref=db.backref('chat_messages', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'family_id': self.family_id,
            'user_id': self.user_id,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'text': self.text,
            'created_at': self.created_at.isoformat(),
        }
