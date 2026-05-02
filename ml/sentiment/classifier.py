from __future__ import annotations


def classify_sentiment(text: str) -> dict[str, object]:
    score = 0.0 if not text else 0.5
    label = "neutral" if score == 0.0 else "positive"
    return {"label": label, "score": score}