from fastapi import FastAPI
from app.api import movies as movies_router

app = FastAPI(title="HomeStream")

app.include_router(movies_router.router)



@app.get("/")
async def read_root():
    return {"message": "Welcome to HomeStream"}
