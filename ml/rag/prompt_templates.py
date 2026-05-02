from __future__ import annotations


def recommendation_prompt(item_name: str, evidence: list[str]) -> str:
    support = ", ".join(evidence) if evidence else "system signals"
    return f"Explain why {item_name} is a strong recommendation using {support}."