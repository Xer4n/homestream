# app/db/models.py
from sqlalchemy import Table, Column, Integer, String
from app.db.database import metadata

movies_table = Table(
    "movies",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, nullable=False),
    Column("filename", String, nullable=False, unique=True),
)
