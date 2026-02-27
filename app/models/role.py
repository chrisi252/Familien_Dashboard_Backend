"""Role Model"""
from app import db


class Role(db.Model):
    """Role model for user roles"""
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    # Relationships
    user_family_roles = db.relationship(
        'UserFamilyRole', back_populates='role')
    widget_permissions = db.relationship(
        'WidgetRolePermission', back_populates='role')

    def to_dict(self):
        """Convert role object to dictionary"""
        return {
            'id': self.id,
            'name': self.name
        }

    def __repr__(self):
        return f'<Role {self.name}>'
