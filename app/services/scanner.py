import os
from typing import List
from app.db.database import database
from app.db.models import movies_table

MOVIES_DIR = "./movies"
VIDEO_EXTENSIONS = ["mp4", "mkv", "webm", "avi", "mov"]

async def scan_and_update_db() -> List[dict]:
    """
    Scan movies folder, add new movies to the database, and return list of movies
    with all available formats for each movie.
    """
    if not os.path.exists(MOVIES_DIR):
        os.makedirs(MOVIES_DIR)

    # Filter files by supported video extensions
    files = [f for f in os.listdir(MOVIES_DIR) if any(f.lower().endswith(ext) for ext in VIDEO_EXTENSIONS)]

    # Group files by base name
    movie_groups = {}
    for file in files:
        name, ext = os.path.splitext(file)
        ext = ext[1:].lower()
        if name not in movie_groups:
            movie_groups[name] = {"formats": []}
        if ext not in movie_groups[name]["formats"]:
            movie_groups[name]["formats"].append(ext)

    movie_list = []

    # Process each movie group
    for base_name, data in movie_groups.items():
        # Check if movie already exists in DB
        query = movies_table.select().where(movies_table.c.title == base_name)
        existing = await database.fetch_one(query)

        if not existing:
            # Insert only once: use first format as representative filename
            first_format = data["formats"][0]
            filename = f"{base_name}.{first_format}"
            movie_id = await database.execute(
                movies_table.insert().values(title=base_name, filename=filename)
            )
        else:
            movie_id = existing["id"]

        # Append movie with all available formats
        movie_list.append({
            "id": movie_id,
            "title": base_name,
            "formats": data["formats"]
        })

    print(movie_list)
    return movie_list
