"""Tests for UserService — fokus auf Verhalten und Invarianten"""
import pytest
from werkzeug.security import check_password_hash

from app.services.user_service import UserService
from tests.conftest import make_user


class TestCreateUser:

    def test_creates_user_with_correct_fields(self, db_transaction):
        user = UserService.create_user('max', 'secret', 'Max', 'Mustermann')
        assert user.id is not None
        assert user.username == 'max'
        assert user.first_name == 'Max'
        assert user.last_name == 'Mustermann'
        assert user.is_active is True

    def test_password_is_hashed_never_plaintext(self, db_transaction):
        user = UserService.create_user('max', 'secret123', 'Max', 'M')
        assert user.password_hash != 'secret123'
        assert check_password_hash(user.password_hash, 'secret123')

    def test_username_is_stripped(self, db_transaction):
        user = UserService.create_user('  max  ', 'pw', 'Max', 'M')
        assert user.username == 'max'

    def test_duplicate_username_raises(self, db_transaction):
        UserService.create_user('max', 'pw', 'Max', 'M')
        with pytest.raises(ValueError, match='already exists'):
            UserService.create_user('max', 'pw2', 'Max', 'M')

    def test_empty_username_raises(self, db_transaction):
        with pytest.raises(ValueError):
            UserService.create_user('', 'pw', 'Max', 'M')

    def test_whitespace_only_username_raises(self, db_transaction):
        with pytest.raises(ValueError):
            UserService.create_user('   ', 'pw', 'Max', 'M')

    def test_empty_password_raises(self, db_transaction):
        with pytest.raises(ValueError):
            UserService.create_user('max', '', 'Max', 'M')

    def test_empty_first_name_raises(self, db_transaction):
        with pytest.raises(ValueError):
            UserService.create_user('max', 'pw', '', 'M')

    def test_empty_last_name_raises(self, db_transaction):
        with pytest.raises(ValueError):
            UserService.create_user('max', 'pw', 'Max', '')


class TestVerifyPassword:

    def test_correct_password_returns_true(self, db_transaction):
        user = make_user(password='correct')
        assert UserService.verify_password(user, 'correct') is True

    def test_wrong_password_returns_false(self, db_transaction):
        user = make_user(password='correct')
        assert UserService.verify_password(user, 'wrong') is False

    def test_none_user_returns_false(self, db_transaction):
        assert UserService.verify_password(None, 'pw') is False

    def test_none_password_returns_false(self, db_transaction):
        user = make_user()
        assert UserService.verify_password(user, None) is False


class TestGetUser:

    def test_get_by_id_returns_user(self, db_transaction):
        user = make_user()
        found = UserService.get_user_by_id(user.id)
        assert found is not None
        assert found.id == user.id

    def test_get_by_id_unknown_returns_none(self, db_transaction):
        assert UserService.get_user_by_id(99999) is None

    def test_get_by_username_returns_user(self, db_transaction):
        make_user(username='maria')
        found = UserService.get_user_by_username('maria')
        assert found is not None
        assert found.username == 'maria'

    def test_get_by_username_strips_whitespace(self, db_transaction):
        make_user(username='maria')
        found = UserService.get_user_by_username('  maria  ')
        assert found is not None

    def test_get_by_username_none_returns_none(self, db_transaction):
        assert UserService.get_user_by_username(None) is None


class TestDeleteUser:

    def test_deletes_existing_user(self, db_transaction):
        user = make_user()
        uid = user.id
        UserService.delete_user(uid)
        assert UserService.get_user_by_id(uid) is None

    def test_delete_unknown_user_raises(self, db_transaction):
        with pytest.raises(ValueError, match='not found'):
            UserService.delete_user(99999)
