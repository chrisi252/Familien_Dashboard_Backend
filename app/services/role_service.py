from app.models import UserFamilyRole


class RoleService:

    @staticmethod
    def get_user_role(user_id, family_id):
        entry = UserFamilyRole.query.filter_by(
            user_id=user_id,
            family_id=family_id
        ).first()
        if not entry:
            return None
        return entry.role.name

    @staticmethod
    def is_family_admin(user_id, family_id):
        return RoleService.get_user_role(user_id, family_id) == 'Familyadmin'
