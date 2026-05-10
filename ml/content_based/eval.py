from pathlib import Path
import sys

# Ensure repo root is on sys.path so we can import the model module
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import pandas as pd
from ml.content_based.model import load_artifacts, get_similar_items


def main():
    index_df, feature_matrix, vectorizer = load_artifacts()

    movies_path = REPO_ROOT / "data" / "processed" / "movies.csv"
    movie_df = pd.read_csv(movies_path)

    # Pick a few positions (replace with specific IDs if you prefer)
    positions = [0, 42, 200]
    test_items = []
    for p in positions:
        if p < len(index_df):
            test_items.append(str(index_df["item_id"].iloc[p]))

    if not test_items:
        print("No test items available in index.")
        return

    for item in test_items:
        results = get_similar_items(item, index_df, feature_matrix, top_k=10)
        print(f"\nTop 10 similar to item_id={item}:")
        if not results:
            print("  (no results)")
            continue
        for r in results:
            item_id = r.get("item_id")
            score = r.get("score", 0)
            title_row = movie_df[movie_df["item_id"] == int(item_id)]
            title = title_row["title"].values[0] if not title_row.empty else "<unknown>"
            print(f"  {item_id}\t score={score:.3f}\t title={title}")


if __name__ == "__main__":
    main()
