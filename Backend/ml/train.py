import sqlite3
import pandas as pd
import joblib
import json
from pathlib import Path
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, recall_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    ExtraTreesClassifier
)

from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "students.db"
MODEL_DIR = BASE_DIR / "models"
METADATA_PATH = MODEL_DIR / "metadata.json"

MODEL_DIR.mkdir(exist_ok=True)


def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()
    return df


def get_next_version(existing_metadata):
    if not existing_metadata:
        return "v1"
    latest = existing_metadata["latest_version"]
    number = int(latest.replace("v", ""))
    return f"v{number + 1}"


def train():
    print("Loading data...")
    df = load_data()
    df = df.dropna()

    # ---------------------------
    # Feature Engineering
    # ---------------------------
    df["academic_pressure"] = (
        df["failed_courses"] * 0.5 +
        df["stress_level"] * 0.3 +
        (1 - df["attendance_rate"]) * 2
    )

    df["engagement_score"] = (
        df["extracurricular_score"] * 0.4 +
        df["attendance_rate"] * 5
    )

    numeric_features = [
        "semester",
        "failed_courses",
        "attendance_rate",
        "stress_level",
        "extracurricular_score",
        "academic_pressure",
        "engagement_score"
    ]

    categorical_features = [
        "internship_completed",
        "family_income_level",
        "part_time_job",
        "scholarship",
        "campus_resident"
    ]

    X = df[numeric_features + categorical_features]
    y = df["graduation_outcome"]

    class_counts = y.value_counts()
    scale_pos_weight = class_counts[0] / class_counts[1] if len(class_counts) > 1 else 1

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # ---------------------------
    # Preprocessing
    # ---------------------------
    numeric_scaled = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    numeric_unscaled = Pipeline([
        ("imputer", SimpleImputer(strategy="median"))
    ])

    categorical_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ])

    preprocessor_scaled = ColumnTransformer([
        ("num", numeric_scaled, numeric_features),
        ("cat", categorical_transformer, categorical_features)
    ])

    preprocessor_unscaled = ColumnTransformer([
        ("num", numeric_unscaled, numeric_features),
        ("cat", categorical_transformer, categorical_features)
    ])

    # ---------------------------
    # 8 MODELS
    # ---------------------------
    models = {

        "logistic": Pipeline([
            ("preprocessor", preprocessor_scaled),
            ("classifier", LogisticRegression(
                max_iter=3000,
                class_weight="balanced"
            ))
        ]),

        "decision_tree": Pipeline([
            ("preprocessor", preprocessor_unscaled),
            ("classifier", DecisionTreeClassifier(
                max_depth=6,
                min_samples_split=20,
                min_samples_leaf=10,
                class_weight="balanced",
                random_state=42
            ))
        ]),

        "random_forest": Pipeline([
            ("preprocessor", preprocessor_unscaled),
            ("classifier", RandomForestClassifier(
                n_estimators=400,
                max_depth=8,
                min_samples_split=15,
                min_samples_leaf=8,
                class_weight="balanced",
                random_state=42
            ))
        ]),

        "extra_trees": Pipeline([
            ("preprocessor", preprocessor_unscaled),
            ("classifier", ExtraTreesClassifier(
                n_estimators=400,
                max_depth=8,
                min_samples_split=15,
                min_samples_leaf=8,
                class_weight="balanced",
                random_state=42
            ))
        ]),

        "gradient_boosting": Pipeline([
            ("preprocessor", preprocessor_unscaled),
            ("classifier", GradientBoostingClassifier(
                n_estimators=400,
                learning_rate=0.03,
                max_depth=3,
                random_state=42
            ))
        ]),

        "xgboost": Pipeline([
            ("preprocessor", preprocessor_unscaled),
            ("classifier", XGBClassifier(
                n_estimators=500,
                learning_rate=0.03,
                max_depth=4,
                subsample=0.8,
                colsample_bytree=0.8,
                reg_alpha=0.7,
                reg_lambda=1.5,
                scale_pos_weight=scale_pos_weight,
                eval_metric="logloss",
                random_state=42
            ))
        ]),

        "lightgbm": Pipeline([
            ("preprocessor", preprocessor_unscaled),
            ("classifier", LGBMClassifier(
                n_estimators=500,
                learning_rate=0.03,
                max_depth=-1,
                random_state=42
            ))
        ]),

        "catboost": Pipeline([
            ("preprocessor", preprocessor_unscaled),
            ("classifier", CatBoostClassifier(
                iterations=500,
                learning_rate=0.03,
                depth=6,
                verbose=0,
                random_state=42
            ))
        ])
    }

    # ---------------------------
    # Versioning
    # ---------------------------
    if METADATA_PATH.exists():
        with open(METADATA_PATH, "r") as f:
            metadata = json.load(f)
    else:
        metadata = None

    version = get_next_version(metadata)
    version_dir = MODEL_DIR / version
    version_dir.mkdir(exist_ok=True)

    print("\nTraining 8 models...\n")

    results = {}

    for name, model in models.items():

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="weighted")
        recall_delayed = recall_score(y_test, y_pred, pos_label=1)

        probs = model.predict_proba(X_test)[:, 1]
        roc = roc_auc_score(y_test, probs)

        print(f"{name.upper()} → Recall:{recall_delayed:.4f}  ROC:{roc:.4f}")

        joblib.dump(model, version_dir / f"{name}.pkl")

        results[name] = {
            "accuracy": round(acc, 4),
            "f1": round(f1, 4),
            "roc_auc": round(roc, 4),
            "recall_delayed": round(recall_delayed, 4)
        }

    # ---------------------------
    # Select Best 3 (Recall Priority)
    # ---------------------------
    sorted_models = sorted(
        results.items(),
        key=lambda x: x[1]["recall_delayed"],
        reverse=True
    )

    top_two = [sorted_models[0][0], sorted_models[1][0]]
    production_models = ["logistic"] + top_two
    production_models = list(set(production_models))

    print("\nProduction Models Selected:")
    print(production_models)

    new_entry = {
        "version": version,
        "models": results,
        "production_models": production_models,
        "trained_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dataset_size": len(df),
    }

    if metadata:
        metadata["latest_version"] = version
        metadata["history"].append(new_entry)
    else:
        metadata = {
            "latest_version": version,
            "history": [new_entry]
        }

    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=4)

    print(f"\nAll models saved under version {version}")


if __name__ == "__main__":
    train()