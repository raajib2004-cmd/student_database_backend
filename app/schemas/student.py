"""
Pydantic schemas for Student.

- StudentBase: common fields shared by create/update
- StudentCreate: data required to create a new student
- StudentUpdate: all fields optional (for partial updates)
- StudentResponse: what we return to the client (adds id, timestamps)
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class StudentBase(BaseModel):
    """Common fields shared across schemas."""

    student_id: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Public student identifier, e.g., S101",
        examples=["S101"],
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Full name of the student",
        examples=["Rajib Das"],
    )
    email: EmailStr = Field(
        ...,
        description="Unique email address",
        examples=["rajib@example.com"],
    )
    phone: str | None = Field(
        default=None,
        max_length=15,
        description="Optional phone number",
        examples=["9876543210"],
    )
    department: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Department, e.g., CSE, ECE, ME",
        examples=["CSE"],
    )
    year: int = Field(
        ...,
        ge=1,
        le=4,
        description="Year of study (1-4)",
        examples=[3],
    )
    cgpa: float = Field(
        ...,
        ge=0.0,
        le=10.0,
        description="CGPA between 0.0 and 10.0",
        examples=[8.5],
    )
    address: str | None = Field(
        default=None,
        max_length=255,
        description="Optional address",
        examples=["Guwahati, Assam"],
    )


class StudentCreate(StudentBase):
    """Schema for creating a new student (POST /students)."""
    pass


class StudentUpdate(BaseModel):
    """
    Schema for updating a student (PUT /students/{id}).
    All fields optional so you can send only what changes.
    """

    name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=15)
    department: str | None = Field(default=None, min_length=1, max_length=50)
    year: int | None = Field(default=None, ge=1, le=4)
    cgpa: float | None = Field(default=None, ge=0.0, le=10.0)
    address: str | None = Field(default=None, max_length=255)


class StudentResponse(StudentBase):
    """
    Schema for returning student data in API responses.
    Adds the DB-managed fields: id, created_at, updated_at.
    """

    id: int
    created_at: datetime
    updated_at: datetime

    # Enable reading attributes from ORM objects (SQLAlchemy models)
    model_config = ConfigDict(from_attributes=True)