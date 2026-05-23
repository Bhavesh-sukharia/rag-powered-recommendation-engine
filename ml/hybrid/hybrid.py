import numpy as np
import pickle
import torch
import sys
from ml.collaborative_filtering.model import CF_RecommenderSystem
import time


class HybridRecommenderSystem:

    def __init__(
        self,
        model_path,
        item_to_index_path,
        index_to_item_path,
        embedding_dim=32
    ):

        # ====================================
        # Load Artifacts
        # ====================================

        with open(item_to_index_path, "rb") as f:
            self.item_to_index = pickle.load(f)

        with open(index_to_item_path, "rb") as f:
            self.index_to_item = pickle.load(f)

        self.num_items = len(self.item_to_index) + 1

        # ====================================
        # Initialize CF Recommender
        # ====================================

        self.cf_recommender = CF_RecommenderSystem(

            model_path=model_path,

            num_items=self.num_items,

            item_to_index=self.item_to_index,

            index_to_item=self.index_to_item,

            embedding_dim=embedding_dim
        )

    # ========================================
    # Candidate Generation
    # ========================================

    def get_candidate_movie_indices(self, rating_history: dict):
        watched_indices = set(self.item_to_index[x["item_id"]] for x in rating_history)

        candidate_indices = [idx for idx in range(1, self.num_items) if idx not in watched_indices]

        print(f"len of candidate indices: {len(candidate_indices)}")
        print(f"watched movies are {watched_indices} and the length is {len(watched_indices)}")

        return candidate_indices

    # ========================================
    # Collaborative Filtering Score
    # ========================================

    def get_cf_score(self, user_embedding, candidate_indices):
        # Normalize to 0 → 1
        return (self.cf_recommender.predict_at_once(user_embedding, candidate_indices) / 5.0)

    # ========================================
    # Content-Based Score
    # ========================================

    def get_cb_score(self, user_id, candidate_indices):
        return torch.rand(len(candidate_indices), device=self.cf_recommender.device)  
    


    def recommend(self, user_id, user_embedding, rating_history, alpha=0.5, top_k=20):
        # ====================================
        # Candidate Movies
        # ====================================

        t1 = time.time()

        candidate_indices = (self.get_candidate_movie_indices(rating_history))

        t2 = time.time()

        print(f"Time taken to calculate candidate movies: {t2 - t1} sec")

        # ====================================
        # Predict Scores
        # ====================================

        t1 = time.time()

        cf_scores = self.get_cf_score(user_embedding, candidate_indices)

        cb_scores = self.get_cb_score(user_id, candidate_indices)

        hybrid_scores = alpha * cf_scores + (1 - alpha) * cb_scores

        t2 = time.time()

        print(f"Time taken to calculate all scores: {t2 - t1} sec")

        # ====================================
        # TOP-K ONLY
        # ====================================

        t1 = time.time()

        top_scores, top_indices = torch.topk(hybrid_scores, k=top_k)

        t2 = time.time()

        print(f"Time taken for topk: {t2 - t1} sec")

        # ====================================
        # Final Results
        # ====================================

        t1 = time.time()

        final_results = []

        for rank_idx in range(top_k):

            movie_tensor_idx = (top_indices[rank_idx].item())

            candidate_movie_idx = candidate_indices[movie_tensor_idx]

            movie_id = self.index_to_item[candidate_movie_idx]
            
            final_results.append(
                {
                    "movie_id": int(movie_id),

                    "hybrid_score": float(hybrid_scores[movie_tensor_idx]),

                    "cf_score": float(cf_scores[movie_tensor_idx]),

                    "cb_score": float(cb_scores[movie_tensor_idx])
                }
            )

        t2 = time.time()

        print(f"Time taken to make final result: {t2 - t1} sec")

        return final_results

if __name__ == "__main__":

    recommender = HybridRecommenderSystem(

        model_path="ml/models/best_dynamic_ncf_online_debug.pth",

        item_to_index_path=(
            "ml/artifacts/item_to_index.pkl"
        ),

        index_to_item_path=(
            "ml/artifacts/index_to_item.pkl"
        ),

        embedding_dim=32
    )

    user_id = int(sys.argv[1])
    user_embedding = None
    rating_history = None
    # alpha = float(sys.argv[1])

    recommendations = recommender.recommend(
        user_id=user_id,
        user_embedding=user_embedding,
        rating_history=None,
        alpha=0.5,
        top_k=10
    )

    print(recommendations)