from datetime import datetime

from pydantic import BaseModel, Field


class Movie(BaseModel):
	id: str | None = None
	item_id: int
	title: str
	genres: list[str]
	overview: str | None = None
	avg_rating: float | None = 0.0
	rating_number: int | None = 0
	created_at: datetime = Field(default_factory=datetime.utcnow)
