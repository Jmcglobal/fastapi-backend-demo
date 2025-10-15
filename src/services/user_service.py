from sqlmodel import Session, select
from src.models.user import User
from src.schemas import SignupSchema, UpdateUserSchema
from typing import Optional, List


class UserService:
    @staticmethod
    def create_user(session: Session, user_data: SignupSchema) -> User:
        """
        Create a new user and save directly to database.
        """
        # Create user object
        user = User(
            name=user_data.name,
            email=user_data.email,
            phone_number=user_data.phone_number,
            country=user_data.country,
            state=user_data.state
        )
        
        # Save to database
        session.add(user)
        session.commit()
        session.refresh(user)
        
        return user
    
    @staticmethod
    def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
        """Get user by ID (not cached)"""
        statement = select(User).where(User.id == user_id)
        user = session.exec(statement).first()
        return user
    
    @staticmethod
    def get_all_users(session: Session) -> List[User]:
        """Get all users"""
        statement = select(User)
        users = session.exec(statement).all()
        return list(users)
    
    @staticmethod
    def get_user_by_email(session: Session, email: str) -> Optional[User]:
        """Get user by email"""
        statement = select(User).where(User.email == email)
        return session.exec(statement).first()
    
    @staticmethod
    def get_user_by_phone(session: Session, phone_number: str) -> Optional[User]:
        """Get user by phone number"""
        statement = select(User).where(User.phone_number == phone_number)
        return session.exec(statement).first()
    
    @staticmethod
    def update_user(session: Session, user_id: int, user_data: UpdateUserSchema) -> User:
        """
        Update existing user information.
        Checks for uniqueness of email and phone_number if being updated.
        """
        # Get existing user
        statement = select(User).where(User.id == user_id)
        user = session.exec(statement).first()
        
        if not user:
            return None
        
        # Check email uniqueness if being updated
        if user_data.email is not None and user_data.email != user.email:
            existing_email = session.exec(
                select(User).where(User.email == user_data.email)
            ).first()
            if existing_email:
                raise ValueError("Email already exists")
        
        # Check phone uniqueness if being updated
        if user_data.phone_number is not None and user_data.phone_number != user.phone_number:
            existing_phone = session.exec(
                select(User).where(User.phone_number == user_data.phone_number)
            ).first()
            if existing_phone:
                raise ValueError("Phone number already exists")
        
        # Update fields if provided
        if user_data.name is not None:
            user.name = user_data.name
        
        if user_data.email is not None:
            user.email = user_data.email
        
        if user_data.phone_number is not None:
            user.phone_number = user_data.phone_number
        
        # Save changes
        session.add(user)
        session.commit()
        session.refresh(user)
        
        return user
