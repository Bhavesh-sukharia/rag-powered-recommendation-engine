from datetime import datetime

from pydantic import BaseModel, Field


class User(BaseModel):
	id: str | None = None
	username: str
	preferred_genres: list[str] = Field(default_factory=list)
	ratings: list[dict] = Field(default_factory=list)  # List of dicts with movie_id and rating
	created_at: datetime = Field(default_factory=datetime.utcnow)
