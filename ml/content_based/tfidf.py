from __future__ import annotations


def build_tfidf_matrix(documents: list[str]) -> dict[str, object]:
    return {"document_count": len(documents), "matrix": []}