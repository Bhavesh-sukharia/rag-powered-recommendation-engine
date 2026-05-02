from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(prefix="/users", tags=["users"])


class PreferenceUpdate(BaseModel):
    user_id: str
    preferences: dict[str, str] = {}


@router.get("/{user_id}/preferences")
def get_preferences(user_id: str) -> dict:
    return {"user_id": user_id, "preferences": {}}


@router.post("/{user_id}/preferences")
def update_preferences(user_id: str, payload: PreferenceUpdate) -> dict:
    return {"user_id": user_id, "saved": True, "preferences": payload.preferences}