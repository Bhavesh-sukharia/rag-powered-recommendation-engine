"""
Recommendation repository to encapsulate weighted recommendation logic.
"""
from typing import Dict, List

from app.repositories.user_repository import UserRepository
from app.repositories.movie_repository import MovieRepository
from app.services.cb_service import CBService
from app.services.cf_service import CFService
from app.services.sentiment_service import SentimentService
from app.core.database import db


class RecommendationRepository:
    """Repository for assembling weighted recommendations."""

    def __init__(self, db_conn=None):
        self.db = db_conn or db
        self.user_repo = UserRepository(self.db)
        self.movie_repo = MovieRepository(self.db)
        self.cb = CBService()
        self.cf = CFService()
        self.sentiment = SentimentService()

    async def get_weighted_recommendations(
        self,
        username: str,
        cb_weight: float,
        cf_weight: float,
        sentiment_weight: float,
        count: int = 10,
    ) -> Dict:
        """Return weighted recommendations for a username.

        This mirrors the previous route logic but is placed in the
        repository layer to keep code organization consistent.
        """
        user = await self.user_repo.get_user_by_username(username)
        if not user:
            return {"error": "user_not_found"}

        # user_id is not used by the placeholder services; pass a simple numeric id
        user_numeric_id = 1

        # request more candidates than needed so merging has overlap
        candidate_count = count * 2

        cb_items, cb_scores = self.cb.get_recommendations(user_numeric_id, candidate_count)
        cf_items, cf_scores = self.cf.get_recommendations(user_numeric_id, candidate_count)
        sentiment_items, sentiment_scores = self.sentiment.get_recommendations(user_numeric_id, candidate_count)

        combined_scores: dict = {}

        def _ensure(item_id: int):
            if item_id not in combined_scores:
                combined_scores[item_id] = {"cb_score": 0.0, "cf_score": 0.0, "sentiment_score": 0.0}

        for item_id, score in zip(cb_items, cb_scores):
            _ensure(item_id)
            combined_scores[item_id]["cb_score"] = score

        for item_id, score in zip(cf_items, cf_scores):
            _ensure(item_id)
            combined_scores[item_id]["cf_score"] = score

        for item_id, score in zip(sentiment_items, sentiment_scores):
            _ensure(item_id)
            combined_scores[item_id]["sentiment_score"] = score

        for item_id, scores in combined_scores.items():
            cb = scores.get("cb_score", 0.0)
            cf = scores.get("cf_score", 0.0)
            sentiment = scores.get("sentiment_score", 0.0)
            combined = cb * cb_weight + cf * cf_weight + sentiment * sentiment_weight
            scores["combined_score"] = combined

        sorted_items = sorted(combined_scores.items(), key=lambda x: x[1]["combined_score"], reverse=True)[:count]
        movie_item_ids = [int(item_id) for item_id, _ in sorted_items]

        movies = await self.movie_repo.get_movies(movie_item_ids)
        movies_by_item = {m["item_id"]: m for m in movies}

        recommendations = []
        for item_id, scores in sorted_items:
            m = movies_by_item.get(int(item_id))
            if not m:
                continue
            # normalize mongo id
            m["id"] = str(m.get("_id", m.get("id", "")))
            m.pop("_id", None)

            recommendations.append({
                "movie": m,
                "combined_score": scores["combined_score"],
                "cb_score": scores.get("cb_score", 0.0),
                "cf_score": scores.get("cf_score", 0.0),
                "sentiment_score": scores.get("sentiment_score", 0.0),
            })

        return {"username": username, "recommendations": recommendations}
