# app/services/user_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from typing import Optional, List

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.auth import get_password_hash, verify_password
from app.utils.helpers import paginate, get_object_or_404

def create_user(db: Session, user_data: UserCreate) -> User:
    """
    Create a new user with hashed password.
    
    Args:
        db: Database session
        user_data: User data from request
        
    Returns:
        Created user object
        
    Raises:
        HTTPException if user with same email or username already exists
    """
    # Check if user with same email exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if user with same username exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user with hashed password
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        is_active=user_data.is_active,
        is_admin=user_data.is_admin
    )
    
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create user due to constraint violation"
        )
    
    return user

def get_user_by_id(db: Session, user_id: int) -> User:
    """Get a user by ID."""
    return get_object_or_404(db, User, user_id)

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email."""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get a user by username."""
    return db.query(User).filter(User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get all users with pagination."""
    return db.query(User).offset(skip).limit(limit).all()

def get_users_paginated(db: Session, page: int = 1, page_size: int = None):
    """Get paginated users."""
    query = db.query(User)
    return paginate(query, page, page_size)

def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
    """Update a user."""
    user = get_object_or_404(db, User, user_id)
    
    update_data = user_data.dict(exclude_unset=True)
    
    # If updating email, check if new email already exists
    if user_data.email and user_data.email != user.email:
        if db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # If updating username, check if new username already exists
    if user_data.username and user_data.username != user.username:
        if db.query(User).filter(User.username == user_data.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Hash password if provided
    if user_data.password:
        update_data["hashed_password"] = get_password_hash(user_data.password)
        # Remove the original password key
        update_data.pop("password", None)
    
    # Update user attributes
    for key, value in update_data.items():
        setattr(user, key, value)
    
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update user due to constraint violation"
        )
    
    return user

def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user."""
    user = get_object_or_404(db, User, user_id)
    
    db.delete(user)
    db.commit()
    
    return True

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password."""
    user = get_user_by_email(db, email)
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user