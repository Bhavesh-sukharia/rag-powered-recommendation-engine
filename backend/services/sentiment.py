from __future__ import annotations


def rerank_with_sentiment(items: list[dict[str, object]]) -> list[dict[str, object]]:
    return sorted(items, key=lambda item: item.get("score", 0), reverse=True)