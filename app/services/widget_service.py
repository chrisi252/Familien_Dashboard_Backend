from app import db
from app.models import FamilyWidget, WidgetRolePermission
from sqlalchemy.orm import contains_eager
from sqlalchemy import and_


class WidgetService:
    """ Service layer for widget-related business logic """

    @staticmethod
    def get_widgets_with_role_permissions(family_id, role_id):
        """ 
        Get all widgets for a family with permissions for a specific role.
        Uses SQL filtering to load only the relevant role's permissions.
        """

        return (FamilyWidget.query
                .filter_by(family_id=family_id)
                .join(FamilyWidget.widget_type)
                .outerjoin(
                    WidgetRolePermission,
                    and_(
                        WidgetRolePermission.family_widget_id == FamilyWidget.id,
                        WidgetRolePermission.role_id == role_id
                    )
                )
                .options(contains_eager(FamilyWidget.permissions))
                .all())
