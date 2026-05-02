from __future__ import annotations


def build_faiss_index(vectors: list[list[float]]) -> dict[str, object]:
    return {"vector_count": len(vectors), "index": "faiss-placeholder"}