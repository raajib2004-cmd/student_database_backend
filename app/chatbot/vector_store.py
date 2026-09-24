"""
Chroma vector store integration for semantic student search.

This module:
- Creates a persistent Chroma collection at ./chroma_data
- Uses Google Gemini embeddings via langchain-google-genai
- Provides:
    * index_student(student) — add/update a single student's vector
    * delete_student(student_id) — remove from index
    * semantic_search(query, k) — find most similar bios
    * reindex_all() — rebuild index from current DB rows
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

# Persistent storage folder (gitignored)
CHROMA_DIR = Path(__file__).resolve().parents[2] / "chroma_data"
CHROMA_DIR.mkdir(exist_ok=True)

COLLECTION_NAME = "student_bios"

# Google Gemini embedding model
_embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY"),
)

# The persistent Chroma instance — created once and reused.
_vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=_embeddings,
    persist_directory=str(CHROMA_DIR),
)


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------
def index_student(student) -> None:
    """
    Add or update a student in the vector index.
    Only students WITH a bio are indexed — students without bio are skipped.
    """
    if not student or not student.bio or not student.bio.strip():
        delete_student(student.student_id)
        return

    _vector_store.add_texts(
        texts=[student.bio],
        metadatas=[
            {
                "student_id": student.student_id,
                "name": student.name,
                "department": student.department,
                "cgpa": student.cgpa,
                "year": student.year,
            }
        ],
        ids=[student.student_id],
    )


def delete_student(student_id: str) -> None:
    """Remove a student from the vector index (no-op if not present)."""
    try:
        _vector_store.delete(ids=[student_id])
    except Exception:
        pass


def semantic_search(query: str, k: int = 5) -> list[dict]:
    """
    Find the top-k students whose bio is semantically closest to `query`.
    Returns a list of dicts with student metadata and similarity score.
    """
    results = _vector_store.similarity_search_with_relevance_scores(query, k=k)
    hits = []
    for doc, score in results:
        meta = doc.metadata or {}
        hits.append(
            {
                "student_id": meta.get("student_id"),
                "name": meta.get("name"),
                "department": meta.get("department"),
                "year": meta.get("year"),
                "cgpa": meta.get("cgpa"),
                "bio": doc.page_content,
                "similarity": round(float(score), 3),
            }
        )
    return hits


def reindex_all() -> int:
    """
    Rebuild the entire vector index from the current DB contents.
    Returns the number of students indexed.
    """
    global _vector_store

    from app.database.connection import SessionLocal
    from app.services import student_service

    # Clear existing collection
    try:
        _vector_store.delete_collection()
    except Exception:
        pass

    # Recreate
    _vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=_embeddings,
        persist_directory=str(CHROMA_DIR),
    )

    db = SessionLocal()
    try:
        students = student_service.get_students(db, skip=0, limit=10000)
        indexed = 0
        for s in students:
            if s.bio and s.bio.strip():
                index_student(s)
                indexed += 1
        return indexed
    finally:
        db.close()