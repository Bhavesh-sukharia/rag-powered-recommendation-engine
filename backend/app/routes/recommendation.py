"""
Recommendation routes.
"""
from fastapi import APIRouter, HTTPException
from app.models.recommendation import RecommendationRequest, MovieRecommendation
from app.models.movie import Movie
from app.repositories.user_repository import UserRepository
from app.repositories.movie_repository import MovieRepository
# from app.services.cb_service import CBService
# from app.services.cf_service import cf_recommender
from app.services.hybrid_service import HybridService
from app.core.database import db
from app.utils.logger import get_logger

router = APIRouter(
    prefix="/api/recommendations",
    tags=["recommendations"],
)

logger = get_logger(__name__)

# Initialize services
# cb_service = CBService()
# cf_service = CFService()
hybrid_service = HybridService()



# sentiment bucketing removed: sentiment weight is not used


@router.post("")
async def get_weighted_recommendations(request: RecommendationRequest):
    """
    Get weighted recommendations based on CB, CF.
    
    Request body:
    {
        "username": "user123",
        "cb_weight": 0.50,
        "cf_weight": 0.50,
        "count": 20
    }
    """
    user_repo = UserRepository(db)
    movie_repo = MovieRepository(db)
    
    # Get user by username
    user = await user_repo.get_user_by_username(request.username)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{request.username}' not found")
    
    user_id = user["_id"]
    ratings = user["ratings"]
    embedding = user["cf_embedding"]
    logger.info(user_id)
    logger.info("user_embedding: %s", embedding)
    
    logger.info(
        "Getting weighted recommendations for user=%s with weights: cb=%s, cf=%s",
        request.username,
        request.cb_weight,
        request.cf_weight,
    )
    
    # Ensure we return at least 20 recommendations
    count = max(request.count, 20)

    # Get scores from each service (request more candidates than needed)
    # cb_items, cb_scores = cb_service.get_recommendations(user_id, count * 2)
    # cf_items, cf_scores = cf_service.get_recommendations(user_id, count * 2)
    
    # # Create a combined score dictionary
    # combined_scores = {}
    
    # # Add CB scores
    # for item_id, score in zip(cb_items, cb_scores):
    #     if item_id not in combined_scores:
    #         combined_scores[item_id] = {"cb_score": 0.0, "cf_score": 0.0}
    #     combined_scores[item_id]["cb_score"] = score
    
    # # Add CF scores
    # for item_id, score in zip(cf_items, cf_scores):
    #     if item_id not in combined_scores:
    #         combined_scores[item_id] = {"cb_score": 0.0, "cf_score": 0.0}
    #     combined_scores[item_id]["cf_score"] = score
    
    # # sentiment scores removed from combination (unused)
    
    # # Calculate weighted combined score
    # for item_id in combined_scores:
    #     cb = combined_scores[item_id]["cb_score"]
    #     cf = combined_scores[item_id]["cf_score"]
    #     combined = cb * request.cb_weight + cf * request.cf_weight
    #     combined_scores[item_id]["combined_score"] = combined
    
    # # Sort by combined score
    # sorted_items = sorted(
    #     combined_scores.items(), key=lambda x: x[1]["combined_score"], reverse=True
    # )[:count]

    # =========================================
    # Hybrid Recommendations
    # =========================================

    hybrid_results = (
        hybrid_service.get_recommendations(
            user_id=user_id,
            rating_history=ratings,
            alpha=request.cf_weight,
            count=count
        )
    )

    sorted_items = []

    for result in hybrid_results:

        sorted_items.append(

            (
                result["item_id"],

                {
                    "combined_score": result[
                        "hybrid_score"
                    ],

                    "cb_score": result[
                        "cb_score"
                    ],

                    "cf_score": result[
                        "cf_score"
                    ]
                }
            )
        )
    
    # Fetch movie details from database
    movie_item_ids = [item_id for item_id, _ in sorted_items]
    movies = await movie_repo.get_movies(movie_item_ids)
    
    # Create a lookup for movies by item_id
    movies_by_item_id = {movie.get("item_id"): movie for movie in movies}
    
    # Build response
    recommendations = []
    for item_id, scores in sorted_items:
        movie_data = movies_by_item_id.get(item_id)
        if movie_data:
            # Convert MongoDB ObjectId to string
            movie_data["id"] = str(movie_data.get("_id", item_id))
            movie_data.pop("_id", None)
            
            rec = MovieRecommendation(
                movie=Movie(**movie_data),
                combined_score=scores["combined_score"],
                cb_score=scores["cb_score"],
                cf_score=scores["cf_score"],
            )
            recommendations.append(rec)
    
    logger.info(
        "Returned %d recommendations for user=%s",
        len(recommendations),
        request.username,
    )
    
    return {
        "username": request.username,
        "recommendations": recommendations,
    }
