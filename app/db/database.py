# app/db/database.py
from sqlalchemy import MetaData, create_engine, Table, Column, Integer, String
from databases import Database
import os

# ---------------------------
# Database URL & setup
# ---------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./homestream.db")

# SQLAlchemy engine (for creating tables)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Database metadata
metadata = MetaData()
# ---------------------------
# Async database connection
# ---------------------------
database = Database(DATABASE_URL)
