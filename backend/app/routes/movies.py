from typing import Optional

from fastapi import APIRouter, HTTPException
from app.models.movie import Movie
from app.core.database import db
from app.repositories.movie_repository import MovieRepository
from app.utils.logger import get_logger

router = APIRouter(prefix="/api/movies", tags=["movies"])
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
    repo = MovieRepository(db)
    movies = await repo.list_movies(skip=skip, limit=limit)
    return movies


@router.get("/search")
async def search_movies(
    q: str = "",
    page: int = 1,
    limit: int = 20,
    genre: Optional[str] = None,
    sort: str = "rating",
):
    """Search movies with pagination and optional genre/sort filters."""
    repo = MovieRepository(db)
    return await repo.search_movies(query=q, page=page, limit=limit, genre=genre, sort=sort)


@router.get("/count")
async def count_movies():
    """Return total number of movies in the database."""
    repo = MovieRepository(db)
    try:
        total = await repo.count_movies()
        return {"count": total}
    except Exception as e:
        logger.error("Failed to count movies: %s", str(e))
        raise HTTPException(status_code=500, detail="Failed to count movies")


@router.get("/{movie_id}")
async def get_movie(movie_id: str):
    """Get a specific movie by ID."""
    repo = MovieRepository(db)
    movie = await repo.get_movie(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.put("/{movie_id}")
async def update_movie(movie_id: str, movie_data: Movie):
    """Update a movie."""
    repo = MovieRepository(db)
    movie = await repo.get_movie(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    try:
        from bson import ObjectId
        result = await repo.collection.update_one(
            {"_id": ObjectId(movie_id)},
            {"$set": movie_data.dict(exclude_unset=True)}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Failed to update movie")
        
        updated = await repo.get_movie(movie_id)
        return updated
    except Exception as e:
        logger.error("Failed to update movie: %s", str(e))
        raise HTTPException(status_code=400, detail=f"Failed to update movie: {str(e)}")
