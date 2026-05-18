"""
User routes.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.core.database import db
from app.utils.logger import get_logger

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
)

logger = get_logger(__name__)


class UserRatingRequest(BaseModel):
    item_id: int
    rating_number: float = Field(ge=0)


class UserPreferencesRequest(BaseModel):
    preferred_genres: list[str] = Field(default_factory=list)

@router.post("")
async def create_user(user_data: User):
    """Create a new user."""
    repo = UserRepository(db)
    try:
        # Check if username already exists
        existing = await repo.get_user_by_username(user_data.username)
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")

        await repo.create_user(user_data.dict())
        return {"message": "User created successfully", "username": user_data.username}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create user: {str(e)}")


@router.put("/{user_id}")
async def update_user(user_id: str, user_data: UserPreferencesRequest):
    """Update only the user's genre preferences."""
    repo = UserRepository(db)
    updated_user = await repo.update_user_preferences(user_id, user_data.preferred_genres)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.post("/{user_id}/ratings")
async def rate_movie(user_id: str, rating_data: UserRatingRequest):
    """Create or update a rating for a movie on a user profile."""
    repo = UserRepository(db)
    user = await repo.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = await repo.update_user_rating(
        user_id,
        rating_data.item_id,
        rating_data.rating_number,
    )
    if not updated_user:
        raise HTTPException(status_code=400, detail="Failed to save rating")

    logger.info(
        "Saved rating for user_id=%s item_id=%s rating_number=%s",
        user_id,
        rating_data.item_id,
        rating_data.rating_number,
    )
    return {
        "message": "Rating saved successfully",
        "user_id": updated_user["id"],
        "item_id": rating_data.item_id,
        "rating_number": rating_data.rating_number,
        "ratings": updated_user.get("ratings", []),
    }


@router.get("")
async def list_users(skip: int = 0, limit: int = 100):
    """List users with pagination."""
    repo = UserRepository(db)
    users = await repo.get_users(skip=skip, limit=limit)
    total = await repo.count_users()
    return {"count": total, "users": users}


@router.delete("/{user_id}")
async def delete_user(user_id: str):
    """Delete a user by id."""
    repo = UserRepository(db)
    if user_id == '1':
        # Protect built-in admin/user 1 from deletion
        raise HTTPException(status_code=400, detail="Cannot delete protected user")

    success = await repo.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found or delete failed")
    return {"message": "User deleted"}
