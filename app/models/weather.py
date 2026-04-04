"""Weather configuration model per family"""
from app import db


class FamilyWeatherConfig(db.Model):
    __tablename__ = 'family_weather_configs'

    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey(
        'families.id', ondelete='CASCADE'), nullable=False, unique=True)
    city_name = db.Column(db.String(255), nullable=False, default='Berlin')
    latitude = db.Column(db.Float, nullable=False, default=52.52)
    longitude = db.Column(db.Float, nullable=False, default=13.405)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(),
                           onupdate=db.func.now())

    family = db.relationship('Family', backref=db.backref(
        'weather_config', uselist=False, cascade='all, delete-orphan'))

    def to_dict(self):
        return {
            'id': self.id,
            'family_id': self.family_id,
            'city_name': self.city_name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<FamilyWeatherConfig family_id={self.family_id} city={self.city_name}>'
