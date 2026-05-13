"""
Helper utility functions.
"""
import uuid
from typing import Any, Dict


def generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid.uuid4())


def normalize_scores(scores: list) -> list:
    """
    Normalize scores to 0-1 range.
    
    Args:
        scores: List of scores
        
    Returns:
        Normalized scores
    """
    if not scores:
        return []
    
    min_score = min(scores)
    max_score = max(scores)
    
    if min_score == max_score:
        return [0.5] * len(scores)
    
    return [(s - min_score) / (max_score - min_score) for s in scores]


def combine_scores(score_dict: Dict[str, list], weights: Dict[str, float]) -> list:
    """
    Combine multiple scores using weights.
    
    Args:
        score_dict: Dictionary of score lists
        weights: Weights for each score type
        
    Returns:
        Combined scores
    """
    pass
