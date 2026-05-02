from __future__ import annotations


def rank_items(user_id: str, query: str, limit: int = 10) -> list[dict[str, object]]:
    del user_id, query
    return [
        {"item_id": f"item-{index + 1}", "score": round(1.0 - index * 0.05, 3)}
        for index in range(max(limit, 0))
    ]