from app import db
from app.models import User


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
    def create_user(name, email):
        """Create a new user"""
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            raise ValueError(f"User with email {email} already exists")

        user = User(name=name, email=email)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def delete_user(user_id):
        """Delete a user by ID"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")

        db.session.delete(user)
        db.session.commit()
        return user
