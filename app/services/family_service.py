from app import db
from app.models import Family, UserFamilyRole, Role, User


class FamilyService:
    """Service layer for family-related business logic"""

    @staticmethod
    def get_all_families():
        """Retrieve all families from database"""
        return Family.query.all()

    @staticmethod
    def get_family_by_id(family_id):
        """Retrieve a single family by ID"""
        return Family.query.get(family_id)

    @staticmethod
    def create_family(family_name, creator_user_id):
        """Create a new family and assign creator as admin
        
        Args:
            family_name: Name of the family
            creator_user_id: ID of the user creating the family
            
        Returns:
            Family object with creator assigned as admin
        """
        if not family_name or not family_name.strip():
            raise ValueError('Family name is required')
        
        # Check if creator exists
        creator = User.query.get(creator_user_id)
        if not creator:
            raise ValueError('User not found')
        
        # Create family
        family = Family(name=family_name.strip())
        
        try:
            db.session.add(family)
            db.session.flush()  # Get the ID without committing
            
            # Get Familyadmin role from database
            family_admin_role = Role.query.filter_by(name='Familyadmin').first()
            if not family_admin_role:
                raise ValueError('Role Familyadmin not found in database')
            
            # Assign creator as Familyadmin
            user_family_role = UserFamilyRole(
                user_id=creator_user_id,
                family_id=family.id,
                role_id=family_admin_role.id
            )
            db.session.add(user_family_role)
            db.session.commit()
            return family
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def add_user_to_family(user_id, family_id, role_name=None):
        """Add a user to a family with a specific role
        
        Args:
            user_id: ID of the user to add
            family_id: ID of the family
            role_name: Name of the role (default: 'Guest')
            
        Returns:
            UserFamilyRole object
        """
        # Use Guest as default role if none specified
        if role_name is None:
            role_name = 'Guest'

        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            raise ValueError('User not found')
        
        # Check if family exists
        family = Family.query.get(family_id)
        if not family:
            raise ValueError('Family not found')
        
        # Check if user is already in family
        existing = UserFamilyRole.query.filter_by(
            user_id=user_id,
            family_id=family_id
        ).first()
        if existing:
            raise ValueError('User is already member of this family')
        
        # Get role from database
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            raise ValueError(f'Role {role_name} not found in database')
        
        # Add user to family
        user_family_role = UserFamilyRole(
            user_id=user_id,
            family_id=family_id,
            role_id=role.id
        )
        
        try:
            db.session.add(user_family_role)
            db.session.commit()
            return user_family_role
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def is_member(user_id, family_id):
        """Check if a user is member of a family"""
        return UserFamilyRole.query.filter_by(
            user_id=user_id,
            family_id=family_id
        ).first() is not None

    @staticmethod
    def get_family_members(family_id):
        """Get all members of a family with their roles"""
        family = Family.query.get(family_id)
        if not family:
            raise ValueError('Family not found')
        
        return UserFamilyRole.query.filter_by(family_id=family_id).all()

    @staticmethod
    def get_user_families(user_id):
        """Get all families a user is member of"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError('User not found')
        
        return UserFamilyRole.query.filter_by(user_id=user_id).all()

    @staticmethod
    def remove_user_from_family(user_id, family_id):
        """Remove a user from a family"""
        user_family_role = UserFamilyRole.query.filter_by(
            user_id=user_id,
            family_id=family_id
        ).first()
        
        if not user_family_role:
            raise ValueError('User is not member of this family')
        
        try:
            db.session.delete(user_family_role)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def delete_family(family_id):
        """Delete a family (cascades to all related data)"""
        family = Family.query.get(family_id)
        if not family:
            raise ValueError('Family not found')
        
        try:
            db.session.delete(family)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
