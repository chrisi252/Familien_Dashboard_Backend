from app import db
from app.models import User
from werkzeug.security import generate_password_hash


class UserService:
    """Service layer for user-related business logic"""

    @staticmethod
    def get_all_users():
        """Retrieve all users from database"""
        return User.query.all()

    @staticmethod
    def get_user_by_id(user_id):
        """Retrieve a single user by ID"""
        return User.query.get(user_id)

    @staticmethod
    def create_user(username, password, first_name, last_name, is_active=True):
        """Create and persist a new user"""
        if not username or not username.strip():
            raise ValueError('Username is required')
        if not password:
            raise ValueError('Password is required')
        if not first_name or not first_name.strip():
            raise ValueError('First name is required')
        if not last_name or not last_name.strip():
            raise ValueError('Last name is required')

        normalized_username = username.strip()
        if User.query.filter_by(username=normalized_username).first():
            raise ValueError('Username already exists')

        user = User(
            username=normalized_username,
            password_hash=generate_password_hash(password),
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            is_active=bool(is_active)
        )

        try:
            db.session.add(user)
            db.session.commit()
            return user
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def delete_user(user_id):
        """Delete a user by ID"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError('User not found')

        try:
            db.session.delete(user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

