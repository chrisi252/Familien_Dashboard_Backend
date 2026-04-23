"""Chat Widget SocketIO Events.

Rooms: 'family_{family_id}' — one room per family.
Online tracking: family_online[family_id] = {user_id: {sid, first_name, last_name}}

Auth: JWT is read from the HTTP-only cookie sent automatically by the browser
via withCredentials. We use flask_jwt_extended.decode_token to validate it.
"""
from flask import request
from flask_jwt_extended import decode_token
from flask_socketio import emit, join_room, leave_room

from app import db
from app.models import ChatMessage, FamilyWidget, User, UserFamilyRole, WidgetType, WidgetUserPermission

# family_id -> {user_id -> {sid, first_name, last_name}}
family_online: dict[int, dict[int, dict]] = {}


def _get_user_from_cookie() -> User | None:
    token = request.cookies.get('access_token_cookie')
    if not token:
        return None
    try:
        data = decode_token(token)
        user_id = int(data['sub'])
        return User.query.get(user_id)
    except Exception:
        return None


def _get_family_id() -> int | None:
    raw = request.args.get('family_id')
    try:
        return int(raw) if raw else None
    except ValueError:
        return None


def _has_widget_permission(user_id: int, family_id: int, permission: str) -> bool:
    family_widget = (
        FamilyWidget.query
        .join(WidgetType)
        .filter(FamilyWidget.family_id == family_id, WidgetType.key == 'chat')
        .first()
    )
    if not family_widget:
        return False
    perm = WidgetUserPermission.query.filter_by(
        family_widget_id=family_widget.id, user_id=user_id
    ).first()
    return bool(perm and getattr(perm, permission))


def _room(family_id: int) -> str:
    return f'family_{family_id}'


def _online_list(family_id: int) -> list[dict]:
    members = family_online.get(family_id, {})
    return [
        {'user_id': uid, 'first_name': info['first_name'], 'last_name': info['last_name']}
        for uid, info in members.items()
    ]


def register_events(socketio) -> None:

    @socketio.on('connect', namespace='/chat')
    def on_connect():
        user = _get_user_from_cookie()
        family_id = _get_family_id()

        if not user or not family_id:
            return False

        membership = UserFamilyRole.query.filter_by(
            user_id=user.id, family_id=family_id
        ).first()
        if not membership:
            return False

        if not _has_widget_permission(user.id, family_id, 'can_view'):
            return False

        join_room(_room(family_id))

        if family_id not in family_online:
            family_online[family_id] = {}
        family_online[family_id][user.id] = {
            'sid': request.sid,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }

        emit('online_members', _online_list(family_id), room=_room(family_id), namespace='/chat')

    @socketio.on('disconnect', namespace='/chat')
    def on_disconnect():
        for family_id, members in list(family_online.items()):
            for uid, info in list(members.items()):
                if info['sid'] == request.sid:
                    del family_online[family_id][uid]
                    leave_room(_room(family_id))
                    emit('online_members', _online_list(family_id),
                         room=_room(family_id), namespace='/chat')
                    return

    @socketio.on('send_message', namespace='/chat')
    def on_send_message(data):
        user = _get_user_from_cookie()
        family_id = _get_family_id()

        if not user or not family_id:
            return

        if not _has_widget_permission(user.id, family_id, 'can_edit'):
            return

        text = (data.get('text') or '').strip()
        if not text or len(text) > 1000:
            return

        membership = UserFamilyRole.query.filter_by(
            user_id=user.id, family_id=family_id
        ).first()
        if not membership:
            return

        msg = ChatMessage(family_id=family_id, user_id=user.id, text=text)
        db.session.add(msg)
        db.session.commit()

        # Keep only the last 10 messages per family — delete older ones
        old_ids = (
            db.session.query(ChatMessage.id)
            .filter_by(family_id=family_id)
            .order_by(ChatMessage.created_at.desc())
            .offset(10)
            .all()
        )
        if old_ids:
            ChatMessage.query.filter(
                ChatMessage.id.in_([r[0] for r in old_ids])
            ).delete(synchronize_session=False)
            db.session.commit()

        emit('new_message', msg.to_dict(), room=_room(family_id), namespace='/chat')
