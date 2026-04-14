"""Tests for TodoService"""
import pytest

from app.widgets.todo.service import TodoService
from app.models import Todo
from tests.conftest import make_user, make_family
from app.services.family_service import FamilyService


class TestGetTodos:

    def test_returns_todos_for_family(self, db_transaction):
        user = make_user()
        family = FamilyService.create_family('Familie', user.id)
        TodoService.create_todo(family.id, 'Einkaufen')
        TodoService.create_todo(family.id, 'Aufräumen')

        todos = TodoService.get_todos(family.id)

        assert len(todos) == 2

    def test_returns_empty_list_for_family_without_todos(self, db_transaction):
        family = make_family()

        todos = TodoService.get_todos(family.id)

        assert todos == []

    def test_does_not_return_todos_from_other_family(self, db_transaction):
        user_a = make_user(username='a')
        user_b = make_user(username='b')
        family_a = FamilyService.create_family('FamilieA', user_a.id)
        family_b = FamilyService.create_family('FamilieB', user_b.id)
        TodoService.create_todo(family_b.id, 'Geheimnis')

        todos = TodoService.get_todos(family_a.id)

        assert len(todos) == 0

    def test_newest_todo_comes_first(self, db_transaction):
        family = make_family()
        TodoService.create_todo(family.id, 'Erster')
        TodoService.create_todo(family.id, 'Zweiter')

        todos = TodoService.get_todos(family.id)

        assert todos[0]['title'] == 'Zweiter'


class TestCreateTodo:

    def test_creates_todo_with_title(self, db_transaction):
        family = make_family()
        todo = TodoService.create_todo(family.id, 'Milch kaufen')

        assert todo.id is not None
        assert todo.title == 'Milch kaufen'
        assert todo.is_completed is False

    def test_title_is_stripped(self, db_transaction):
        family = make_family()
        todo = TodoService.create_todo(family.id, '  Milch kaufen  ')

        assert todo.title == 'Milch kaufen'

    def test_empty_title_raises(self, db_transaction):
        family = make_family()
        with pytest.raises(ValueError, match='Title'):
            TodoService.create_todo(family.id, '')

    def test_whitespace_only_title_raises(self, db_transaction):
        family = make_family()
        with pytest.raises(ValueError, match='Title'):
            TodoService.create_todo(family.id, '   ')

    def test_creates_todo_with_description(self, db_transaction):
        family = make_family()
        todo = TodoService.create_todo(family.id, 'Einkaufen', description='Brot und Milch')

        assert todo.description == 'Brot und Milch'


class TestUpdateTodo:

    def test_marks_todo_as_completed(self, db_transaction):
        family = make_family()
        todo = TodoService.create_todo(family.id, 'Aufgabe')

        updated = TodoService.update_todo(todo.id, family.id, is_completed=True)

        assert updated.is_completed is True

    def test_updates_title(self, db_transaction):
        family = make_family()
        todo = TodoService.create_todo(family.id, 'Alt')

        updated = TodoService.update_todo(todo.id, family.id, title='Neu')

        assert updated.title == 'Neu'

    def test_todo_from_other_family_raises(self, db_transaction):
        family_a = make_family(name='A')
        family_b = make_family(name='B')
        todo = TodoService.create_todo(family_a.id, 'Geheimnis')

        with pytest.raises(ValueError, match='Todo not found'):
            TodoService.update_todo(todo.id, family_b.id, is_completed=True)

    def test_unknown_todo_raises(self, db_transaction):
        family = make_family()
        with pytest.raises(ValueError, match='Todo not found'):
            TodoService.update_todo(99999, family.id, is_completed=True)


class TestDeleteTodo:

    def test_deletes_todo(self, db_transaction):
        family = make_family()
        todo = TodoService.create_todo(family.id, 'Löschen')
        tid = todo.id

        TodoService.delete_todo(tid, family.id)

        assert Todo.query.get(tid) is None

    def test_todo_from_other_family_raises(self, db_transaction):
        family_a = make_family(name='A')
        family_b = make_family(name='B')
        todo = TodoService.create_todo(family_a.id, 'Geheimnis')

        with pytest.raises(ValueError, match='Todo not found'):
            TodoService.delete_todo(todo.id, family_b.id)
