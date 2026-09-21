"""
FastAPI application entry point.

Phase 1: Only a health check endpoint exists.
CRUD routes will be added in Phase 3.
"""
from fastapi import FastAPI

app = FastAPI(
    title="Student Database Backend",
    description="Backend for managing student information with AI chatbot",
    version="0.1.0",
)


@app.get("/")
def root():
    """Health check endpoint."""
    return {"message": "Student Database Backend is running"}