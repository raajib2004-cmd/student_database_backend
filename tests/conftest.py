"""
Pytest fixtures shared across all tests.

IMPORTANT: Tests run against a SEPARATE database (student_db_test) so
they never wipe your development data.
"""
import os

from dotenv import load_dotenv

# Load .env BEFORE anything else so DATABASE_URL and GEMINI_API_KEY are available
load_dotenv()

# Override the DATABASE_URL BEFORE importing app modules so SQLAlchemy
# uses the test database.
os.environ["DATABASE_URL"] = (
    "mysql+pymysql://root:@localhost:3306/student_db_test"
)

import pytest
from fastapi.testclient import TestClient

from app.database.connection import Base, SessionLocal, engine
from app.main import app
from app.models.student import Student  # noqa: F401


# ---------------------------------------------------------------------
# Session-scoped setup: create all tables once before tests run
# ---------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all tables in the test database before the test session starts."""
    Base.metadata.create_all(bind=engine)
    yield


# ---------------------------------------------------------------------
# Function-scoped cleanup: empty the students table between tests
# ---------------------------------------------------------------------
@pytest.fixture(autouse=True)
def clean_students_table():
    """Delete all rows from `students` before AND after each test."""
    db = SessionLocal()
    try:
        db.query(Student).delete()
        db.commit()
    finally:
        db.close()
    yield
    db = SessionLocal()
    try:
        db.query(Student).delete()
        db.commit()
    finally:
        db.close()


# ---------------------------------------------------------------------
# HTTP client fixture
# ---------------------------------------------------------------------
@pytest.fixture
def client():
    """A FastAPI TestClient that talks to the app in-process."""
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------
# Sample student payload
# ---------------------------------------------------------------------
@pytest.fixture
def sample_student():
    """A valid student payload for tests."""
    return {
        "student_id": "T001",
        "name": "Test Student",
        "email": "test.student@example.com",
        "phone": "9000000001",
        "department": "CSE",
        "year": 2,
        "cgpa": 8.0,
        "address": "Test Address",
        "bio": "Interested in machine learning and Python.",
    }