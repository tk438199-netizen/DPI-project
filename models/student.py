from sqlalchemy import (
    Column, String, Integer, Float,
    ForeignKey, text
)

from database import Base


class Student(Base):
    __tablename__ = "students"

    student_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    semester = Column(Integer, nullable=False)


class AcademicRecord(Base):
    __tablename__ = "academic_records"

    record_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(
        String,
        ForeignKey("students.student_id"),
        nullable=False
    )

    study_hours = Column(Float)
    attendance = Column(Float)
    previous_marks = Column(Float)
    assignment_marks = Column(Float)
    class_test_marks = Column(Float)
    final_marks = Column(Float)


class Prediction(Base):
    __tablename__ = "predictions"

    prediction_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(
        String,
        ForeignKey("students.student_id"),
        nullable=False
    )

    predicted_marks = Column(Float)

    created_at = Column(
        String,
        server_default=text("CURRENT_TIMESTAMP")
    )