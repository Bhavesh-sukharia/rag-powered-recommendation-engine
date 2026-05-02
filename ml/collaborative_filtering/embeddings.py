from __future__ import annotations


def build_user_item_embeddings(interactions: list[dict[str, object]]) -> dict[str, object]:
    return {"count": len(interactions), "embeddings": []}