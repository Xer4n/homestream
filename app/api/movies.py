from fastapi import APIRouter
from ..services.scanner import scan_movies

router = APIRouter()

@router.get("/movies")
async def get_movies():
    """Get a list of all movies."""
    movies = scan_movies()
    return movies
