import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

DB_PATH = "students.db"


def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM students", conn)
    conn.close()
    return df


def prepare_data(df):
    feature_cols = [
        "pep_credits",
        "humanities_credits",
        "sip_credits",
        "short_iip_credits",
        "long_iip_credits",
        "effective_execution_credits",
        "total_credits",
        "year_of_study",
    ]

    X = df[feature_cols]
    y = df["degree_eligible"]

    return train_test_split(X, y, test_size=0.25, random_state=42)


def evaluate_model(model, X_test, y_test, model_name):
    preds = model.predict(X_test)

    print(f"\n===== {model_name} Evaluation =====")
    print("Accuracy:", accuracy_score(y_test, preds))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, preds))
    print("\nClassification Report:")
    print(classification_report(y_test, preds, zero_division=0))


def main():
    df = load_data()
    X_train, X_test, y_train, y_test = prepare_data(df)

    print("\nClass distribution in test data:")
    print(y_test.value_counts())

    dt = DecisionTreeClassifier(random_state=42)
    rf = RandomForestClassifier(n_estimators=100, random_state=42)

    dt.fit(X_train, y_train)
    rf.fit(X_train, y_train)

    evaluate_model(dt, X_test, y_test, "Decision Tree")
    evaluate_model(rf, X_test, y_test, "Random Forest")


if __name__ == "__main__":
    main()
