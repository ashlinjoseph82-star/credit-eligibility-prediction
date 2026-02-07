import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

from src.db_connection import load_student_data


def prepare_data():
    df = load_student_data()

    X = df.drop(columns=[
        "student_id",
        "degree_eligible",
        "graduation_risk"
    ])

    y = df["degree_eligible"]

    X = pd.get_dummies(X, drop_first=True)

    return train_test_split(X, y, test_size=0.2, random_state=42)


def train_models():
    X_train, X_test, y_train, y_test = prepare_data()

    print("Class distribution in training data:")
    print(y_train.value_counts())

    models = {
        "Decision Tree": DecisionTreeClassifier(),
        "Random Forest": RandomForestClassifier()
    }

    # Train Logistic Regression ONLY if both classes exist
    if y_train.nunique() > 1:
        models["Logistic Regression"] = LogisticRegression(max_iter=1000)
    else:
        print("Skipping Logistic Regression (only one class in training data)")

    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        print(f"{name} Accuracy: {acc:.2f}")


if __name__ == "__main__":
    train_models()
