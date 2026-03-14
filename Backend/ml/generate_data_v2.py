import sqlite3
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Database paths
DB_PATH = BASE_DIR / "database" / "students_v2.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"

TOTAL_STUDENTS = 12000
TOTAL_REQUIRED_CREDITS = 160

# Degree structures (terms)
DEGREE_OPTIONS = [12, 16, 20]  # 3 yr, 4 yr, 5 yr


def create_database():
    if DB_PATH.exists():
        print("students_v2.db already exists. Delete it to regenerate.")
        return False

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(SCHEMA_PATH, "r") as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()

    return True


def generate_student():

    # Choose program type
    degree_terms = random.choice(DEGREE_OPTIONS)

    # Current term of student
    term = random.randint(1, degree_terms)

    # Academic credits
    core_credits = random.randint(20, 130)
    pep_credits = random.randint(3, 18)
    humanities_credits = random.randint(3, 18)

    internship_completed = random.choices([0, 1], weights=[0.4, 0.6])[0]
    failed_courses = random.randint(0, 7)

    attendance_rate = round(random.uniform(0.45, 0.98), 2)

    family_income_level = random.choice([1, 2, 3])
    part_time_job = random.choice([0, 1])

    extracurricular_score = random.randint(0, 12)

    # Stress distribution
    stress_level = random.choices(
        [1,2,3,4,5,6,7,8,9,10],
        weights=[2,3,5,7,9,9,7,5,3,2]
    )[0]

    scholarship = random.choice([0, 1])
    campus_resident = random.choice([0, 1])

    # Calculate credits
    total_credits = core_credits + pep_credits + humanities_credits

    if internship_completed:
        total_credits += 10

    # Expected credits based on progression
    expected_credits = int((TOTAL_REQUIRED_CREDITS / degree_terms) * term)

    deviation = total_credits - expected_credits

    # ---------------------------
    # RISK MODEL
    # ---------------------------

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

    if extracurricular_score < 2 and attendance_rate < 0.7:
        risk_score += 1

    if part_time_job and attendance_rate < 0.7:
        risk_score += 1

    # Internship expected near end
    if internship_completed == 0 and term >= degree_terms - 2:
        risk_score += 1

    if scholarship == 1 and failed_courses == 0:
        risk_score -= 1

    # Add randomness
    risk_score += random.uniform(-1.5, 1.5)

    delay_probability = min(max(risk_score * 0.12, 0.05), 0.85)

    delayed = 1 if random.random() < delay_probability else 0

    # Label noise
    if random.random() < 0.05:
        delayed = 1 - delayed

    return (
        term,
        core_credits,
        pep_credits,
        humanities_credits,
        internship_completed,
        failed_courses,
        total_credits,
        expected_credits,
        deviation,
        attendance_rate,
        extracurricular_score,
        family_income_level,
        part_time_job,
        scholarship,
        campus_resident,
        stress_level,
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
                term,
                core_credits,
                pep_credits,
                humanities_credits,
                internship_completed,
                failed_courses,
                total_credits,
                expected_credits,
                deviation,
                attendance_rate,
                extracurricular_score,
                family_income_level,
                part_time_job,
                scholarship,
                campus_resident,
                stress_level,
                graduation_outcome
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            student,
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":

    print("Creating v2 database...")

    created = create_database()

    if not created:
        exit()

    print("Generating diverse synthetic student dataset...")

    populate_database()

    print(f"Done. {TOTAL_STUDENTS} students inserted into students_v2.db")
