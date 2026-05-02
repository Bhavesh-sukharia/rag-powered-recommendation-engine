from __future__ import annotations


def encode_documents(documents: list[str]) -> list[list[float]]:
    return [[0.0] * 3 for _ in documents]