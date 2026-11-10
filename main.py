from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import engine, Base, get_db

from models.student import (
    Student,
    AcademicRecord,
    Prediction
)

from schemas.student import (
    StudentCreate,
    StudentUpdate,
    StudentOut,
    AcademicRecordCreate,
    AcademicRecordOut,
    PredictionOut
)

from ml.predictor import predict_marks


# Create tables if they do not exist
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Student Management & Result Prediction API",
    description="Student management with ML-based result prediction",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Student Management API is running!"
    }


# -------------------------
# STUDENT APIs
# -------------------------

@app.post("/students/", response_model=StudentOut)
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):

    existing = db.query(Student).filter(
        Student.student_id == student.student_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Student already exists"
        )

    new_student = Student(**student.model_dump())

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return new_student


@app.get("/students/", response_model=list[StudentOut])
def get_students(db: Session = Depends(get_db)):

    return db.query(Student).all()


@app.get("/students/{student_id}", response_model=StudentOut)
def get_student(
    student_id: str,
    db: Session = Depends(get_db)
):

    student = db.query(Student).filter(
        Student.student_id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return student


@app.put("/students/{student_id}", response_model=StudentOut)
def update_student(
    student_id: str,
    student_data: StudentUpdate,
    db: Session = Depends(get_db)
):

    student = db.query(Student).filter(
        Student.student_id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    updates = student_data.model_dump(exclude_unset=True)

    for key, value in updates.items():
        setattr(student, key, value)

    db.commit()
    db.refresh(student)

    return student


@app.delete("/students/{student_id}")
def delete_student(
    student_id: str,
    db: Session = Depends(get_db)
):

    student = db.query(Student).filter(
        Student.student_id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    has_records = db.query(AcademicRecord).filter(
        AcademicRecord.student_id == student_id
    ).first()

    has_predictions = db.query(Prediction).filter(
        Prediction.student_id == student_id
    ).first()

    if has_records or has_predictions:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete student with existing records or predictions"
        )

    db.delete(student)
    db.commit()

    return {"message": "Student deleted successfully"}


# -------------------------
# ACADEMIC RECORD APIs
# -------------------------

@app.post("/records/", response_model=AcademicRecordOut)
def create_record(
    record: AcademicRecordCreate,
    db: Session = Depends(get_db)
):

    student = db.query(Student).filter(
        Student.student_id == record.student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    new_record = AcademicRecord(**record.model_dump())

    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return new_record


@app.get("/records/{student_id}", response_model=list[AcademicRecordOut])
def get_student_records(
    student_id: str,
    db: Session = Depends(get_db)
):

    return db.query(AcademicRecord).filter(
        AcademicRecord.student_id == student_id
    ).all()


# -------------------------
# ML PREDICTION API
# -------------------------

@app.post("/predict/{student_id}")
def predict_student_result(
    student_id: str,
    db: Session = Depends(get_db)
):

    student = db.query(Student).filter(
        Student.student_id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    record = db.query(AcademicRecord).filter(
        AcademicRecord.student_id == student_id
    ).order_by(
        AcademicRecord.record_id.desc()
    ).first()

    if not record:
        raise HTTPException(
            status_code=404,
            detail="Academic record not found"
        )

    try:
        predicted_marks = predict_marks(student, record)
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(error)}"
        )

    prediction = Prediction(
        student_id=student_id,
        predicted_marks=predicted_marks
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return {
        "student_id": student_id,
        "predicted_marks": predicted_marks,
        "message": "Prediction completed and saved!"
    }


# -------------------------
# PREDICTION HISTORY API
# -------------------------

@app.get("/predictions/", response_model=list[PredictionOut])
def get_predictions(db: Session = Depends(get_db)):

    return db.query(Prediction).order_by(
        Prediction.prediction_id.desc()
    ).all()


# -------------------------
# ANALYTICS API
# -------------------------

@app.get("/analytics/")
def get_analytics(db: Session = Depends(get_db)):

    total_students = db.query(Student).count()

    total_records = db.query(AcademicRecord).count()

    total_predictions = db.query(Prediction).count()

    average_marks = db.query(
        func.avg(AcademicRecord.final_marks)
    ).scalar()

    return {
        "total_students": total_students,
        "total_academic_records": total_records,
        "total_predictions": total_predictions,
        "average_final_marks": round(average_marks, 2)
        if average_marks is not None else None
    }