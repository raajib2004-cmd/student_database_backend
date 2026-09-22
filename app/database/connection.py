"""
Database connection setup for SQLAlchemy.

This module:
- Reads DATABASE_URL from the .env file
- Creates the SQLAlchemy engine (connection to MariaDB)
- Provides a Base class that all models inherit from
- Provides a get_db() dependency for FastAPI routes
"""
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load variables from .env into os.environ
load_dotenv()

# Read the database URL from the environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Did you create the .env file? "
        "See .env.example for the expected format."
    )

# The engine is the interface to the database.
# - pool_pre_ping=True: checks a connection is alive before using it.
# - echo=False: set True to log SQL statements (useful for debugging).
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)

# SessionLocal is a factory that creates new database sessions.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class for all ORM models.
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session per request.

    Usage in a route:
        def my_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()