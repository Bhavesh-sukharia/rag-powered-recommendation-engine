from __future__ import annotations


def chunk_and_embed(texts: list[str]) -> list[dict[str, object]]:
    return [{"chunk": text, "embedding": [0.0, 0.0, 0.0]} for text in texts]