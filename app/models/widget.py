"""Widget Models"""
from app import db


class WidgetType(db.Model):
    """WidgetType model - Defines available widget types"""
    __tablename__ = 'widget_types'

    id = db.Column(db.Integer, primary_key=True)
    # e.g., 'todo', 'weather', 'calendar'
    key = db.Column(db.String(100), unique=True, nullable=False)
    display_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    # Relationships
    family_widgets = db.relationship(
        'FamilyWidget', back_populates='widget_type')

    def to_dict(self):
        """Convert widget type to dictionary"""
        return {
            'id': self.id,
            'key': self.key,
            'display_name': self.display_name,
            'description': self.description
        }

    def __repr__(self):
        return f'<WidgetType {self.key}>'


class FamilyWidget(db.Model):
    """FamilyWidget model - Widget instances enabled for a family"""
    __tablename__ = 'family_widgets'

    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey(
        'families.id', ondelete='CASCADE'), nullable=False)
    widget_type_id = db.Column(db.Integer, db.ForeignKey(
        'widget_types.id', ondelete='CASCADE'), nullable=False)
    is_enabled = db.Column(db.Boolean, default=True)

    # Unique constraint: Family kann ein Widget-Typ nur einmal haben
    __table_args__ = (db.UniqueConstraint(
        'family_id', 'widget_type_id', name='uq_family_widget_type'),)

    # Relationships
    family = db.relationship('Family', back_populates='widgets')
    widget_type = db.relationship(
        'WidgetType', back_populates='family_widgets')
    permissions = db.relationship(
        'WidgetRolePermission', back_populates='family_widget', cascade='all, delete-orphan')

    def to_dict(self):
        """Convert family widget to dictionary"""
        return {
            'id': self.id,
            'family_id': self.family_id,
            'widget_type_id': self.widget_type_id,
            'widget_key': self.widget_type.key if self.widget_type else None,
            'is_enabled': self.is_enabled
        }

    def __repr__(self):
        return f'<FamilyWidget family_id={self.family_id} widget_type={self.widget_type_id}>'


class WidgetRolePermission(db.Model):
    """WidgetRolePermission model - Defines role permissions for widgets"""
    __tablename__ = 'widget_role_permissions'

    id = db.Column(db.Integer, primary_key=True)
    family_widget_id = db.Column(db.Integer, db.ForeignKey(
        'family_widgets.id', ondelete='CASCADE'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey(
        'roles.id', ondelete='CASCADE'), nullable=False)

    can_view = db.Column(db.Boolean, default=True)
    can_edit = db.Column(db.Boolean, default=False)

    # Unique constraint: Role kann nur einmal für ein Widget Berechtigungen haben
    __table_args__ = (db.UniqueConstraint(
        'family_widget_id', 'role_id', name='uq_widget_role'),)

    # Relationships
    family_widget = db.relationship(
        'FamilyWidget', back_populates='permissions')
    role = db.relationship('Role', back_populates='widget_permissions')

    def to_dict(self):
        """Convert widget role permission to dictionary"""
        return {
            'id': self.id,
            'family_widget_id': self.family_widget_id,
            'role_id': self.role_id,
            'role_name': self.role.name if self.role else None,
            'can_view': self.can_view,
            'can_edit': self.can_edit
        }

    def __repr__(self):
        return f'<WidgetRolePermission widget_id={self.family_widget_id} role_id={self.role_id}>'
