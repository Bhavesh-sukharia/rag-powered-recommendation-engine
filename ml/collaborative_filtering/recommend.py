import pickle
from model import CF_RecommenderSystem

with open("ml/artifacts/item_to_index.pkl", "rb") as f:
    item_to_index = pickle.load(f)

with open("ml/artifacts/index_to_item.pkl", "rb") as f:
    index_to_item = pickle.load(f)

num_items = len(item_to_index) + 1

recommender = CF_RecommenderSystem(

    model_path="ml/models/best_dynamic_ncf_online_debug.pth",

    num_items=num_items,

    item_to_index=item_to_index,

    index_to_item=index_to_item,

    embedding_dim=32

)

recommendations = recommender.recommend_movies(
    user_id=10,
    top_k=10
)

for recommendation in recommendations:

    print(recommendation)
    