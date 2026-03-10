import joblib
import json
import sqlite3
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"
METADATA_PATH = MODEL_DIR / "metadata.json"
DB_PATH = BASE_DIR / "database" / "students.db"


# --------------------------------------------------
# App Initialization
# --------------------------------------------------
app = FastAPI(title="Academic AI Guard API", version="4.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Load Model By Name
# --------------------------------------------------
def load_model_by_name(model_name: str):

    if not METADATA_PATH.exists():
        raise HTTPException(status_code=500, detail="Model metadata not found")

    with open(METADATA_PATH, "r") as f:
        metadata = json.load(f)

    latest_version = metadata["latest_version"]

    model_path = MODEL_DIR / latest_version / f"{model_name}.pkl"

    if not model_path.exists():
        raise HTTPException(
            status_code=400,
            detail=f"Model '{model_name}' not found in version {latest_version}"
        )

    model = joblib.load(model_path)

    return model, latest_version


# --------------------------------------------------
# Input Schema
# --------------------------------------------------
class StudentInput(BaseModel):

    model: str

    semester: int
    failed_courses: int

    attendance_rate: float
    stress_level: float
    extracurricular_score: float

    internship_completed: int
    family_income_level: int
    part_time_job: int
    scholarship: int
    campus_resident: int


# --------------------------------------------------
# Predict Endpoint
# --------------------------------------------------
@app.post("/predict")
def predict(data: StudentInput):

    model, version = load_model_by_name(data.model.lower())

    input_data = data.model_dump()
    model_used = input_data.pop("model")

    df = pd.DataFrame([input_data])

    # recreate engineered features (same as training)
    df["academic_pressure"] = (
        df["failed_courses"] * 0.5 +
        df["stress_level"] * 0.3 +
        (1 - df["attendance_rate"]) * 2
    )

    df["engagement_score"] = (
        df["extracurricular_score"] * 0.4 +
        df["attendance_rate"] * 5
    )

    try:

        prediction = model.predict(df)[0]

        probs = model.predict_proba(df)[0]

        classes = list(model.classes_)

        if 1 in classes:
            delayed_index = classes.index(1)

        elif "Delayed" in classes:
            delayed_index = classes.index("Delayed")

        else:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected model classes {classes}"
            )

        probability = float(probs[delayed_index])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    probability_percent = probability * 100

    if probability_percent >= 70:
        risk_level = "High"
    elif probability_percent >= 40:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "prediction": "Delayed" if prediction == 1 else "On-Time",
        "probability": round(probability_percent, 2),
        "risk_level": risk_level,
        "model_version": version,
        "model_used": model_used
    }


# --------------------------------------------------
# Model Info Endpoint
# (Logistic baseline + Top 2 performing models)
# --------------------------------------------------
@app.get("/model-info")
def model_info():

    if not METADATA_PATH.exists():
        raise HTTPException(status_code=500, detail="Metadata not found")

    with open(METADATA_PATH, "r") as f:
        metadata = json.load(f)

    if not metadata.get("history"):
        raise HTTPException(status_code=500, detail="No training history found")

    latest_entry = metadata["history"][-1]

    all_models = latest_entry["models"]

    # Always include logistic baseline
    logistic_model = {"logistic": all_models["logistic"]}

    # Rank models by recall_delayed (best for detecting delayed students)
    ranked_models = sorted(
        all_models.items(),
        key=lambda x: x[1]["recall_delayed"],
        reverse=True
    )

    top_models = {}

    for name, metrics in ranked_models:

        if name != "logistic":
            top_models[name] = metrics

        if len(top_models) == 2:
            break

    # Final dashboard models
    dashboard_models = {**logistic_model, **top_models}

    selected_model = max(
        dashboard_models,
        key=lambda m: dashboard_models[m]["accuracy"]
    )

    return {
        "version": latest_entry["version"],
        "selected_model": selected_model,
        "dataset_size": latest_entry["dataset_size"],
        "metrics": dashboard_models
    }


# --------------------------------------------------
# Dashboard Summary
# --------------------------------------------------
@app.get("/summary")
def summary():

    if not DB_PATH.exists():
        raise HTTPException(status_code=500, detail="Database not found")

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query("SELECT * FROM students", conn)

    conn.close()

    total = len(df)

    delayed = int(df["graduation_outcome"].sum())

    on_time = total - delayed

    return {
        "total_students": total,
        "delayed_percentage": round((delayed / total) * 100, 2),
        "on_time_percentage": round((on_time / total) * 100, 2)
    }


# --------------------------------------------------
# Retrain Endpoint
# --------------------------------------------------
@app.post("/retrain")
def retrain():

    try:
        from ml.train import train
        train()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "message": "All models retrained successfully"
    }