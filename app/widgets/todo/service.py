"""Todo Widget Service"""
from app import db
from app.models import Todo


class TodoService:

    @staticmethod
    def get_todos(family_id: int) -> list[dict]:
        todos = Todo.query.filter_by(family_id=family_id).order_by(Todo.created_at.desc()).all()
        return [t.to_dict() for t in todos]

    @staticmethod
    def create_todo(family_id: int, title: str, description: str = None) -> Todo:
        if not title or not title.strip():
            raise ValueError('Title is required')
        todo = Todo(family_id=family_id, title=title.strip(), description=description)
        try:
            db.session.add(todo)
            db.session.commit()
            return todo
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def update_todo(todo_id: int, family_id: int, **kwargs) -> Todo:
        todo = Todo.query.filter_by(id=todo_id, family_id=family_id).first()
        if not todo:
            raise ValueError('Todo not found')
        if 'title' in kwargs and (not kwargs['title'] or not kwargs['title'].strip()):
            raise ValueError('Title is required')
        for field in ('title', 'description', 'is_completed'):
            if field in kwargs:
                setattr(todo, field, kwargs[field])
        try:
            db.session.commit()
            return todo
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def delete_todo(todo_id: int, family_id: int) -> None:
        todo = Todo.query.filter_by(id=todo_id, family_id=family_id).first()
        if not todo:
            raise ValueError('Todo not found')
        try:
            db.session.delete(todo)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
