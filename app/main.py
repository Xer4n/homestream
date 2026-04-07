# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.scanner import scan_and_update_db
from app.api import movies as movies_router

app = FastAPI(title="HomeStream")

# Templates folder
templates = Jinja2Templates(directory="app/templates")

# Include API router
app.include_router(movies_router.router)

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    """
    Render homepage with movie list.
    """
    # Fetch movies from DB
    movies = await scan_and_update_db()
    print(movies)

    # Convert to plain dicts
    movies = [{"id": m["id"], "title": m["title"]} for m in movies]

    # Correct order: first template name, then context dict
    return templates.TemplateResponse(request, name="index.html", context={"movies": movies})
