import secrets
from datetime import datetime, timedelta

from app import db
from app.models import (
    Family,
    FamilyInviteCode,
    FamilyWidget,
    Role,
    User,
    UserFamilyRole,
    UserWidgetConfig,
    WidgetType,
    WidgetUserPermission,
)

_CODE_CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'  # ohne 0/O/I/1 zur Verwechslungsvermeidung
_INVITE_CODE_LENGTH = 6
_INVITE_CODE_MAX_RETRIES = 5
_INVITE_CODE_EXPIRY_MINUTES = 2


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

        family_admin_role = _get_role_or_raise('Familyadmin')

        family = Family(name=family_name.strip())
        try:
            db.session.add(family)
            db.session.flush()

            db.session.add(UserFamilyRole(
                user_id=creator_user_id,
                family_id=family.id,
                role_id=family_admin_role.id,
            ))

            for wt in WidgetType.query.all():
                fw = _create_family_widget(family.id, wt)
                _create_widget_permission(fw.id, creator_user_id, 'Familyadmin', wt.key)

            db.session.commit()
            return family
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def add_user_to_family(user_id, family_id, role_name=None):
        if role_name is None:
            role_name = 'Guest'

        _get_user_or_raise(user_id)
        _get_family_or_raise(family_id)

        existing = UserFamilyRole.query.filter_by(user_id=user_id, family_id=family_id).first()
        if existing:
            raise ValueError('User is already a member of this family')

        role = _get_role_or_raise(role_name)

        try:
            db.session.add(UserFamilyRole(user_id=user_id, family_id=family_id, role_id=role.id))
            db.session.flush()

            for family_widget in FamilyWidget.query.filter_by(family_id=family_id).all():
                widget_key = family_widget.widget_type.key if family_widget.widget_type else None
                _create_widget_permission(family_widget.id, user_id, role_name, widget_key)

            db.session.commit()
            return UserFamilyRole.query.filter_by(user_id=user_id, family_id=family_id).first()
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def is_member(user_id, family_id):
        return UserFamilyRole.query.filter_by(
            user_id=user_id,
            family_id=family_id,
        ).first() is not None

    @staticmethod
    def get_family_members(family_id):
        _get_family_or_raise(family_id)
        return UserFamilyRole.query.filter_by(family_id=family_id).all()

    @staticmethod
    def get_user_families(user_id):
        _get_user_or_raise(user_id)
        return UserFamilyRole.query.filter_by(user_id=user_id).all()

    @staticmethod
    def remove_user_from_family(user_id, family_id):
        membership = UserFamilyRole.query.filter_by(user_id=user_id, family_id=family_id).first()
        if not membership:
            raise ValueError('User is not a member of this family')
        try:
            family_widget_ids = [
                fw.id for fw in FamilyWidget.query.filter_by(family_id=family_id).all()
            ]
            if family_widget_ids:
                WidgetUserPermission.query.filter(
                    WidgetUserPermission.user_id == user_id,
                    WidgetUserPermission.family_widget_id.in_(family_widget_ids),
                ).delete(synchronize_session=False)
                UserWidgetConfig.query.filter(
                    UserWidgetConfig.user_id == user_id,
                    UserWidgetConfig.family_widget_id.in_(family_widget_ids),
                ).delete(synchronize_session=False)

            db.session.delete(membership)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def change_user_role(user_id, family_id, role_name):
        _get_family_or_raise(family_id)
        _get_user_or_raise(user_id)

        membership = UserFamilyRole.query.filter_by(user_id=user_id, family_id=family_id).first()
        if not membership:
            raise ValueError('User is not a member of this family')

        role = _get_role_or_raise(role_name)
        if membership.role_id == role.id:
            return membership

        try:
            membership.role_id = role.id

            family_widget_ids = [
                fw.id for fw in FamilyWidget.query.filter_by(family_id=family_id).all()
            ]
            if family_widget_ids:
                WidgetUserPermission.query.filter(
                    WidgetUserPermission.user_id == user_id,
                    WidgetUserPermission.family_widget_id.in_(family_widget_ids),
                ).delete(synchronize_session='fetch')

                for family_widget in FamilyWidget.query.filter_by(family_id=family_id).all():
                    widget_key = family_widget.widget_type.key if family_widget.widget_type else None
                    _create_widget_permission(family_widget.id, user_id, role_name, widget_key)

            db.session.commit()
            return membership
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def delete_family(family_id):
        family = _get_family_or_raise(family_id)
        try:
            db.session.delete(family)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def generate_invite_code(family_id):
        _get_family_or_raise(family_id)

        existing = FamilyInviteCode.query.filter_by(family_id=family_id).first()
        if existing:
            db.session.delete(existing)
            db.session.flush()

        code = _generate_unique_code()

        invite = FamilyInviteCode(
            family_id=family_id,
            code=code,
            expires_at=datetime.utcnow() + timedelta(minutes=_INVITE_CODE_EXPIRY_MINUTES),
        )
        try:
            db.session.add(invite)
            db.session.commit()
            return invite
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def join_family_by_code(user_id, code):
        invite = FamilyInviteCode.query.filter_by(code=code.upper().strip()).first()
        if not invite:
            raise ValueError('Invalid invite code')

        if invite.is_expired():
            db.session.delete(invite)
            db.session.commit()
            raise ValueError('Invite code has expired')

        return FamilyService.add_user_to_family(user_id, invite.family_id)


# ---------------------------------------------------------------------------
# Private Hilfsfunktionen
# ---------------------------------------------------------------------------

def _get_user_or_raise(user_id):
    user = User.query.get(user_id)
    if not user:
        raise ValueError('User not found')
    return user


def _get_family_or_raise(family_id):
    family = Family.query.get(family_id)
    if not family:
        raise ValueError('Family not found')
    return family


def _get_role_or_raise(role_name: str) -> Role:
    role = Role.query.filter_by(name=role_name).first()
    if not role:
        raise ValueError(f'Role "{role_name}" not found in database')
    return role


def _create_family_widget(family_id: int, widget_type: WidgetType) -> FamilyWidget:
    fw = FamilyWidget(family_id=family_id, widget_type_id=widget_type.id)
    db.session.add(fw)
    db.session.flush()
    return fw


def _create_widget_permission(family_widget_id: int, user_id: int, role_name: str, widget_key: str | None) -> None:
    from app.widgets import registry
    widget_instance = registry.get(widget_key) if widget_key else None
    defaults = (
        widget_instance.get_default_permissions(role_name)
        if widget_instance
        else {'can_view': True, 'can_edit': False}
    )
    db.session.add(WidgetUserPermission(
        family_widget_id=family_widget_id,
        user_id=user_id,
        can_view=defaults['can_view'],
        can_edit=defaults['can_edit'],
    ))


def _generate_unique_code() -> str:
    for _ in range(_INVITE_CODE_MAX_RETRIES):
        code = ''.join(secrets.choice(_CODE_CHARS) for _ in range(_INVITE_CODE_LENGTH))
        if not FamilyInviteCode.query.filter_by(code=code).first():
            return code
    raise ValueError('Code generation failed, please try again')
