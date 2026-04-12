"""Family Invite Code Model"""
from app import db
from datetime import datetime


class FamilyInviteCode(db.Model):
    __tablename__ = 'family_invite_codes'

    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey(
        'families.id', ondelete='CASCADE'), nullable=False, unique=True)
    code = db.Column(db.String(6), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

    family = db.relationship('Family', backref=db.backref(
        'invite_code', uselist=False, cascade='all, delete-orphan'))

    def is_expired(self):
        return datetime.utcnow() > self.expires_at

    def to_dict(self):
        return {
            'id': self.id,
            'family_id': self.family_id,
            'code': self.code,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
        }

    def __repr__(self):
        return f'<FamilyInviteCode family_id={self.family_id} code={self.code}>'
