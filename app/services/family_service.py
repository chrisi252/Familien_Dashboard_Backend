from app import db
from app.models import Family, UserFamilyRole, Role, User, FamilyWidget, WidgetUserPermission


class FamilyService:

    @staticmethod
    def get_family_by_id(family_id):
        return Family.query.get(family_id)

    @staticmethod
    def create_family(family_name, creator_user_id):
        if not family_name or not family_name.strip():
            raise ValueError('Family name is required')

        creator = User.query.get(creator_user_id)
        if not creator:
            raise ValueError('User not found')

        family = Family(name=family_name.strip())

        try:
            db.session.add(family)
            db.session.flush()

            family_admin_role = Role.query.filter_by(name='Familyadmin').first()
            if not family_admin_role:
                raise ValueError('Role Familyadmin not found in database')

            user_family_role = UserFamilyRole(
                user_id=creator_user_id,
                family_id=family.id,
                role_id=family_admin_role.id
            )
            db.session.add(user_family_role)
            db.session.commit()
            return family
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def add_user_to_family(user_id, family_id, role_name=None):
        if role_name is None:
            role_name = 'Guest'

        user = User.query.get(user_id)
        if not user:
            raise ValueError('User not found')

        family = Family.query.get(family_id)
        if not family:
            raise ValueError('Family not found')

        existing = UserFamilyRole.query.filter_by(
            user_id=user_id,
            family_id=family_id
        ).first()
        if existing:
            raise ValueError('User is already member of this family')

        role = Role.query.filter_by(name=role_name).first()
        if not role:
            raise ValueError(f'Role {role_name} not found in database')

        user_family_role = UserFamilyRole(
            user_id=user_id,
            family_id=family_id,
            role_id=role.id
        )

        try:
            db.session.add(user_family_role)
            db.session.flush()

            # Widget-Permissions für alle aktiven Widgets anlegen
            from app.widgets import registry
            active_widgets = FamilyWidget.query.filter_by(
                family_id=family_id, is_enabled=True
            ).all()
            for family_widget in active_widgets:
                widget_key = family_widget.widget_type.key if family_widget.widget_type else None
                widget_instance = registry.get(widget_key) if widget_key else None
                defaults = widget_instance.get_default_permissions(role_name) if widget_instance else {
                    'can_view': True, 'can_edit': False
                }
                if role_name == 'Familyadmin':
                    defaults['can_view'] = True
                db.session.add(WidgetUserPermission(
                    family_widget_id=family_widget.id,
                    user_id=user_id,
                    can_view=defaults['can_view'],
                    can_edit=defaults['can_edit'],
                ))

            db.session.commit()
            return user_family_role
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def is_member(user_id, family_id):
        return UserFamilyRole.query.filter_by(
            user_id=user_id,
            family_id=family_id
        ).first() is not None

    @staticmethod
    def get_family_members(family_id):
        family = Family.query.get(family_id)
        if not family:
            raise ValueError('Family not found')
        
        return UserFamilyRole.query.filter_by(family_id=family_id).all()

    @staticmethod
    def get_user_families(user_id):
        user = User.query.get(user_id)
        if not user:
            raise ValueError('User not found')
        
        return UserFamilyRole.query.filter_by(user_id=user_id).all()

    @staticmethod
    def remove_user_from_family(user_id, family_id):
        user_family_role = UserFamilyRole.query.filter_by(
            user_id=user_id,
            family_id=family_id
        ).first()
        
        if not user_family_role:
            raise ValueError('User is not member of this family')
        
        try:
            db.session.delete(user_family_role)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def delete_family(family_id):
        family = Family.query.get(family_id)
        if not family:
            raise ValueError('Family not found')
        
        try:
            db.session.delete(family)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
