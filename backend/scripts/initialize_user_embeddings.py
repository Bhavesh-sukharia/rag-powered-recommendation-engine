import asyncio
import sys
from pathlib import Path
import pickle

# Add backend root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "backend"))

from app.core.database import db
from app.repositories.user_repository import UserRepository

from ml.collaborative_filtering.model import CF_RecommenderSystem

from app.core.config import get_settings

settings = get_settings()


CURRENT_EMBEDDING_VERSION = 1

with open(settings.ITEM_TO_INDEX_PATH, "rb") as f:
    ITEM_TO_INDEX = pickle.load(f)

with open(settings.INDEX_TO_ITEM_PATH, "rb") as f:
    INDEX_TO_ITEM = pickle.load(f)



async def initialize_user_embeddings():

    user_repo = UserRepository(db)

    print("db name: ", db.name)

    print("Mongo URL:", settings.MONGODB_URL)
    print("Database:", settings.DATABASE_NAME)
    print("Collection:", user_repo.collection.name)

    count = await user_repo.collection.count_documents({})
    print("User count:", count)

    client = db.client

    dbs = await client.list_database_names()

    print("DATABASES:")
    for database in dbs:
        print("-", database)

    collections = await db.list_collection_names()

    print("COLLECTIONS:")
    for c in collections:
        print("-", c)

    count = await db["users"].count_documents({})
    print("Users:", count)

    # recommender = CF_RecommenderSystem(
    #     model_path="ml/models/best_dynamic_ncf_online_debug.pth",
    #     num_items=99224,
    #     item_to_index=ITEM_TO_INDEX,
    #     index_to_item=INDEX_TO_ITEM,
    #     user_histories=None
    # )

    recommender = CF_RecommenderSystem(
        model_path=str(
            PROJECT_ROOT
            / "ml"
            / "models"
            / "best_dynamic_ncf_online_debug.pth"
        ),
        num_items=99224,
        item_to_index=ITEM_TO_INDEX,
        index_to_item=INDEX_TO_ITEM,
        user_histories=None
    )

    users = await user_repo.collection.find({}).to_list(None)

    initialized_count = 0
    skipped_count = 0
    failed_count = 0

    for user in users:

        try:

            user_id = str(user["_id"])

            # Skip if embedding already exists
            if (user.get("cf_embedding") is not None
                and
                user.get("embedding_version") == CURRENT_EMBEDDING_VERSION
            ):

                skipped_count += 1
                print(f"[SKIPPED] {user['username']}")
                continue

            rating_history = user.get("ratings", [])

            if len(rating_history) == 0:

                failed_count += 1

                print(f"[FAILED] {user['username']} -> no ratings")
                continue

            user_embedding, weight_sum = (recommender.build_user_embedding_from_history(user_id, rating_history))

            payload = (recommender.tensor_to_embedding_payload(user_embedding,weight_sum))

            await user_repo.save_user_embedding(
                user_id=user_id,
                embedding=payload["embedding"],
                weight_sum=payload["weight_sum"],
                embedding_version=CURRENT_EMBEDDING_VERSION
            )

            initialized_count += 1

            print(f"[SUCCESS] {user['username']}")

        except Exception as e:

            failed_count += 1

            print(
                f"[ERROR] {user.get('username')} -> {e}"
            )

    print("\n========== SUMMARY ==========")

    print(
        f"Initialized : {initialized_count}"
    )

    print(
        f"Skipped     : {skipped_count}"
    )

    print(
        f"Failed      : {failed_count}"
    )


if __name__ == "__main__":
    asyncio.run(
        initialize_user_embeddings()
    )