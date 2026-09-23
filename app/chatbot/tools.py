"""
Tools the chatbot can use to access student data.

Phase 6: These are placeholder stubs — they return fake data so the graph works.
Phase 7: We'll connect them to the real database via the student_service layer.
"""
from app.database.connection import SessionLocal
from app.services import student_service


def find_student_by_student_id(student_id: str) -> dict | None:
    """
    Look up a student by their public student_id (e.g., "S101").

    Returns a dict of student details, or None if not found.
    """
    db = SessionLocal()
    try:
        student = student_service.get_student_by_student_id(db, student_id)
        if student is None:
            return None
        return _student_to_dict(student)
    finally:
        db.close()


def list_students(limit: int = 20) -> list[dict]:
    """Return a list of students (up to `limit`)."""
    db = SessionLocal()
    try:
        students = student_service.get_students(db, skip=0, limit=limit)
        return [_student_to_dict(s) for s in students]
    finally:
        db.close()


def count_students_in_department(department: str) -> int:
    """Return the number of students in a given department."""
    db = SessionLocal()
    try:
        students = student_service.get_students(db, skip=0, limit=1000)
        return sum(1 for s in students if s.department.lower() == department.lower())
    finally:
        db.close()


def _student_to_dict(student) -> dict:
    """Convert a Student ORM object to a plain dict (safe to pass to Gemini)."""
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