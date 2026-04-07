# initdb.py
from app.db.database import engine, metadata
from app.db import models  # ensures all tables are registered

metadata.create_all(engine)
print("Database initialized:", metadata.tables.keys())
