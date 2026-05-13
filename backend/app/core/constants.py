"""
Application constants.
"""

# Recommendation parameters
MIN_RATING = 0.0
MAX_RATING = 5.0
DEFAULT_RECOMMENDATION_COUNT = 10

# Cache TTL (seconds)
CACHE_TTL_RATINGS = 3600  # 1 hour
CACHE_TTL_RECOMMENDATIONS = 1800  # 30 minutes
CACHE_TTL_USER_DATA = 7200  # 2 hours

# Model weights for hybrid recommendations
CF_WEIGHT = 0.4
CB_WEIGHT = 0.4
RAG_WEIGHT = 0.2

# Sentiment thresholds
POSITIVE_SENTIMENT_THRESHOLD = 0.6
NEGATIVE_SENTIMENT_THRESHOLD = 0.4
