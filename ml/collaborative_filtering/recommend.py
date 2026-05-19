import pickle
from model import RecommenderSystem

with open("ml/artifacts/item_to_index.pkl", "rb") as f:
    item_to_index = pickle.load(f)

with open("ml/artifacts/index_to_item.pkl", "rb") as f:
    index_to_item = pickle.load(f)

with open("ml/artifacts/user_histories.pkl", "rb") as f:
    user_histories  = pickle.load(f)

num_items = len(item_to_index) + 1

recommender = RecommenderSystem(

    model_path="ml/models/best_dynamic_ncf_online_debug.pth",

    num_items=num_items,

    item_to_index=item_to_index,

    index_to_item=index_to_item,

    user_histories=user_histories,

    user_embeddings={},

    embedding_dim=32

)

recommendations = recommender.recommend_movies(
    user_id=10,
    top_k=10
)

for recommendation in recommendations:

    print(recommendation)
    

# import pickle
# from pathlib import Path

# import torch


# DEVICE = torch.device(
#     "cuda" if torch.cuda.is_available() else "cpu"
# )


# # =========================================================
# # PATHS
# # =========================================================

# BASE_DIR = Path(__file__).resolve().parent
# ARTIFACTS_DIR = (BASE_DIR / "../artifacts").resolve()
# MODELS_DIR = (BASE_DIR / "../models").resolve()


# # =========================================================
# # LOAD ARTIFACTS
# # =========================================================

# with open(ARTIFACTS_DIR / "item_to_index.pkl", "rb") as f:
#     item_to_index = pickle.load(f)

# with open(ARTIFACTS_DIR / "index_to_item.pkl", "rb") as f:
#     index_to_item = pickle.load(f)

# with open(ARTIFACTS_DIR / "user_histories.pkl", "rb") as f:
#     user_histories = pickle.load(f)


# # =========================================================
# # MODEL
# # =========================================================

# class DynamicNCF(torch.nn.Module):
#     def __init__(self, num_items, embedding_dim=32):
#         super().__init__()

#         self.item_embedding = torch.nn.Embedding(
#             num_items,
#             embedding_dim,
#             padding_idx=0
#         )

#         self.mlp = torch.nn.Sequential(
#             torch.nn.Linear(embedding_dim * 2, 128),
#             torch.nn.ReLU(),
#             torch.nn.Dropout(0.2),

#             torch.nn.Linear(128, 64),
#             torch.nn.ReLU(),

#             torch.nn.Linear(64, 1)
#         )

#     def build_user_embedding(
#         self,
#         history_items,
#         history_ratings
#     ):
#         history_embeds = self.item_embedding(history_items)

#         weights = history_ratings.unsqueeze(-1)

#         weight_sum = history_ratings.sum(
#             dim=1,
#             keepdim=True
#         )

#         mask = (
#             history_items != 0
#         ).unsqueeze(-1)

#         weighted = (
#             history_embeds *
#             weights *
#             mask
#         )

#         user_embedding = (
#             weighted.sum(dim=1)
#             /
#             weight_sum.clamp(min=1e-6)
#         )

#         return user_embedding, weight_sum

#     def forward(
#         self,
#         user_embedding,
#         target_items
#     ):
#         target_embedding = self.item_embedding(
#             target_items
#         )

#         x = torch.cat(
#             [user_embedding, target_embedding],
#             dim=1
#         )

#         return 5.0 * torch.sigmoid(
#             self.mlp(x).squeeze()
#         )


# # =========================================================
# # LOAD MODEL
# # =========================================================

# model = DynamicNCF(
#     num_items=len(item_to_index),
#     embedding_dim=32
# ).to(DEVICE)

# model.load_state_dict(
#     torch.load(
#         MODELS_DIR / "best_dynamic_ncf_online.pth",
#         map_location=DEVICE,
#         weights_only=True
#     )
# )

# model.eval()

# print("Model loaded successfully.")


# # =========================================================
# # RECOMMENDATION FUNCTION
# # =========================================================

# def recommend_movies(
#     user_id,
#     top_k=10
# ):
#     if user_id not in user_histories:
#         print("User not found.")
#         return []

#     history = user_histories[user_id]

#     watched_items = []
#     watched_ratings = []

#     for item_id, rating in history:
#         if item_id in item_to_index:
#             watched_items.append(
#                 item_to_index[item_id]
#             )
#             watched_ratings.append(rating)

#     if len(watched_items) == 0:
#         print("No valid history.")
#         return []

#     history_items_tensor = torch.tensor(
#         [watched_items],
#         dtype=torch.long,
#         device=DEVICE
#     )

#     history_ratings_tensor = torch.tensor(
#         [watched_ratings],
#         dtype=torch.float32,
#         device=DEVICE
#     )

#     with torch.inference_mode():

#         # Build User Embedding
#         user_embedding, _ = model.build_user_embedding(
#             history_items_tensor,
#             history_ratings_tensor
#         )

#         candidate_item_ids = []

#         for item_id in item_to_index.keys():

#             # Skip watched movies
#             if item_id in [x[0] for x in history]:
#                 continue

#             candidate_item_ids.append(item_id)

#         candidate_indices = torch.tensor(
#             [
#                 item_to_index[item_id]
#                 for item_id in candidate_item_ids
#             ],
#             dtype=torch.long,
#             device=DEVICE
#         )

#         repeated_user_embedding = user_embedding.repeat(
#             len(candidate_indices),
#             1
#         )

#         predictions = model(
#             repeated_user_embedding,
#             candidate_indices
#         )

#         top_indices = torch.topk(
#             predictions,
#             k=top_k
#         ).indices

#         raw_scores = model.mlp(
#             torch.cat(
#                 [repeated_user_embedding,
#                 model.item_embedding(candidate_indices)],
#                 dim=1
#             )
#         ).squeeze()

#         print(raw_scores[:10])

#         recommendations = []

#         for idx in top_indices:

#             item_id = candidate_item_ids[idx]

#             recommendations.append({
#                 "item_id": item_id,
#                 "predicted_rating": float(
#                     predictions[idx]
#                 )
#             })

#     return recommendations


# # =========================================================
# # TEST
# # =========================================================

# user_id = 1

# recommendations = recommend_movies(
#     user_id=user_id,
#     top_k=10
# )

# for rec in recommendations:
#     print(rec)