"""
Movie data repository.
"""
from typing import List, Optional, Dict
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
                movie["id"] = str(movie["_id"])
            return movie
        except Exception:
            return None
    
    async def get_movie_by_title(self, title: str) -> Optional[Dict]:
        """Get movie by title."""
        try:
            movie = await self.collection.find_one({"title": title})
            if movie:
                movie["id"] = str(movie["_id"])
            return movie
        except Exception:
            return None
    
    async def get_movie(self, movie_id: str) -> Optional[Dict]:
        """Get movie by ID."""
        try:
            movie = await self.collection.find_one({"_id": ObjectId(movie_id)})
            if movie:
                movie["id"] = str(movie["_id"])
            return movie
        except Exception:
            return None
    
    async def get_movies(self, movie_ids: List[int]) -> List[Dict]:
        """Get multiple movies by IDs."""
        try:
            movies = await self.collection.find({"item_id": {"$in": movie_ids}}).to_list(None)
            for movie in movies:
                movie["id"] = str(movie["_id"])
            return movies
        except Exception:
            return []
    
    async def search_movies(self, query: str) -> List[Dict]:
        """Search movies by title or description."""
        try:
            movies = await self.collection.find({
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"overview": {"$regex": query, "$options": "i"}}
                ]
            }).to_list(None)
            for movie in movies:
                movie["id"] = str(movie["_id"])
            return movies
        except Exception:
            return []
    
    async def get_movie_metadata(self, movie_id: int) -> Optional[Dict]:
        """Get movie metadata (year, categories, etc)."""
        try:
            movie = await self.collection.find_one(
                {"item_id": movie_id},
                {"genres": 1, "avg_rating": 1, "created_at": 1}
            )
            if movie:
                movie["id"] = str(movie["_id"])
            return movie
        except Exception:
            return None
