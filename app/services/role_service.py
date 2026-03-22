from app.models import UserFamilyRole, Role


class RoleService:

    @staticmethod
    def get_user_role(user_id, family_id):
        """Return the role name of a user in a family, or None if not a member."""
        entry = UserFamilyRole.query.filter_by(
            user_id=user_id,
            family_id=family_id
        ).first()
        if not entry:
            return None
        return entry.role.name

    @staticmethod
    def is_family_admin(user_id, family_id):
        """Return True if the user is Familyadmin in the given family."""
        return RoleService.get_user_role(user_id, family_id) == 'Familyadmin'

    @staticmethod
    def is_member(user_id, family_id):
        """Return True if the user is any member of the given family."""
        return UserFamilyRole.query.filter_by(
            user_id=user_id,
            family_id=family_id
        ).first() is not None
