"""Widget service"""
from app import db
from app.models import FamilyWidget, WidgetType, WidgetUserPermission, UserWidgetConfig


class WidgetService:

    @staticmethod
    def get_widgets_for_user(family_id: int, user_id: int) -> list[dict]:
        perms = (
            WidgetUserPermission.query
            .join(FamilyWidget)
            .join(WidgetType)
            .filter(
                FamilyWidget.family_id == family_id,
                WidgetUserPermission.user_id == user_id,
                WidgetUserPermission.can_view,
            )
            .all()
        )

        configs: dict[int, UserWidgetConfig] = {
            c.family_widget_id: c
            for c in UserWidgetConfig.query.filter_by(user_id=user_id).all()
        }

        result = []
        for perm in perms:
            fw = perm.family_widget
            data = fw.to_dict()
            data['display_name'] = fw.widget_type.display_name
            data['description'] = fw.widget_type.description
            data['can_edit'] = perm.can_edit

            cfg = configs.get(fw.id)
            if cfg:
                data['position'] = cfg.position
                data['grid_col'] = cfg.grid_col
                data['grid_row'] = cfg.grid_row
            else:
                data['position'] = None
                data['grid_col'] = None
                data['grid_row'] = None

            result.append(data)

        result.sort(key=lambda w: (w['position'] is None, w['position']))
        return result

    @staticmethod
    def get_widget_permissions(family_id: int, family_widget_id: int) -> list[dict]:
        family_widget = FamilyWidget.query.filter_by(
            id=family_widget_id, family_id=family_id
        ).first()
        if not family_widget:
            raise ValueError('Widget nicht gefunden')

        return [perm.to_dict() for perm in family_widget.user_permissions]

    @staticmethod
    def update_user_permission(
        family_id: int,
        family_widget_id: int,
        user_id: int,
        can_view: bool,
        can_edit: bool,
    ) -> WidgetUserPermission:
        family_widget = FamilyWidget.query.filter_by(
            id=family_widget_id, family_id=family_id
        ).first()
        if not family_widget:
            raise ValueError('Widget nicht gefunden')

        perm = WidgetUserPermission.query.filter_by(
            family_widget_id=family_widget_id, user_id=user_id
        ).first()
        if not perm:
            raise ValueError('Permission-Eintrag nicht gefunden')

        perm.can_view = can_view
        perm.can_edit = can_edit
        db.session.commit()
        return perm

    @staticmethod
    def update_layout(family_id: int, user_id: int, layout: list[dict]) -> list[dict]:
        """
        layout: [{ family_widget_id, position, grid_col, grid_row }, ...]
        Replaces all UserWidgetConfig entries for this user+family.
        """
        family_widget_ids = {
            fw.id for fw in FamilyWidget.query.filter_by(family_id=family_id).all()
        }

        UserWidgetConfig.query.filter(
            UserWidgetConfig.user_id == user_id,
            UserWidgetConfig.family_widget_id.in_(family_widget_ids)
        ).delete(synchronize_session=False)

        new_configs = []
        for item in layout:
            fwid = item.get('family_widget_id')
            if fwid not in family_widget_ids:
                raise ValueError(f'Widget {fwid} gehört nicht zu Familie {family_id}')
            cfg = UserWidgetConfig(
                user_id=user_id,
                family_widget_id=fwid,
                position=item.get('position', 0),
                grid_col=item.get('grid_col', 1),
                grid_row=item.get('grid_row', 1),
            )
            db.session.add(cfg)
            new_configs.append(cfg)

        db.session.commit()
        return [c.to_dict() for c in new_configs]
