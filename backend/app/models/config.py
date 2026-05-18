from datetime import datetime

from pydantic import BaseModel, Field


class Config(BaseModel):
    cf_weight: int = Field(default=50, ge=0, le=100)
    cb_weight: int = Field(default=50, ge=0, le=100)
    sentiment_reranking: bool = Field(default=True)
    rag_enabled: bool = Field(default=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
