"""
SQLAlchemy model for the `students` table.

Each attribute maps to a column in the database.
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, func

from app.database.connection import Base


class Student(Base):
    """Represents a single row in the `students` table."""

    __tablename__ = "students"

    # Primary key: unique internal identifier for each row
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # Public student identifier (e.g., "S101"), must be unique
    student_id = Column(String(20), unique=True, nullable=False, index=True)

    # Full name of the student
    name = Column(String(100), nullable=False)

    # Email — must be unique across all students
    email = Column(String(120), unique=True, nullable=False, index=True)

    # Optional phone number
    phone = Column(String(15), nullable=True)

    # Department (e.g., CSE, ECE, ME)
    department = Column(String(50), nullable=False)

    # Year of study (1-4)
    year = Column(Integer, nullable=False)

    # CGPA (0.0 - 10.0)
    cgpa = Column(Float, nullable=False)

    # Optional address
    address = Column(String(255), nullable=True)

    # Timestamps — handled automatically
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Student id={self.id} student_id={self.student_id!r} name={self.name!r}>"