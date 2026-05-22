# import random
# import pickle
# from ml.collaborative_filtering.model import CF_RecommenderSystem

# with open("ml/artifacts/item_to_index.pkl", "rb") as f:
#     item_to_index = pickle.load(f)

# with open("ml/artifacts/index_to_item.pkl", "rb") as f:
#     index_to_item = pickle.load(f)

# with open("ml/artifacts/user_histories.pkl", "rb") as f:
#     user_histories  = pickle.load(f)


# num_items = len(item_to_index) + 1

# def get_candidate_movie_indices(user_id, user_histories):
#     watched_movies = set([x[0] for x in user_histories[user_id]])
#     candidate_indices = [idx for idx in range(1, num_items) if idx not in watched_movies]
#     return candidate_indices

# def get_cf_score(user_id, movie_id, cf_recommender):
#     cf_score = cf_recommender.predict_rating(user_id, movie_id)
#     return cf_score / 5.0

# def get_cb_score(user_id, movie_id):
#     return random.random()
    

# def generate_scores(
#     user_id,
#     candidate_movies,
#     cf_recommender,
#     index_to_item
# ):

#     predicted_scores = {}

#     for idx in candidate_movies:
#         movie_id = index_to_item[idx]
#         cf_score = get_cf_score(
#             user_id=user_id,
#             movie_id=movie_id,
#             cf_recommender=cf_recommender
#         )

#         cb_score = get_cb_score(
#             user_id=user_id,
#             movie_id=movie_id,
#         )

#         predicted_scores[movie_id] = {
#             "cf_score": cf_score,
#             "cb_score": cb_score,
#             "hybrid_score": None
#         }

#     return predicted_scores

# def hybrid_recommedation(user_id, user_histories, alpha, top_k):
#     cf_recommender = CF_RecommenderSystem(

#     model_path="ml/models/best_dynamic_ncf_online_debug.pth",

#     num_items=num_items,

#     item_to_index=item_to_index,

#     index_to_item=index_to_item,

#     user_histories=user_histories,

#     user_embeddings={},

#     embedding_dim=32

# )
#     # cb_recommender = CB_Recommendation()

#     candidate_movies = get_candidate_movie_indices(user_id, user_histories)

#     predicted_scores = generate_scores(user_id, candidate_movies, cf_recommender, index_to_item)

#     for movie_id in predicted_scores:
#         print(movie_id)
#         cf_score = predicted_scores[movie_id]["cf_score"]
#         cb_score = predicted_scores[movie_id]["cb_score"]
#         hybrid_score = alpha * cf_score + (1 - alpha) * cb_score
#         predicted_scores[movie_id]["hybrid_score"] = hybrid_score

#     ranked_movies = sorted(
#         predicted_scores.items(),
#         key=lambda x: x[1]["hybrid_score"],
#         reverse=True
#     )

#     return ranked_movies[:top_k]

