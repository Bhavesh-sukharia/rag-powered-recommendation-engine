from fastapi import APIRouter, HTTPException
from app.models.movie import Movie
from app.core.database import db
from app.repositories.movie_repository import MovieRepository
from app.utils.logger import get_logger

router = APIRouter(prefix="/movies", tags=["movies"])
logger = get_logger(__name__)


@router.post("")
async def create_movie(movie: Movie):
    """Create a new movie."""
    logger.info("Received POST /movies with payload: title=%s, item_id=%s", movie.title, movie.item_id)
    repo = MovieRepository(db)
    
    try:
        # Check if movie with same item_id already exists
        existing = await repo.get_movie_by_item_id(movie.item_id)
        if existing:
            logger.warning("Movie creation failed: item_id=%s already exists", movie.item_id)
            raise HTTPException(status_code=400, detail=f"Movie with item_id {movie.item_id} already exists")
        
        # Create movie via repository
        created = await repo.create_movie(movie.dict())
        logger.info("Movie created successfully: item_id=%s, title=%s, id=%s", movie.item_id, movie.title, created["id"])
        
        return {
            "message": "Movie created successfully",
            "id": created["id"],
            "title": movie.title,
            "item_id": movie.item_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create movie: %s", str(e))
        raise HTTPException(status_code=400, detail=f"Failed to create movie: {str(e)}")


@router.get("")
async def list_movies(skip: int = 0, limit: int = 10):
    """List all movies with pagination."""
    movies = await Movie.find().skip(skip).limit(limit).to_list()
    return movies


@router.get("/{movie_id}")
async def get_movie(movie_id: str):
    """Get a specific movie by ID."""
    movie = await Movie.get(movie_id)
    if not movie:
        return {"error": "Movie not found"}
    return movie


@router.put("/{movie_id}")
async def update_movie(movie_id: str, movie_data: Movie):
    """Update a movie."""
    movie = await Movie.get(movie_id)
    if not movie:
        return {"error": "Movie not found"}
    
    await movie.set(movie_data.dict(exclude_unset=True))
    return movie
