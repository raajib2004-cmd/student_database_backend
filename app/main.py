"""
FastAPI application entry point.

- Configures global API metadata (shown in Swagger)
- Includes the students router (CRUD endpoints)
- Provides a root health check
"""
from fastapi import FastAPI

from app.routes import students

# Markdown-supported description shown at the top of /docs
API_DESCRIPTION = """
Backend API for managing student information.

## Features

- ✅ **Full CRUD** — create, read, update, delete students
- ✅ **Validation** — email format, CGPA range, year range, required fields
- ✅ **Error handling** — clean JSON errors for duplicates and missing students
- ✅ **Auto documentation** — this Swagger UI is generated from the code
- 🚧 **AI chatbot** — powered by LangGraph + Google Gemini (coming in later phases)

## Notes

- All endpoints return JSON.
- Duplicate `student_id` or `email` returns **409 Conflict**.
- Missing student returns **404 Not Found**.
- Validation errors return **422 Unprocessable Entity**.
"""

TAGS_METADATA = [
    {
        "name": "Health",
        "description": "Health check endpoints to verify the API is running.",
    },
    {
        "name": "Students",
        "description": "CRUD operations for student records. "
        "Every student has a unique `student_id` (e.g., `S101`) and a unique `email`.",
    },
]

app = FastAPI(
    title="Student Database Backend",
    description=API_DESCRIPTION,
    version="0.4.0",
    contact={
        "name": "Rajib Das",
        "url": "https://github.com/raajib2004-cmd",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=TAGS_METADATA,
)

# Attach the students router — all its endpoints now live under /students
app.include_router(students.router)


@app.get(
    "/",
    tags=["Health"],
    summary="Health check",
    description="Returns a simple message confirming the API is running.",
)
def root():
    """Health check endpoint."""
    return {"message": "Student Database Backend is running"}