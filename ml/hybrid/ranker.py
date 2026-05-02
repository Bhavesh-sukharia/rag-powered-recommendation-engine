from __future__ import annotations


def blend_scores(cf_score: float, cb_score: float, cf_weight: float = 0.6) -> float:
    cb_weight = 1.0 - cf_weight
    return round((cf_score * cf_weight) + (cb_score * cb_weight), 4)