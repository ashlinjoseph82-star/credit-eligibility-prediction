import sqlite3
import pandas as pd

DB_PATH = "students.db"

def load_student_data():
    """
    Load student data from SQLite database into a pandas DataFrame
    """
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM students"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
