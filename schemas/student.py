from pydantic import BaseModel, ConfigDict
from typing import Optional


class StudentCreate(BaseModel):
    student_id: str
    name: str
    department: str
    semester: int


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    semester: Optional[int] = None


class StudentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: str
    name: str
    department: str
    semester: int


class AcademicRecordCreate(BaseModel):
    student_id: str
    study_hours: float
    attendance: float
    previous_marks: float
    assignment_marks: float
    class_test_marks: float
    final_marks: float


class AcademicRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    record_id: int
    student_id: str
    study_hours: float
    attendance: float
    previous_marks: float
    assignment_marks: float
    class_test_marks: float
    final_marks: float


class PredictionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    prediction_id: int
    student_id: str
    predicted_marks: float
    created_at: Optional[str] = None