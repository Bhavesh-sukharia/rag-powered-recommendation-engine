from __future__ import annotations


def build_explanation(item_id: str, evidence: list[str]) -> str:
    snippets = ", ".join(evidence) if evidence else "available catalog signals"
    return f"{item_id} is recommended based on {snippets}."