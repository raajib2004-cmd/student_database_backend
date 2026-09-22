"""
Business logic for student CRUD operations.

Routes call these functions. Functions raise custom exceptions for
error conditions, which routes translate into HTTP responses.
"""
from sqlalchemy.orm import Session

from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate


# ---------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------
class DuplicateStudentError(Exception):
    """Raised when a student_id or email already exists in the database."""

    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value
        super().__init__(f"A student with {field}={value!r} already exists.")


class StudentNotFoundError(Exception):
    """Raised when a student lookup finds nothing."""

    def __init__(self, identifier):
        self.identifier = identifier
        super().__init__(f"Student {identifier!r} not found.")


# ---------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------
def create_student(db: Session, data: StudentCreate) -> Student:
    """
    Insert a new student.
    Raises DuplicateStudentError if student_id or email is already taken.
    """
    # Check for duplicates BEFORE inserting — gives a clean error message.
    existing_sid = (
        db.query(Student).filter(Student.student_id == data.student_id).first()
    )
    if existing_sid:
        raise DuplicateStudentError("student_id", data.student_id)

    existing_email = (
        db.query(Student).filter(Student.email == data.email).first()
    )
    if existing_email:
        raise DuplicateStudentError("email", data.email)

    # Build the model from the Pydantic schema
    student = Student(**data.model_dump())

    db.add(student)
    db.commit()
    db.refresh(student)  # reload so student.id, created_at, etc. are populated
    return student


# ---------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------
def get_students(db: Session, skip: int = 0, limit: int = 100) -> list[Student]:
    """Return a paginated list of students."""
    return db.query(Student).offset(skip).limit(limit).all()


def get_student_by_id(db: Session, student_pk: int) -> Student | None:
    """Fetch a student by the primary key (internal id)."""
    return db.query(Student).filter(Student.id == student_pk).first()


def get_student_by_student_id(db: Session, student_id: str) -> Student | None:
    """Fetch a student by the public student_id (e.g., S101)."""
    return db.query(Student).filter(Student.student_id == student_id).first()


# ---------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------
def update_student(
    db: Session, student_pk: int, data: StudentUpdate
) -> Student | None:
    """
    Update a student's fields.
    Only fields that are set in `data` (i.e., not None) are changed.
    Returns the updated student, or None if not found.
    Raises DuplicateStudentError if the new email belongs to another student.
    """
    student = get_student_by_id(db, student_pk)
    if student is None:
        return None

    # exclude_unset=True means "only include fields the client explicitly provided"
    update_data = data.model_dump(exclude_unset=True)

    # If email is being changed, make sure it's not taken by someone else
    if "email" in update_data and update_data["email"] != student.email:
        other = (
            db.query(Student)
            .filter(Student.email == update_data["email"], Student.id != student_pk)
            .first()
        )
        if other:
            raise DuplicateStudentError("email", update_data["email"])

    # Apply the changes
    for field, value in update_data.items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)
    return student


# ---------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------
def delete_student(db: Session, student_pk: int) -> bool:
    """Delete a student. Returns True if deleted, False if not found."""
    student = get_student_by_id(db, student_pk)
    if student is None:
        return False

    db.delete(student)
    db.commit()
    return True