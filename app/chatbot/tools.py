"""
Tools the chatbot can use to access student data.

This file has TWO layers:
1. Plain Python functions (`find_student_by_student_id`, etc.) — used directly by tests.
2. LangChain `@tool` wrappers (`tool_find_student_by_student_id`, etc.) — exposed to Gemini
   so it can call them during `database_query_node` and `semantic_query_node`.

The docstrings on the `@tool` wrappers are important — Gemini reads them to decide
which tool to call for a given question.
"""
from langchain_core.tools import tool

from app.chatbot.vector_store import semantic_search as _semantic_search
from app.database.connection import SessionLocal
from app.services import student_service


# =====================================================================
# Plain Python functions
# =====================================================================
def find_student_by_student_id(student_id: str) -> dict | None:
    """Look up a student by their public student_id (e.g., "S101")."""
    db = SessionLocal()
    try:
        student = student_service.get_student_by_student_id(db, student_id)
        return _student_to_dict(student) if student else None
    finally:
        db.close()


def find_students_by_name(name: str) -> list[dict]:
    """
    Search for students whose name contains `name` (case-insensitive).
    Returns a list (possibly empty) of matching students.
    """
    db = SessionLocal()
    try:
        students = student_service.get_students(db, skip=0, limit=1000)
        needle = name.lower().strip()
        matches = [s for s in students if needle in s.name.lower()]
        return [_student_to_dict(s) for s in matches]
    finally:
        db.close()


def list_students(limit: int = 20) -> list[dict]:
    """Return up to `limit` students (default 20)."""
    db = SessionLocal()
    try:
        students = student_service.get_students(db, skip=0, limit=limit)
        return [_student_to_dict(s) for s in students]
    finally:
        db.close()


def count_students_in_department(department: str) -> int:
    """Count how many students are in the given department (case-insensitive)."""
    db = SessionLocal()
    try:
        students = student_service.get_students(db, skip=0, limit=10000)
        return sum(1 for s in students if s.department.lower() == department.lower())
    finally:
        db.close()


def find_students_by_cgpa(min_cgpa: float = 0.0, max_cgpa: float = 10.0) -> list[dict]:
    """Return students whose CGPA is between `min_cgpa` and `max_cgpa` (inclusive)."""
    db = SessionLocal()
    try:
        students = student_service.get_students(db, skip=0, limit=10000)
        matches = [s for s in students if min_cgpa <= s.cgpa <= max_cgpa]
        return [_student_to_dict(s) for s in matches]
    finally:
        db.close()


# =====================================================================
# Helper
# =====================================================================
def _student_to_dict(student) -> dict:
    """Convert a Student ORM object into a plain dict."""
    return {
        "student_id": student.student_id,
        "name": student.name,
        "email": student.email,
        "phone": student.phone,
        "department": student.department,
        "year": student.year,
        "cgpa": student.cgpa,
        "address": student.address,
    }


# =====================================================================
# LangChain tool wrappers (exposed to Gemini)
# =====================================================================
# These wrap the plain functions above so Gemini can call them.
# The docstrings matter — Gemini reads them to decide which tool to use.
# =====================================================================

@tool
def tool_find_student_by_student_id(student_id: str) -> dict:
    """
    Look up a single student by their public student_id (e.g., "S101").
    Use this when the user mentions a specific student ID.
    Returns the student's record or None if not found.
    """
    return find_student_by_student_id(student_id)


@tool
def tool_find_students_by_name(name: str) -> list[dict]:
    """
    Search for students whose name contains the given text (case-insensitive).
    Use this when the user mentions a student by name (e.g., "Rajib", "Priya Patel").
    Returns a list of matching students (may be empty).
    """
    return find_students_by_name(name)


@tool
def tool_list_students(limit: int = 20) -> list[dict]:
    """
    List students in the database, up to `limit` results (default 20).
    Use this when the user asks to see "all students" or "list students".
    """
    return list_students(limit)


@tool
def tool_count_students_in_department(department: str) -> int:
    """
    Count how many students are in a given department (e.g., "CSE", "ECE").
    Use this when the user asks "how many students are in <department>".
    Returns an integer count.
    """
    return count_students_in_department(department)


@tool
def tool_find_students_by_cgpa(min_cgpa: float = 0.0, max_cgpa: float = 10.0) -> list[dict]:
    """
    Find students whose CGPA is between min_cgpa and max_cgpa (inclusive).
    Use this when the user asks for students above/below a certain CGPA.
    Example: "students with CGPA above 8" → min_cgpa=8.0, max_cgpa=10.0
    """
    return find_students_by_cgpa(min_cgpa, max_cgpa)


@tool
def tool_semantic_search_students(query: str, k: int = 5) -> list[dict]:
    """
    Search student bios by MEANING, not exact keywords.
    Use this when the user asks about skills, interests, hobbies, or background
    (e.g., "who knows machine learning", "students interested in mobile apps",
    "anyone into robotics", "has backend experience").
    Returns the top matching students with their bios and similarity scores.
    """
    return _semantic_search(query, k=k)


# Convenient list for binding to the LLM
ALL_TOOLS = [
    tool_find_student_by_student_id,
    tool_find_students_by_name,
    tool_list_students,
    tool_count_students_in_department,
    tool_find_students_by_cgpa,
    tool_semantic_search_students,
]