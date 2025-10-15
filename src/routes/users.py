from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from src.database import get_session
from src.schemas import SignupSchema, UserResponse, UserWithContentsResponse, UpdateUserSchema
from src.services.user_service import UserService
from typing import List

router = APIRouter(prefix="/api/v1", tags=["users"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: SignupSchema, session: Session = Depends(get_session)):
    """
    Create a new user account.
    Writes to Redis first, then immediately saves to database.
    """
    # Check if email already exists
    existing_user = UserService.get_user_by_email(session, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if phone number already exists
    existing_phone = UserService.get_user_by_phone(session, user_data.phone_number)
    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    
    # Create user
    user = UserService.create_user(session, user_data)
    return user


@router.get("/users", response_model=List[UserWithContentsResponse])
def get_all_users(session: Session = Depends(get_session)):
    """
    Get all users with their associated content.
    """
    users = UserService.get_all_users(session)
    return users


@router.get("/users/{user_id}", response_model=UserWithContentsResponse)
def get_user_by_id(user_id: int, session: Session = Depends(get_session)):
    """
    Get a single user by ID with their associated content.
    """
    user = UserService.get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int, 
    user_data: UpdateUserSchema, 
    session: Session = Depends(get_session)
):
    """
    Update user information (name, email, phone_number).
    Only updates fields that are provided in the request.
    """
    try:
        user = UserService.update_user(session, user_id, user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
