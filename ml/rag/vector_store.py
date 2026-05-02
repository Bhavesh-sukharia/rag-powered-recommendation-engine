from __future__ import annotations


def upsert_vectors(vectors: list[dict[str, object]]) -> dict[str, object]:
    return {"stored": len(vectors)}