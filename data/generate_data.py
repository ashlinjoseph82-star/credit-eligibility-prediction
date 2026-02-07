import random
import sqlite3

# -----------------------------
# DEGREE CONFIGURATION
# -----------------------------
DEGREES = {
    "BTECH_AI": {"years": 4, "total_credits": 160},
    "TSM": {"years": 4, "total_credits": 160},
    "BBA": {"years": 3, "total_credits": 120},
    "BBA_LLB": {"years": 5, "total_credits": 200},
}

CREDIT_REQUIREMENTS = {
    "pep": 12,
    "humanities": 8,
    "sip": 3,
    "short_iip": 2,
    "long_iip": 10,
}

DB_PATH = "students.db"


# -----------------------------
# DATABASE SETUP
# -----------------------------
def create_table():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            degree_program TEXT,
            year_of_study INTEGER,

            pep_credits INTEGER,
            humanities_credits INTEGER,
            sip_credits INTEGER,
            short_iip_credits INTEGER,
            long_iip_credits INTEGER,
            effective_execution_credits INTEGER,

            total_credits INTEGER,
            degree_eligible INTEGER,
            graduation_risk TEXT
        )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# BUSINESS LOGIC
# -----------------------------
def calculate_eligibility(total, category_credits, required_total):
    if total < required_total:
        return 0

    for key, min_val in CREDIT_REQUIREMENTS.items():
        if category_credits[key] < min_val:
            return 0

    return 1


def calculate_risk(total, required_total, eligible):
    if eligible == 1:
        return "Low"

    progress = total / required_total

    if progress >= 0.7:
        return "Medium"
    return "High"


# -----------------------------
# DATA GENERATION
# -----------------------------
def generate_student():
    degree = random.choice(list(DEGREES.keys()))
    degree_info = DEGREES[degree]

    year = random.randint(1, degree_info["years"])

    pep = random.randint(0, 15)
    humanities = random.randint(0, 12)
    sip = random.randint(0, 5)
    short_iip = random.randint(0, 4)
    long_iip = random.randint(0, 12)
    effective_execution = random.randint(0, 6)

    total = (
        pep
        + humanities
        + sip
        + short_iip
        + long_iip
        + effective_execution
        + random.randint(20, 60)
    )

    category_credits = {
        "pep": pep,
        "humanities": humanities,
        "sip": sip,
        "short_iip": short_iip,
        "long_iip": long_iip,
    }

    eligible = calculate_eligibility(
        total, category_credits, degree_info["total_credits"]
    )

    risk = calculate_risk(total, degree_info["total_credits"], eligible)

    return (
        degree,
        year,
        pep,
        humanities,
        sip,
        short_iip,
        long_iip,
        effective_execution,
        total,
        eligible,
        risk,
    )


def insert_students(n=500):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for _ in range(n):
        cur.execute("""
            INSERT INTO students (
                degree_program,
                year_of_study,
                pep_credits,
                humanities_credits,
                sip_credits,
                short_iip_credits,
                long_iip_credits,
                effective_execution_credits,
                total_credits,
                degree_eligible,
                graduation_risk
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, generate_student())

    conn.commit()
    conn.close()


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    create_table()
    insert_students(800)
    print("Synthetic student data generated successfully.")
