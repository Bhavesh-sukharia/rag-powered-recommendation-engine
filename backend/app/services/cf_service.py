"""
# Collaborative Filtering recommendation service.
# """
# from typing import List, Dict, Tuple
# import random


# class CFService:
#     """Service for collaborative filtering recommendations."""
    
#     def __init__(self):
#         """Initialize CF service."""
#         pass
    
#     def load_models(self):
#         """Load pre-trained CF models."""
#         pass
    
#     def get_recommendations(
#         self,
#         user_id: int,
#         count: int = 10
#     ) -> Tuple[List[int], List[float]]:
#         """
#         Get collaborative filtering recommendations.
        
#         Args:
#             user_id: User ID
#             count: Number of recommendations
            
#         Returns:
#             Tuple of (movie_ids, scores)
#         """
#         # Hardcoded movie IDs from the dataset
#         available_items = list(range(1, 101))  # item_id range
        
#         # Return random movies with scores for now
#         selected_items = random.sample(available_items, min(count, len(available_items)))
#         scores = [random.uniform(0.5, 1.0) for _ in selected_items]
        
#         return selected_items, scores
    
#     def get_user_embedding(self, user_id: int) -> List[float]:
#         """Get user embedding vector."""
#         return [random.random() for _ in range(64)]


import pickle
import sys
from pathlib import Path
import os
PROJECT_ROOT = Path(__file__).resolve().parents[3]


sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "backend"))

from ml.collaborative_filtering.model import CF_RecommenderSystem
from app.core.config import get_settings

settings = get_settings()

with open(settings.ITEM_TO_INDEX_PATH, "rb") as f:
    ITEM_TO_INDEX = pickle.load(f)

with open(settings.INDEX_TO_ITEM_PATH, "rb") as f:
    INDEX_TO_ITEM = pickle.load(f)

MODEL_PATH = os.path.join(
    PROJECT_ROOT,
    "ml",
    "models",
    "best_dynamic_ncf_online_debug.pth"
)

cf_recommender = CF_RecommenderSystem(
    model_path=MODEL_PATH,
    num_items=99224,
    item_to_index=ITEM_TO_INDEX,
    index_to_item=INDEX_TO_ITEM,
)