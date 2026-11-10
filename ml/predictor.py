import joblib
import pandas as pd

from pathlib import Path


MODEL_PATH = (
    Path(__file__).resolve().parents[1]
    / "student_model.joblib"
)

model = joblib.load(MODEL_PATH)


MODEL_FEATURES = [
    "semester",
    "study_hours",
    "attendance",
    "previous_marks",
    "assignment_marks",
    "class_test_marks",
    "department_CST",
    "department_Civil",
    "department_Computer",
    "department_Electrical",
    "department_Mechanical"
]


def predict_marks(student, record):

    data = {
        "semester": student.semester,
        "study_hours": record.study_hours,
        "attendance": record.attendance,
        "previous_marks": record.previous_marks,
        "assignment_marks": record.assignment_marks,
        "class_test_marks": record.class_test_marks
    }

    departments = [
        "CST",
        "Civil",
        "Computer",
        "Electrical",
        "Mechanical"
    ]

    for department in departments:
        data[f"department_{department}"] = int(
            student.department == department
        )

    input_df = pd.DataFrame(
        [data],
        columns=MODEL_FEATURES
    )

    prediction = model.predict(input_df)[0]

    return round(float(prediction), 2)