from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp
import joblib
from sklearn.metrics.pairwise import cosine_similarity


BASE_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def load_artifacts():
    index_df = pd.read_csv(PROCESSED_DIR / "item_features_index.csv")
    feature_matrix = sp.load_npz(PROCESSED_DIR / "item_features.npz")
    vectorizer = joblib.load(PROCESSED_DIR / "tfidf_vectorizer.pkl")
    return index_df, feature_matrix, vectorizer


def _row_index_column(index_df: pd.DataFrame) -> str:
    if "row_idx" in index_df.columns:
        return "row_idx"
    if "index" in index_df.columns:
        return "index"
    raise KeyError("Expected 'row_idx' or 'index' column in item_features_index.csv")


def get_similar_items(item_id: str, index_df: pd.DataFrame, feature_matrix, top_k: int = 10):
    row_col = _row_index_column(index_df)
    row = index_df[index_df["item_id"].astype(str) == str(item_id)]
    if row.empty:
        return []

    idx = int(row[row_col].values[0])
    item_vec = feature_matrix[idx]
    scores = cosine_similarity(item_vec, feature_matrix).flatten()

    top_indices = np.argsort(scores)[::-1][1 : top_k + 1]
    top_items = index_df[index_df[row_col].isin(top_indices)].copy()
    top_items["score"] = scores[top_items[row_col].values]
    return top_items.sort_values("score", ascending=False).to_dict("records")


def get_similar_by_text(
    query_text: str,
    index_df: pd.DataFrame,
    feature_matrix,
    vectorizer,
    top_k: int = 10,
):
    row_col = _row_index_column(index_df)
    query_vec = vectorizer.transform([query_text])
    scores = cosine_similarity(query_vec, feature_matrix).flatten()
    top_indices = np.argsort(scores)[::-1][:top_k]
    top_items = index_df[index_df[row_col].isin(top_indices)].copy()
    top_items["score"] = scores[top_items[row_col].values]
    return top_items.sort_values("score", ascending=False).to_dict("records")


if __name__ == "__main__":
    index_df, feature_matrix, vectorizer = load_artifacts()
    print(f"Loaded artifacts: feature_matrix={feature_matrix.shape}, index_rows={len(index_df)}")
