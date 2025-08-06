"""
Users API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database.session import get_db

router = APIRouter(prefix="/users", tags=["Users"])


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    full_name: str
    role: str
    status: str
    is_active: bool
    is_verified: bool


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all users"""
    # For now, return mock data
    # TODO: Implement actual user listing
    return [
        {
            "id": 1,
            "email": "admin@docugenie.com",
            "username": "admin",
            "first_name": "Admin",
            "last_name": "User",
            "full_name": "Admin User",
            "role": "admin",
            "status": "active",
            "is_active": True,
            "is_verified": True
        }
    ]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific user"""
    # For now, return mock data
    # TODO: Implement actual user retrieval
    return {
        "id": user_id,
        "email": f"user{user_id}@docugenie.com",
        "username": f"user{user_id}",
        "first_name": "User",
        "last_name": f"{user_id}",
        "full_name": f"User {user_id}",
        "role": "viewer",
        "status": "active",
        "is_active": True,
        "is_verified": False
    }


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Update a user"""
    # For now, return a mock response
    # TODO: Implement actual user update
    return {
        "message": f"User {user_id} update endpoint created"
    }


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Delete a user"""
    # For now, return a mock response
    # TODO: Implement actual user deletion
    return {
        "message": f"User {user_id} deletion endpoint created"
    }
