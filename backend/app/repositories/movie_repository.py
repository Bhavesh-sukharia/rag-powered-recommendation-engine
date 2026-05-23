"""
Movie data repository.
"""
import re
from typing import Any, Dict, List, Optional
from bson import ObjectId


class MovieRepository:
    """Repository for movie data operations."""
    
    def __init__(self, db):
        """Initialize movie repository."""
        self.db = db
        self.collection = db["movies"]
    
    async def create_movie(self, movie_data: Dict) -> Dict:
        """Create a new movie."""
        # Remove id if it's None
        if "id" in movie_data and movie_data["id"] is None:
            del movie_data["id"]
        
        result = await self.collection.insert_one(movie_data)
        # Build a JSON-serializable response
        created = dict(movie_data)
        created["id"] = str(result.inserted_id)
        if "_id" in created:
            created.pop("_id")
        return created

    async def bulk_create_movies(self, movie_data_list: List[Dict]) -> int:
        """Create many movies while skipping existing item_ids."""
        if not movie_data_list:
            return 0

        item_ids = [movie["item_id"] for movie in movie_data_list if movie.get("item_id") is not None]
        existing_item_ids = set()

        if item_ids:
            existing_movies = await self.collection.find(
                {"item_id": {"$in": item_ids}},
                {"item_id": 1}
            ).to_list(None)
            existing_item_ids = {movie["item_id"] for movie in existing_movies}

        docs_to_insert = []
        seen_item_ids = set(existing_item_ids)

        for movie in movie_data_list:
            item_id = movie.get("item_id")
            if item_id is None or item_id in seen_item_ids:
                continue
            seen_item_ids.add(item_id)
            docs_to_insert.append(movie)

        if not docs_to_insert:
            return 0

        result = await self.collection.insert_many(docs_to_insert)
        return len(result.inserted_ids)
    
    async def get_movie_by_item_id(self, item_id: int) -> Optional[Dict]:
        """Get movie by item_id."""
        try:
            movie = await self.collection.find_one({"item_id": item_id})
            if movie:
                movie_dict = dict(movie)
                if "_id" in movie_dict:
                    movie_dict["id"] = str(movie_dict.pop("_id"))
                return movie_dict
            return None
        except Exception:
            return None
    
    async def get_movie_by_title(self, title: str) -> Optional[Dict]:
        """Get movie by title."""
        try:
            movie = await self.collection.find_one({"title": title})
            if movie:
                movie_dict = dict(movie)
                if "_id" in movie_dict:
                    movie_dict["id"] = str(movie_dict.pop("_id"))
                return movie_dict
            return None
        except Exception:
            return None
    
    async def get_movie(self, movie_id: str) -> Optional[Dict]:
        """Get movie by ID."""
        try:
            movie = await self.collection.find_one({"_id": ObjectId(movie_id)})
            if movie:
                movie_dict = dict(movie)
                if "_id" in movie_dict:
                    movie_dict["id"] = str(movie_dict.pop("_id"))
                return movie_dict
            return None
        except Exception:
            return None
    
    async def get_movies(self, movie_ids: List[int]) -> List[Dict]:
        """Get multiple movies by IDs."""
        try:
            movies = await self.collection.find({"item_id": {"$in": movie_ids}}).to_list(None)
            result = []
            for movie in movies:
                movie_dict = dict(movie)
                if "_id" in movie_dict:
                    movie_dict["id"] = str(movie_dict.pop("_id"))
                result.append(movie_dict)
            return result
        except Exception:
            return []
    
    async def search_movies(
        self,
        query: str,
        page: int = 1,
        limit: int = 20,
        genre: Optional[str] = None,
        sort: str = "rating",
    ) -> Dict[str, Any]:
        """Search movies by title, overview, and optional genre with pagination."""
        try:
            page = max(page, 1)
            limit = max(limit, 1)
            skip = (page - 1) * limit

            criteria: Dict[str, Any] = {}
            if query.strip():
                escaped_query = re.escape(query.strip())
                criteria["$or"] = [
                    {"title": {"$regex": escaped_query, "$options": "i"}},
                    {"genres": {"$regex": escaped_query, "$options": "i"}},
                ]

            if genre and genre.strip():
                criteria["genres"] = {"$regex": re.escape(genre.strip()), "$options": "i"}

            if sort == "popularity":
                sort_fields = [("rating_number", -1), ("avg_rating", -1), ("title", 1)]
            elif sort == "rating":
                sort_fields = [("avg_rating", -1), ("rating_number", -1), ("title", 1)]
            else:
                sort_fields = [("title", 1)]

            total = await self.collection.count_documents(criteria)
            cursor = self.collection.find(criteria).sort(sort_fields).skip(skip).limit(limit)
            movies = await cursor.to_list(None)

            result = []
            for movie in movies:
                movie_dict = dict(movie)
                if "_id" in movie_dict:
                    movie_dict["id"] = str(movie_dict.pop("_id"))
                result.append(movie_dict)

            return {
                "movies": result,
                "page": page,
                "limit": limit,
                "total": int(total),
                "has_more": skip + len(result) < int(total),
            }
        except Exception:
            return {
                "movies": [],
                "page": page,
                "limit": limit,
                "total": 0,
                "has_more": False,
            }
    
    async def get_movie_metadata(self, movie_id: int) -> Optional[Dict]:
        """Get movie metadata (year, categories, etc)."""
        try:
            movie = await self.collection.find_one(
                {"item_id": movie_id},
                {"genres": 1, "avg_rating": 1, "created_at": 1}
            )
            if movie:
                movie_dict = dict(movie)
                if "_id" in movie_dict:
                    movie_dict["id"] = str(movie_dict.pop("_id"))
                return movie_dict
            return None
        except Exception:
            return None

    async def list_movies(self, skip: int = 0, limit: int = 10) -> List[Dict]:
        """List movies with pagination."""
        try:
            movies = await self.collection.find().skip(skip).limit(limit).to_list(None)
            result = []
            for movie in movies:
                # Convert ObjectId to string for JSON serialization
                movie_dict = dict(movie)
                if "_id" in movie_dict:
                    movie_dict["id"] = str(movie_dict.pop("_id"))
                result.append(movie_dict)
            return result
        except Exception:
            return []

    async def count_movies(self) -> int:
        """Return the total number of movies in the collection."""
        try:
            # Use count_documents for an accurate count
            count = await self.collection.count_documents({})
            return int(count)
        except Exception:
            return 0

    async def get_top_rated_movies(self, limit=20):
        cursor = (
            self.collection
            .find({})
            .sort("vote_average", -1)
            .limit(limit)
        )

        return await cursor.to_list(length=limit)