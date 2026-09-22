"""
HTTP routes for student CRUD.

These are thin wrappers around app.services.student_service.
They handle HTTP concerns (status codes, request/response shapes),
and let the service layer handle business logic.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.student import StudentCreate, StudentResponse, StudentUpdate
from app.services import student_service
from app.services.student_service import (
    DuplicateStudentError,
    StudentNotFoundError,
)

router = APIRouter(
    prefix="/students",
    tags=["Students"],
)


# Common error response examples shown in Swagger
ERROR_404_EXAMPLE = {"detail": "Student with id=42 not found."}
ERROR_409_EXAMPLE = {"detail": "A student with student_id='S101' already exists."}


# ---------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------
@router.post(
    "",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student",
    description=(
        "Create a new student record.\n\n"
        "- `student_id` must be unique\n"
        "- `email` must be unique and valid\n"
        "- `year` must be between 1 and 4\n"
        "- `cgpa` must be between 0.0 and 10.0"
    ),
    responses={
        409: {
            "description": "Duplicate student_id or email",
            "content": {"application/json": {"example": ERROR_409_EXAMPLE}},
        },
    },
)
def create_student(
    payload: StudentCreate,
    db: Session = Depends(get_db),
):
    """Create a new student record."""
    try:
        student = student_service.create_student(db, payload)
    except DuplicateStudentError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    return student


# ---------------------------------------------------------------------
# READ ALL
# ---------------------------------------------------------------------
@router.get(
    "",
    response_model=list[StudentResponse],
    summary="List all students",
    description="Return a paginated list of students, sorted by internal id.",
)
def list_students(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Max records to return"),
    db: Session = Depends(get_db),
):
    """Return a paginated list of students."""
    return student_service.get_students(db, skip=skip, limit=limit)


# ---------------------------------------------------------------------
# READ ONE
# ---------------------------------------------------------------------
@router.get(
    "/{student_pk}",
    response_model=StudentResponse,
    summary="Get a single student by internal id",
    description="Fetch a student by their internal integer `id` (not `student_id`).",
    responses={
        404: {
            "description": "Student not found",
            "content": {"application/json": {"example": ERROR_404_EXAMPLE}},
        },
    },
)
def get_student(
    student_pk: int,
    db: Session = Depends(get_db),
):
    """Fetch a student by the internal primary key (integer id)."""
    student = student_service.get_student_by_id(db, student_pk)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id={student_pk} not found.",
        )
    return student


# ---------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------
@router.put(
    "/{student_pk}",
    response_model=StudentResponse,
    summary="Update an existing student",
    description=(
        "Update fields on a student. Only fields included in the request body are changed.\n\n"
        "- If `email` is changed, it must be unique.\n"
        "- Returns 404 if the student doesn't exist.\n"
        "- Returns 409 if the new email is already used by another student."
    ),
    responses={
        404: {
            "description": "Student not found",
            "content": {"application/json": {"example": ERROR_404_EXAMPLE}},
        },
        409: {
            "description": "Duplicate email",
            "content": {"application/json": {"example": ERROR_409_EXAMPLE}},
        },
    },
)
def update_student(
    student_pk: int,
    payload: StudentUpdate,
    db: Session = Depends(get_db),
):
    """Update a student by internal id."""
    try:
        student = student_service.update_student(db, student_pk, payload)
    except DuplicateStudentError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id={student_pk} not found.",
        )
    return student


# ---------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------
@router.delete(
    "/{student_pk}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a student",
    description="Delete a student by internal id. Returns 204 on success, 404 if not found.",
    responses={
        404: {
            "description": "Student not found",
            "content": {"application/json": {"example": ERROR_404_EXAMPLE}},
        },
    },
)
def delete_student(
    student_pk: int,
    db: Session = Depends(get_db),
):
    """Delete a student by internal id."""
    deleted = student_service.delete_student(db, student_pk)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id={student_pk} not found.",
        )
    return None