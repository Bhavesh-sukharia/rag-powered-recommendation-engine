"""
User data repository.
"""
from typing import Optional, Dict
from bson import ObjectId
import datetime



class UserRepository:
    """Repository for user data operations."""
    
    def __init__(self, db):
        """Initialize user repository."""
        self.db = db
        self.collection = db["users"]
    
    async def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID."""
        try:
            user = await self.collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user["id"] = str(user["_id"])
            return user
        except Exception:
            return None
    
    async def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username."""
        try:
            user = await self.collection.find_one({"username": username})
            if user:
                user["id"] = str(user["_id"])
            return user
        except Exception:
            return None
    
    async def create_user(self, user_data: Dict) -> Dict:
        """Create a new user."""
        # Remove id if it's None
        if "id" in user_data and user_data["id"] is None:
            del user_data["id"]
        
        result = await self.collection.insert_one(user_data)
        # Build a JSON-serializable response (remove ObjectId)
        created = dict(user_data)
        created_id = result.inserted_id
        created["id"] = str(created_id)
        # Remove raw _id if present
        if "_id" in created:
            created.pop("_id")
        return created

    async def get_users(self, skip: int = 0, limit: int = 100) -> list[Dict]:
        """Return a paginated list of users."""
        try:
            users = await self.collection.find().skip(skip).limit(limit).to_list(None)
            for u in users:
                u["id"] = str(u.get("_id"))
                u.pop("_id", None)
            return users
        except Exception:
            return []

    async def count_users(self) -> int:
        """Return total number of users in the collection."""
        try:
            return await self.collection.count_documents({})
        except Exception:
            return 0

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user by id. Returns True if deleted."""
        try:
            result = await self.collection.delete_one({"_id": ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception:
            return False

    async def update_user_preferences(self, user_id: str, preferred_genres: list[str]) -> Optional[Dict]:
        """Update only the user's preferred genres."""
        try:
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(user_id)},
                {"$set": {"preferred_genres": preferred_genres}},
                return_document=True,
            )
            if result:
                result["id"] = str(result["_id"])
            return result
        except Exception:
            return None

    async def update_user_rating(self, user_id: str, item_id: int, rating_number: float) -> Optional[Dict]:
        """Update a movie rating for a user."""
        try:
            user = await self.collection.find_one(
                {"_id": ObjectId(user_id)},
                {"ratings": 1}
            )
            if not user:
                return None

            ratings = user.get("ratings", [])
            updated_ratings = []
            rating_found = False

            for rating in ratings:
                if rating.get("item_id") == item_id:
                    updated_ratings.append({"item_id": item_id, "rating_number": rating_number})
                    rating_found = True
                else:
                    updated_ratings.append(rating)

            if not rating_found:
                updated_ratings.append({"item_id": item_id, "rating_number": rating_number})

            await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"ratings": updated_ratings}},
            )
            return await self.get_user(user_id)
        except Exception:
            return None
    
    async def get_user_preferences(self, user_id: str) -> Optional[Dict]:
        """Get user preferences."""
        try:
            user = await self.collection.find_one(
                {"_id": ObjectId(user_id)},
                {"preferred_genres": 1}
            )
            return user
        except Exception:
            return None
        
    from typing import Optional


    async def get_user_embedding(self, user_id: str) -> Optional[dict]:

        try:
            user = await self.collection.find_one(
                {"id": user_id},
                {
                    "cf_embedding": 1,
                    "cf_weight_sum": 1,
                    "embedding_version": 1
                }
            )

            if user is None:
                return None

            return {
                "embedding": user.get("cf_embedding"),
                "weight_sum": user.get("cf_weight_sum"),
                "embedding_version": user.get(
                    "embedding_version",
                    0
                )
            }

        except Exception as e:
            print(e)
            return None
        
    async def save_user_embedding(self, user_id: str, embedding: list[float], weight_sum: float, embedding_version: int):

        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "cf_embedding": embedding,
                    "cf_weight_sum": weight_sum,
                    "embedding_version": embedding_version,
                    "embedding_updated_at": datetime.datetime.now(datetime.timezone.utc)
                }
            }
        )

    async def get_embedding_version(
        self,
        user_id: str
    ) -> int | None:

        try:

            user = await self.collection.find_one(
                {"id": user_id},
                {
                    "embedding_version": 1
                }
            )

            if user is None:
                return None

            version = user.get("embedding_version", 0)

            try:
                return int(version)

            except (TypeError, ValueError):
                return 0

        except Exception as e:
            print(e)
            return None
