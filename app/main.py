"""
FastAPI application entry point.

- Configures global API metadata (shown in Swagger)
- Includes the students router (CRUD endpoints)
- Includes the chat router (AI chatbot via LangGraph + Gemini)
- Provides a root health check
"""
from fastapi import FastAPI

from app.routes import chat, students

# Markdown-supported description shown at the top of /docs
API_DESCRIPTION = """
Backend API for managing student information with an AI chatbot.

## Features

- ✅ **Full CRUD** — create, read, update, delete students
- ✅ **Validation** — email format, CGPA range, year range, required fields
- ✅ **Error handling** — clean JSON errors for duplicates and missing students
- ✅ **AI chatbot** — LangGraph + Google Gemini with tool calling
- ✅ **Hybrid retrieval** — SQL for structured queries, vector search for meaning
- ✅ **Swagger documentation** — every endpoint documented with examples

## Chatbot Capabilities

The `/chat` endpoint can answer questions like:

- **Structured queries** → *"Show me student S101"*, *"How many CSE students?"*, *"Find students with CGPA above 8"*
- **Semantic queries** → *"Who knows machine learning?"*, *"Anyone into mobile apps?"*, *"Find students with robotics experience"*
- **General chat** → *"Hello"*, *"What can you do?"*

The chatbot **never invents student data** — every fact comes from a real database or vector query.

## Notes

- Duplicate `student_id` or `email` returns **409 Conflict**.
- Missing student returns **404 Not Found**.
- Validation errors return **422 Unprocessable Entity**.
- Chatbot dependency health: `GET /chat/health`.
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
    {
        "name": "Chatbot",
        "description": "AI chatbot powered by LangGraph + Google Gemini. "
        "Classifies questions into greeting / database_query / semantic_query / general, "
        "then uses SQL or vector search to answer.",
    },
]

app = FastAPI(
    title="Student Database Backend",
    description=API_DESCRIPTION,
    version="0.9.0",
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

# Attach routers — endpoints now live under /students and /chat
app.include_router(students.router)
app.include_router(chat.router)


@app.get(
    "/",
    tags=["Health"],
    summary="Health check",
    description="Returns a simple message confirming the API is running.",
)
def root():
    """Health check endpoint."""
    return {"message": "Student Database Backend is running"}