# if __name__ == "__main__":
#     print(hybrid_recommedation(10, user_histories, 0.5, 5))

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
        user_histories_path,
        embedding_dim=32
    ):

        # ====================================
        # Load Artifacts
        # ====================================

        with open(item_to_index_path, "rb") as f:
            self.item_to_index = pickle.load(f)

        with open(index_to_item_path, "rb") as f:
            self.index_to_item = pickle.load(f)

        with open(user_histories_path, "rb") as f:
            self.user_histories = pickle.load(f)

        self.num_items = len(self.item_to_index) + 1

        # ====================================
        # Initialize CF Recommender
        # ====================================

        self.cf_recommender = CF_RecommenderSystem(

            model_path=model_path,

            num_items=self.num_items,

            item_to_index=self.item_to_index,

            index_to_item=self.index_to_item,

            user_histories=self.user_histories,

            user_embeddings={},

            embedding_dim=embedding_dim
        )

    # ========================================
    # Candidate Generation
    # ========================================

    def get_candidate_movie_indices(
        self,
        user_id
    ):

        watched_indices = set(
            [
                x[0]
                for x in self.user_histories[user_id]
            ]
        )

        candidate_indices = [

            idx

            for idx in range(1, self.num_items)

            if idx not in watched_indices
        ]

        print(
            f"len of candidate indices: "
            f"{len(candidate_indices)}"
        )

        return candidate_indices

    # ========================================
    # Collaborative Filtering Score
    # ========================================

    def get_cf_score(
        self,
        user_id,
        rating_history,
        candidate_indices,
    ):
        # Normalize to 0 → 1
        return (self.cf_recommender.predict_at_once(user_id, rating_history, candidate_indices) / 5.0)

    # ========================================
    # Content-Based Score
    # ========================================

    def get_cb_score(
        self,
        user_id,
        candidate_indices
    ):

        return torch.rand(
            len(candidate_indices),
            device="cuda"
        )  
    # ========================================
    # Generate Scores
    # ========================================

    def generate_scores(
        self,
        user_id,
        candidate_movies,
        alpha = 0.5 
    ):

        predicted_scores = {}
        cf_scores = self.get_cf_score(user_id, candidate_movies)
        cb_scores = self.get_cb_score(user_id, candidate_movies)
        print(candidate_movies[0])
        print(candidate_movies[-1])

        for i, idx in enumerate(candidate_movies):
            movie_id = self.index_to_item[idx]
            cf_score = cf_scores[i]
            cb_score = cb_scores[i]
            hybrid_score = alpha * cf_score + (1 - alpha) * cb_score

            predicted_scores[movie_id] = {
                "cf_score": cf_score,
                "cb_score": cb_score,
                "hybrid_score": hybrid_score
            }

        return predicted_scores

    # ========================================
    # Hybrid Recommendation
    # ========================================

    # def recommend(
    #     self,
    #     user_id,
    #     alpha=0.5,
    #     top_k=10
    # ):
    #     t1 = time.time()
    #     candidate_movies = (
    #         self.get_candidate_movie_indices(
    #             user_id
    #         )
    #     )
    #     t2 = time.time()

    #     print(f"Time taken to calculate candidate movies: {t2 - t1}")

    #     t1 = time.time()

    #     predicted_scores = self.generate_scores(
    #         user_id=user_id,
    #         candidate_movies=candidate_movies,
    #     )

    #     t2 = time.time()

    #     print(f"Time taken to calculate all the predicted scores: {t2 - t1}")


    #     # ====================================
    #     # Ranking
    #     # ====================================
    #     t1 = time.time()
    #     ranked_movies = sorted(
    #         predicted_scores.items(),
    #         key=lambda x: x[1]["hybrid_score"],
    #         reverse=True
    #     )
    #     t2 = time.time()

    #     print(f"Time taken to sort the movies: {t2 - t1}")

    #     # ====================================
    #     # Final Results
    #     # ====================================
    #     t1 = time.time()
    #     final_results = []

    #     for movie_id, scores in ranked_movies[:top_k]:

    #         final_results.append(
    #             {
    #                 "movie_id": int(movie_id),

    #                 "hybrid_score": float(
    #                     scores["hybrid_score"]
    #                 ),

    #                 "cf_score": float(
    #                     scores["cf_score"]
    #                 ),

    #                 "cb_score": float(
    #                     scores["cb_score"]
    #                 )
    #             }
    #         )

    #     t2 = time.time()

    #     print(f"Time taken to make final result: {t2 - t1}")
    #     return final_results

    def recommend(
        self,
        user_id,
        rating_history,
        alpha=0.5,
        top_k=20
    ):

        # ====================================
        # Candidate Movies
        # ====================================

        t1 = time.time()

        candidate_movies = (
            self.get_candidate_movie_indices(user_id)
        )

        t2 = time.time()

        print(
            f"Time taken to calculate candidate movies: {t2 - t1}"
        )

        # ====================================
        # Predict Scores
        # ====================================

        t1 = time.time()

        cf_scores = self.get_cf_score(
            user_id,
            rating_history,
            candidate_movies
        )

        cb_scores = self.get_cb_score(
            user_id,
            candidate_movies
        )

        hybrid_scores = (
            alpha * cf_scores
            + (1 - alpha) * cb_scores
        )

        t2 = time.time()

        print(
            f"Time taken to calculate all scores: {t2 - t1}"
        )

        # ====================================
        # TOP-K ONLY
        # ====================================

        t1 = time.time()

        top_scores, top_indices = torch.topk(
            hybrid_scores,
            k=top_k
        )

        t2 = time.time()

        print(
            f"Time taken for topk: {t2 - t1}"
        )

        # ====================================
        # Final Results
        # ====================================

        t1 = time.time()

        final_results = []

        for rank_idx in range(top_k):

            movie_tensor_idx = (
                top_indices[rank_idx].item()
            )

            candidate_movie_idx = (
                candidate_movies[movie_tensor_idx]
            )

            movie_id = (
                self.index_to_item[candidate_movie_idx]
            )

            final_results.append(
                {
                    "movie_id": int(movie_id),

                    "hybrid_score": float(
                        hybrid_scores[movie_tensor_idx]
                    ),

                    "cf_score": float(
                        cf_scores[movie_tensor_idx]
                    ),

                    "cb_score": float(
                        cb_scores[movie_tensor_idx]
                    )
                }
            )

        t2 = time.time()

        print(
            f"Time taken to make final result: {t2 - t1}"
        )

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

        user_histories_path=(
            "ml/artifacts/user_histories.pkl"
        ),

        embedding_dim=32
    )

    user_id = int(sys.argv[1])
    # alpha = float(sys.argv[1])

    recommendations = recommender.recommend(
        user_id=user_id,
        rating_history=None,
        alpha=0.5,
        top_k=10
    )

    print(recommendations)