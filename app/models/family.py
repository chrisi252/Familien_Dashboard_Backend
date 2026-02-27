"""Family and UserFamilyRole Models"""
from app import db
from datetime import datetime


class Family(db.Model):
    """Family model for grouping users"""
    __tablename__ = 'families'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user_roles = db.relationship(
        'UserFamilyRole', back_populates='family', cascade='all, delete-orphan')
    widgets = db.relationship(
        'FamilyWidget', back_populates='family', cascade='all, delete-orphan')
    todos = db.relationship(
        'Todo', back_populates='family', cascade='all, delete-orphan')

    def to_dict(self):
        """Convert family object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<Family {self.name}>'


class UserFamilyRole(db.Model):
    """UserFamilyRole model - Associates users with families and roles (RBAC)"""
    __tablename__ = 'user_family_roles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=False)
    family_id = db.Column(db.Integer, db.ForeignKey(
        'families.id', ondelete='CASCADE'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey(
        'roles.id', ondelete='CASCADE'), nullable=False)

    # Unique constraint: User kann in einer Familie nur eine Rolle haben
    __table_args__ = (db.UniqueConstraint(
        'user_id', 'family_id', name='uq_user_family'),)

    # Relationships
    user = db.relationship('User', back_populates='family_roles')
    family = db.relationship('Family', back_populates='user_roles')
    role = db.relationship('Role', back_populates='user_family_roles')

    def to_dict(self):
        """Convert user family role to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'family_id': self.family_id,
            'role_id': self.role_id,
            'role_name': self.role.name if self.role else None,
            'user_username': self.user.username if self.user else None
        }

    def __repr__(self):
        return f'<UserFamilyRole user_id={self.user_id} family_id={self.family_id} role={self.role_id}>'
