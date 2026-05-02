from sqlalchemy import JSON, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(128), nullable=False, index=True)
    preferences = Column(JSON, nullable=False, default=dict)


class RecommendationEvent(Base):
    __tablename__ = "recommendation_events"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(128), nullable=False, index=True)
    item_id = Column(String(128), nullable=False)
    context = Column(Text, nullable=True)