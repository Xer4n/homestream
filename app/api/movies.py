# app/api/movies.py
import os
from typing import List
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from app.db.database import database
from app.db.models import movies_table

from app.services.scanner import MOVIES_DIR, VIDEO_EXTENSIONS

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# ---------------------------
# Movie scanning & DB update
# ---------------------------
async def scan_and_update_db() -> List[dict]:
    """
    Scan movies folder, add new movies to DB, return list of movies.
    Supports multiple formats.
    """
    if not os.path.exists(MOVIES_DIR):
        os.makedirs(MOVIES_DIR)

    files = [f for f in os.listdir(MOVIES_DIR)
             if any(f.lower().endswith(ext) for ext in VIDEO_EXTENSIONS)]
    movie_list = []

    for file in files:
        base_name, ext = os.path.splitext(file)
        ext = ext.lstrip(".").lower()
        query = movies_table.select().where(movies_table.c.filename == file)
        existing = await database.fetch_one(query)

        if not existing:
            insert_query = movies_table.insert().values(title=base_name, filename=file)
            movie_id = await database.execute(insert_query)
            movie_list.append({"id": movie_id, "title": base_name})
        else:
            movie_list.append({"id": existing["id"], "title": existing["title"]})

    return movie_list

# ---------------------------
# Format detection
# ---------------------------
def get_movie_formats(base_name: str) -> List[str]:
    """
    Returns a list of available formats for a movie based on its base name.
    """
    formats = []
    for ext in VIDEO_EXTENSIONS:
        file_path = os.path.join(MOVIES_DIR, f"{base_name}.{ext}")
        if os.path.exists(file_path):
            formats.append(ext)
    return formats

# ---------------------------
# Streaming page (HTML)
# ---------------------------
@router.get("/stream/{movie_id}", response_class=HTMLResponse)
async def streaming_page(movie_id: int, request: Request):
    """
    Render streaming page with <video> player and format selection.
    """
    query = movies_table.select().where(movies_table.c.id == movie_id)
    movie = await database.fetch_one(query)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    base_name = movie["title"]
    available_formats = get_movie_formats(base_name)
    if not available_formats:
        raise HTTPException(status_code=404, detail="No video files found")

    format = available_formats[0]
    video_src = f"/stream-file/{movie_id}?format={format}"

    return templates.TemplateResponse(
        request,
        name="stream.html",
        context={
            "request": request,
            "movie": movie,
            "video_src": video_src,
            "available_formats": available_formats
        }
    )

# ---------------------------
# Streaming raw bytes
# ---------------------------
@router.get("/stream-file/{movie_id}")
async def stream_file(movie_id: int, format: str = None, request: Request = None):
    """
    Stream movie file with Range support for HTML5 player.
    """
    query = movies_table.select().where(movies_table.c.id == movie_id)
    movie = await database.fetch_one(query)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    base_name = movie["title"]
    available_formats = get_movie_formats(base_name)
    if not available_formats:
        raise HTTPException(status_code=404, detail="No video files found")

    if format is None or format not in available_formats:
        format = available_formats[0]

    filename = f"{base_name}.{format}"
    movie_path = os.path.join(MOVIES_DIR, filename)
    if not os.path.exists(movie_path):
        raise HTTPException(status_code=404, detail=f"Movie file not found: {filename}")

    mime_map = {
        "mp4": "video/mp4",
        "webm": "video/webm",
        "mkv": "video/x-matroska",
        "avi": "video/x-msvideo",
        "mov": "video/quicktime",
    }
    media_type = mime_map.get(format, f"video/{format}")

    file_size = os.path.getsize(movie_path)
    headers = {}
    start = 0
    end = file_size - 1
    status_code = 200

    range_header = request.headers.get("range") if request else None
    if range_header:
        bytes_range = range_header.replace("bytes=", "").split("-")
        start = int(bytes_range[0])
        if bytes_range[1]:
            end = int(bytes_range[1])
        status_code = 206
        headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"
        headers["Accept-Ranges"] = "bytes"

    headers["Content-Length"] = str(end - start + 1)

    def iter_file(path, start_byte, end_byte, chunk_size=1024*1024):
        with open(path, "rb") as f:
            f.seek(start_byte)
            remaining = end_byte - start_byte + 1
            while remaining > 0:
                read_bytes = min(chunk_size, remaining)
                data = f.read(read_bytes)
                if not data:
                    break
                yield data
                remaining -= len(data)

    return StreamingResponse(
        iter_file(movie_path, start, end),
        media_type=media_type,
        status_code=status_code,
        headers=headers,
    )
