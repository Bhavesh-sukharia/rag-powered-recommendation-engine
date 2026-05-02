from fastapi import APIRouter
from pydantic import BaseModel, Field

from services.rag import build_explanation
from services.recommender import rank_items


router = APIRouter(tags=["recommendations"])


class RecommendationRequest(BaseModel):
    user_id: str = Field(..., examples=["user-123"])
    query: str = Field(default="")
    limit: int = 10


@router.post("/recommend")
def recommend(payload: RecommendationRequest) -> dict:
    ranked_items = rank_items(payload.user_id, payload.query, payload.limit)
    return {"user_id": payload.user_id, "items": ranked_items}


@router.get("/explanations/{item_id}")
def explanation(item_id: str) -> dict:
    explanation_text = build_explanation(item_id, ["collaborative signals", "content similarity"])
    return {"item_id": item_id, "explanation": explanation_text}