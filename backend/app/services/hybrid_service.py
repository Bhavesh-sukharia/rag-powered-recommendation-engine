import sys
import os

# =========================================
# Add Project Root To Python Path
# =========================================

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../../.."
        )
    )
)

from ml.hybrid.hybrid import HybridRecommenderSystem
# =========================================
# Project Root
# =========================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../../.."
    )
)

# =========================================
# Paths
# =========================================

MODEL_PATH = os.path.join(
    PROJECT_ROOT,
    "ml",
    "models",
    "best_dynamic_ncf_online_debug.pth"
)

ITEM_TO_INDEX_PATH = os.path.join(
    PROJECT_ROOT,
    "ml",
    "artifacts",
    "item_to_index.pkl"
)

INDEX_TO_ITEM_PATH = os.path.join(
    PROJECT_ROOT,
    "ml",
    "artifacts",
    "index_to_item.pkl"
)


class HybridService:

    def __init__(self):

        self.recommender = HybridRecommenderSystem(
                                model_path=MODEL_PATH,

                                item_to_index_path=ITEM_TO_INDEX_PATH,

                                index_to_item_path=INDEX_TO_ITEM_PATH,

                                embedding_dim=32
                            )

    # =====================================
    # Get Recommendations
    # =====================================

    def get_recommendations(self, user_id, user_embedding, rating_history, alpha=0.5, count=20):

        recommendations = (
            self.recommender.recommend(
                user_id=user_id,
                user_embedding=user_embedding,
                rating_history=rating_history,
                alpha=alpha,
                top_k=count
            )
        )

        formatted_results = []

        for recommendation in recommendations:

            formatted_results.append({

                "item_id": recommendation[
                    "movie_id"
                ],

                "hybrid_score": recommendation[
                    "hybrid_score"
                ],

                "cf_score": recommendation[
                    "cf_score"
                ],

                "cb_score": recommendation[
                    "cb_score"
                ]
            })

        return formatted_results