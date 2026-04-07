import os
from typing import List

MOVIES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "movies")
VIDEO_EXTENSIONS = [".mp4", ".avi", ".mkv"]


def scan_movies() -> List[str]:
    """Scan the movies directory and return a list of video file paths."""
    movies = []
    if not os.path.exists(MOVIES_DIR):
        os.makedirs(MOVIES_DIR)
    for file in os.listdir(MOVIES_DIR):
        if any(file.lower().endswith(ext) for ext in VIDEO_EXTENSIONS):
            movies.append(file)
    return movies
