from __future__ import annotations


def extract_aspects(text: str) -> list[str]:
    return [phrase.strip() for phrase in text.split(",") if phrase.strip()]