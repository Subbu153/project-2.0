
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import sqlalchemy
from urllib.parse import quote_plus

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "task_manager_db")

# URL encode credentials to handle special characters
encoded_user = quote_plus(DB_USER) if DB_USER else ""
encoded_password = quote_plus(DB_PASSWORD) if DB_PASSWORD else ""

# Construct connection URL
DATABASE_URL = f"mysql+pymysql://{encoded_user}:{encoded_password}@{DB_HOST}/{DB_NAME}"

# Create the engine
# We might need to create the database first if it doesn't exist.
# A common pattern is to connect to the server without a DB to create it.
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # Helper to create database if not exists
    # Connect to default database (mysql or sys) to create the target db
    server_url = f"mysql+pymysql://{encoded_user}:{encoded_password}@{DB_HOST}"
    server_engine = create_engine(server_url)
    with server_engine.connect() as conn:
        conn.execute(sqlalchemy.text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
    
    # Now create tables
    import models
    models.Base.metadata.create_all(bind=engine)
