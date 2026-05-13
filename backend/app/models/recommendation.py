from pydantic import BaseModel, Field
from app.models.movie import Movie


class MovieRecommendation(BaseModel):
    """Movie recommendation with score details."""
    movie: Movie
    combined_score: float
    cb_score: float = 0.0
    cf_score: float = 0.0
    sentiment_score: float = 0.0


class RecommendationRequest(BaseModel):
    """Request for weighted recommendations from frontend."""
    username: str
    cb_weight: float = Field(default=0.33, ge=0.0, le=1.0)
    cf_weight: float = Field(default=0.33, ge=0.0, le=1.0)
    sentiment_weight: float = Field(default=0.34, ge=0.0, le=1.0)
    count: int = Field(default=10, ge=1, le=100)
