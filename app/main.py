"""
FastAPI application entry point.

- Configures the app (title, version)
- Includes the students router (CRUD endpoints)
- Provides a root health check
"""
from fastapi import FastAPI

from app.routes import students

app = FastAPI(
    title="Student Database Backend",
    description="Backend for managing student information with AI chatbot",
    version="0.3.0",
)

# Attach the students router — all its endpoints now live under /students
app.include_router(students.router)


@app.get("/", tags=["Health"])
def root():
    """Health check endpoint."""
    return {"message": "Student Database Backend is running"}