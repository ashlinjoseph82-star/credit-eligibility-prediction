import sqlite3
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "students.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"

TOTAL_STUDENTS = 10000
TOTAL_TERMS = 8
TOTAL_REQUIRED_CREDITS = 160


def create_database():
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(SCHEMA_PATH, "r") as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()


def generate_student():
    semester = random.randint(4, 10)

    core_credits = random.randint(50, 120)
    pep_credits = random.randint(5, 15)
    humanities_credits = random.randint(5, 15)

    internship_completed = random.choices([0, 1], weights=[0.45, 0.55])[0]
    failed_courses = random.randint(0, 5)

    attendance_rate = round(random.uniform(0.55, 0.98), 2)
    family_income_level = random.choice([1, 2, 3])  # 1=low,2=mid,3=high
    part_time_job = random.choice([0, 1])
    extracurricular_score = random.randint(0, 10)
    stress_level = random.randint(1, 10)
    scholarship = random.choice([0, 1])
    campus_resident = random.choice([0, 1])

    total_credits = core_credits + pep_credits + humanities_credits
    if internship_completed:
        total_credits += 10

    expected_credits = int((TOTAL_REQUIRED_CREDITS / TOTAL_TERMS) * semester)
    deviation = total_credits - expected_credits

    # ----------------------------------------
    # NONLINEAR RISK MODEL
    # ----------------------------------------
    risk_score = 0

    if failed_courses >= 3:
        risk_score += 2

    if attendance_rate < 0.65:
        risk_score += 2
    elif attendance_rate < 0.75:
        risk_score += 1

    if deviation < -25:
        risk_score += 2
    elif deviation < -10:
        risk_score += 1

    if stress_level > 7:
        risk_score += 1

    if part_time_job and attendance_rate < 0.7:
        risk_score += 1

    if internship_completed == 0 and semester >= 8:
        risk_score += 1

    if scholarship == 1 and failed_courses == 0:
        risk_score -= 1

    # Add controlled randomness
    risk_score += random.uniform(-1.5, 1.5)

    # Convert to probability
    delay_probability = min(max(risk_score * 0.12, 0.05), 0.85)

    delayed = 1 if random.random() < delay_probability else 0

    # Add 5% random label noise
    if random.random() < 0.05:
        delayed = 1 - delayed

    return (
        semester,
        core_credits,
        pep_credits,
        humanities_credits,
        internship_completed,
        failed_courses,
        total_credits,
        expected_credits,
        deviation,
        attendance_rate,
        family_income_level,
        part_time_job,
        extracurricular_score,
        stress_level,
        scholarship,
        campus_resident,
        delayed,
    )


def populate_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for _ in range(TOTAL_STUDENTS):
        student = generate_student()
        cursor.execute(
            """
            INSERT INTO students (
                semester,
                core_credits,
                pep_credits,
                humanities_credits,
                internship_completed,
                failed_courses,
                total_credits,
                expected_credits,
                deviation,
                attendance_rate,
                family_income_level,
                part_time_job,
                extracurricular_score,
                stress_level,
                scholarship,
                campus_resident,
                graduation_outcome
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            student,
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    print("Creating database...")
    create_database()

    print("Generating realistic synthetic student data...")
    populate_database()

    print(f"Done. {TOTAL_STUDENTS} students inserted.")