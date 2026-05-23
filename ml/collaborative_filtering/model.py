import torch
import torch.nn as nn
import torch.nn.functional as F


# Model only handle tensors
class DynamicNCF(nn.Module):
    def __init__(self, num_items, embedding_dim=32):
        super().__init__()

        self.item_embedding = nn.Embedding(
            num_items,
            embedding_dim,
            padding_idx=0
        )

        self.mlp = nn.Sequential(
            nn.Linear(embedding_dim * 2, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )

    def build_user_embedding(self, history_items, history_ratings):
        """
        Called ONCE to initialize embedding from history.
        history_items:   (B, seq_len) long tensor
        history_ratings: (B, seq_len) float tensor
        Returns: user_embedding (B, dim), weight_sum (B, 1)
        """
        history_embeds = self.item_embedding(history_items)          # (B, seq, dim)
        weights  = (history_ratings).unsqueeze(-1)               # (B, seq, 1)
        weight_sum  = history_ratings.sum(dim=1, keepdim=True)    # (B, 1)
        
        mask = (history_items != 0).unsqueeze(-1)          # (B, seq, 1)
        weighted = history_embeds * weights * mask             # (B, seq, dim)

        user_embedding = weighted.sum(dim=1) / weight_sum.clamp(min=1e-6)  # (B, dim)

        return user_embedding, weight_sum

    def update_user_embedding(self, user_embedding, weight_sum, new_item, new_rating):
        """
        Incrementally update a single user's embedding.
        user_embedding: (1, dim)
        weight_sum:     scalar or (1, 1)
        new_item:       (1,) long tensor
        new_rating:     float
        Returns: updated user_embedding (1, dim), updated weight_sum
        """
        new_item_embed = self.item_embedding(new_item)               # (1, dim)
        new_weight_sum = weight_sum + new_rating

        user_embedding = (
            user_embedding * weight_sum + new_item_embed * new_rating
        ) / new_weight_sum.clamp(min=1e-6)

        return user_embedding, new_weight_sum


    def forward(self, user_embedding, target_items):
        """
        user_embedding: (B, dim) — pre-built, passed in
        target_items:   (B,)    — item indices
        """
        target_embedding = self.item_embedding(target_items)         # (B, dim)
        x = torch.cat([user_embedding, target_embedding], dim=1)
        return 5.0 * torch.sigmoid(self.mlp(x).squeeze())    


# Recommender class. For utility functions, builds tensors and calls model 
class CF_RecommenderSystem:
    def __init__(
            self, 
            model_path,
            num_items,
            item_to_index: dict,
            index_to_item: dict,
            embedding_dim=32,
            device=None
    ):
        self.device = (
            device if device is not None else torch.device(
                "cuda" if torch.cuda.is_available() else "cpu"
            )
        )

        self.item_to_index = item_to_index
        self.index_to_item = index_to_item
        # self.item_id_to_title = item_id_to_title
        self.num_items = num_items

        self.model = DynamicNCF(num_items=num_items, embedding_dim=embedding_dim)

        self.model.load_state_dict(
            torch.load(model_path, map_location=self.device, weights_only=True)
            )

        self.model = self.model.to(self.device)

        self.model.eval()

        print("Model loaded successfully.")


    def build_user_embedding(self, user_id):
        if user_id in self.user_embeddings:
            cached = self.user_embeddings[user_id]
            return cached["embedding"].to(self.device), cached["weight_sum"].to(self.device)

        user_history    = self.user_histories[user_id][-50:]
        history_items   = [x[0] for x in user_history]
        history_ratings = [x[1] for x in user_history]

        history_items_tensor   = torch.tensor(history_items,   dtype=torch.long).unsqueeze(0).to(self.device)
        history_ratings_tensor = torch.tensor(history_ratings, dtype=torch.float32).unsqueeze(0).to(self.device)

        with torch.inference_mode():
            user_embedding, weight_sum = self.model.build_user_embedding(
                history_items_tensor,
                history_ratings_tensor
            )

        self.user_embeddings[user_id] = {
            "embedding":  user_embedding.detach().cpu(),
            "weight_sum": weight_sum.detach().cpu()
        }

        return user_embedding, weight_sum
    

    def build_user_embedding_from_history(self, rating_history):
        user_history = rating_history[-50:] if len(rating_history) > 50 else rating_history

        valid_history = [x for x in user_history if x["item_id"] in self.item_to_index]

        if len(valid_history) == 0:
            # raise ValueError("No valid movies found in rating history.")
            return None, None

        history_items = [self.item_to_index[x["item_id"]] for x in valid_history]

        history_ratings = [float(x["rating_number"]) for x in valid_history]

        history_items_tensor = torch.tensor(history_items, dtype=torch.long).unsqueeze(0).to(self.device)

        history_ratings_tensor = torch.tensor(history_ratings, dtype=torch.float32).unsqueeze(0).to(self.device)

        with torch.inference_mode():
            user_embedding, weight_sum = self.model.build_user_embedding(history_items_tensor, history_ratings_tensor)

        return user_embedding, weight_sum


    def update_user_embedding(self, user_id, old_user_embedding, old_weight_sum, item_id, rating):
        item_idx    = self.item_to_index[item_id]
        item_idx_tensor = torch.tensor([item_idx], dtype=torch.long).to(self.device)

        if old_user_embedding is None:
            return self.model.item_embedding(item_idx_tensor), (rating - 3)

        with torch.inference_mode():
            user_embedding, weight_sum = self.model.update_user_embedding(
                old_user_embedding,
                old_weight_sum,
                item_idx_tensor,
                rating
            )

        return user_embedding, weight_sum


    def tensor_to_embedding_payload(self, embedding, weight_sum):
        return {
            "embedding": (embedding.squeeze(0).detach().cpu().tolist()),

            "weight_sum": float(weight_sum.item())
        }
    
    def embedding_payload_to_tensor(self, embedding, weight_sum):
        return {
            "embedding": torch.tensor(embedding, dtype=torch.float32).to(self.device),

            "weight_sum": torch.tensor(weight_sum, dtype=torch.float32).to(self.device)
        }

    def predict_rating(self, user_id, item_id):
        user_embedding, _ = self.build_user_embedding(user_id)
        item_idx = self.item_to_index[item_id]

        item_idx_tensor = torch.tensor([item_idx],
                                   dtype=torch.long).to(self.device)
        
        with torch.inference_mode():
            prediction = self.model(user_embedding, item_idx_tensor)
        return prediction.item()
    
    def predict_at_once(self, user_embedding, candidate_indices):
        self.model.eval()
        user_embedding = torch.tensor(user_embedding, dtype=torch.float32).to(self.device)

        candidate_tensors = torch.tensor(candidate_indices, dtype=torch.long).to(self.device)

        repeated_user_embedding = user_embedding.repeat(len(candidate_indices), 1)

        with torch.inference_mode():
            predictions = self.model(repeated_user_embedding, candidate_tensors)
            print(f"Length of predictions: {len(predictions)}")
            print(f"predicted scores: {predictions}")
           
        return predictions
    
    def recommend_movies(self, user_embedding, rating_history, top_k=10):
        watched_movies = set([x[0] for x in rating_history])

        candidate_indices = [idx for idx in range(1, self.num_items) if idx not in watched_movies]

        predictions = self.predict_at_once(user_embedding, candidate_indices)
        with torch.inference_mode():
            top_scores, top_positions = torch.topk(predictions, k=top_k)

        recommendations = []

        for score, position in zip(top_scores.cpu().numpy(), top_positions.cpu().numpy()):
            item_idx = candidate_indices[position]
            item_id = self.index_to_item[item_idx]
            recommendations.append({
                "item_id": item_id,
                "predicted_rating": float(score)
            })

        return recommendations
    
    def show_user_history(
        self,
        user_id,
        history,
        top_n=20
    ):
        if history is None:
            print("No history found for this user.")
            return

        print("\nUSER HISTORY\n")

        for item_id, rating in history[-top_n:]:
            print(
                f"Rating: {rating:.1f} | {item_id}"
            )
    




if __name__ == "__main__":
    recommender = CF_RecommenderSystem(
    model_path="ml/models/best_dynamic_ncf_online.pth",
    num_items=100456,
    embedding_dim=32
)
