import sqlite3
from datetime import datetime, timedelta
import bcrypt
from student_hub.util_classes import LoginData, Lecture, Exam
from typing import List, Dict

DB_NAME = "studenthub.db"

def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_db(connection_provider=get_connection):
    """
    Initializes the database with the required tables to store user profiles with their grades, and timetables.
    """
    with connection_provider() as conn:
        c = conn.cursor()

        # Profiles table
        c.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            firstname TEXT NOT NULL,
            lastname TEXT NOT NULL,
            email TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            study_group_id TEXT NOT NULL,
            study_group TEXT NOT NULL,
            average_grade TEXT NOT NULL,
            total_credits TEXT NOT NULL      
        )
        """)

        # Modules table (stores alle modules with grades and credits for each student)
        c.execute("""
        CREATE TABLE IF NOT EXISTS modules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module TEXT NOT NULL,
            grade TEXT NOT NULL,
            credits REAL NOT NULL,
            email TEXT NOT NULL,
            FOREIGN KEY (email) REFERENCES profiles(email)
        )
        """)

        # Lectures table - shared courses (one lecture can be attended by more than one student), referenced by profiles in link table
        c.execute("""
        CREATE TABLE IF NOT EXISTS lectures (
            title TEXT NOT NULL,
            room TEXT NOT NULL,
            format TEXT NOT NULL,
            weekday TEXT NOT NULL,
            time TEXT NOT NULL,
            PRIMARY KEY (room, weekday, time)
        )
        """)

        # Link table: which profiles are assigned to which lectures -> which students are attending which courses
        c.execute("""
        CREATE TABLE IF NOT EXISTS profile_lecture (
            email TEXT NOT NULL,
            room TEXT NOT NULL,
            time TEXT NOT NULL,
            weekday TEXT NOT NULL,
            FOREIGN KEY (email) REFERENCES profile(email),
            FOREIGN KEY (room, time, weekday) REFERENCES lectures(room, time, weekday)
            PRIMARY KEY (email, room, time, weekday)
        )
        """)

        # Exams table - shared exams (one exam can be attended by more than one student), referenced by profiles in link table
        c.execute("""
        CREATE TABLE IF NOT EXISTS exams (
            exam_name TEXT NOT NULL,
            study_groups TEXT NOT NULL,
            examiner TEXT NOT NULL,
            exam_date TEXT NOT NULL,
            PRIMARY KEY (examiner, exam_date)
        )
        """)

        # Link table: which profiles are assigned to which exams -> which students are writing which exams
        c.execute("""
        CREATE TABLE IF NOT EXISTS profile_exam (
            email TEXT NOT NULL,
            examiner TEXT NOT NULL,
            exam_date TEXT NOT NULL,
            FOREIGN KEY (email) REFERENCES profile(email),
            FOREIGN KEY (examiner, exam_date) REFERENCES exams(examiner, exam_date)
            PRIMARY KEY (email, examiner, exam_date)
        )
        """)

        conn.commit()


# Insert profile (Create Account)
def insert_profile(firstname: str, lastname: str, email: str, password: str, study_group_id: str, study_group: str, average_grade: str, total_credits: str, connection_provider=get_connection):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    with connection_provider() as conn:
        try: 
            conn.execute("""
                INSERT INTO profiles (firstname, lastname, email, password, study_group_id, study_group, average_grade, total_credits)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (firstname, lastname, email, hashed.decode('utf-8'), study_group_id, study_group, average_grade, total_credits))
            conn.commit()
        except sqlite3.IntegrityError as e:
            raise ValueError(f"There is already an account registered with the following email: {email}")    

# Delete Student Account
def delete_profile(email: str, connection_provider=get_connection):
    with connection_provider() as conn:
        conn.execute("DELETE FROM profiles WHERE email = ?", (email,))
    
# Check login credentials
def check_login_data(login_data: LoginData, connection_provider=get_connection):
    with connection_provider() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM profiles WHERE email = ?", (login_data.email,))
        row = cursor.fetchone()
        if row:
            stored_hash = row[0]
            return bcrypt.checkpw(login_data.password.encode('utf-8'), stored_hash.encode('utf-8'))
        return False

# Insert all grades from the transcript for a student -> clear existing grades first
def update_grades(email: str, modules: List[Dict], connection_provider=get_connection):
    clear_grades(email, connection_provider)
    with connection_provider() as conn:
        for module in modules:
            conn.execute("""
                INSERT INTO modules (module, grade, credits, email)
                VALUES (?, ?, ?, ?)
            """, (module["module"], module["grade"], module["ects"], email))
        conn.commit()

# Update study progress (average grade and total credits) of a student profile
def update_study_progress(email: str, avg: str, total: str, connection_provider=get_connection):
    with connection_provider() as conn:
        conn.execute("UPDATE profiles SET average_grade = ?, total_credits = ? WHERE email = ?", (avg, total, email))
        conn.commit()

# Update study group of a student profile
def update_study_group(email: str, new_group_id: str, new_group: str, connection_provider=get_connection):
    with connection_provider() as conn:
        conn.execute("UPDATE profiles SET study_group_id = ? WHERE email = ?", (new_group_id, email))
        conn.execute("UPDATE profiles SET study_group = ? WHERE email = ?", (new_group, email))
        conn.commit()

# Insert lectures if they are not already present and link them to the student's profile -> clear existing lectures for the student first
def update_timetable(email: str, lectures: List[Lecture], connection_provider=get_connection):
    clear_timetable(email, connection_provider)
    with connection_provider() as conn:
        for lec in lectures:
            conn.execute("""
                INSERT OR IGNORE INTO lectures (title, room, format, weekday, time)
                VALUES (?, ?, ?, ?, ?)
            """, (lec.title, lec.room, lec.format, lec.weekday, lec.time))
            conn.execute("""
                INSERT INTO profile_lecture (email, room, weekday, time)
                VALUES (?, ?, ?, ?)
            """, (email, lec.room, lec.weekday, lec.time))
        conn.commit()

# Insert exams if they are not already present and link them to the student's profile -> clear existing exams for the student first
def update_exams(email: str, exams: List[Exam], connection_provider=get_connection):
    clear_exams(email, connection_provider)
    with connection_provider() as conn:
        for exam in exams:
            conn.execute("""
                INSERT OR IGNORE INTO exams (exam_name, study_groups, examiner, exam_date)
                VALUES (?, ?, ?, ?)
            """, (exam.examName, exam.studyGroups, exam.examiner, exam.examDate.isoformat()))
            conn.execute("""
                INSERT INTO profile_exam (email, examiner, exam_date)
                VALUES (?, ?, ?)
            """, (email, exam.examiner, exam.examDate.isoformat()))
        conn.commit()

# Retrieve all lectures attended by a specific student profile
def get_lectures_for_profile(email: str, connection_provider=get_connection):
    with connection_provider() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.title, t.room, t.format, t.weekday, t.time
            FROM lectures t
            JOIN profile_lecture pl ON t.room = pl.room AND t.time = pl.time AND t.weekday = pl.weekday
            WHERE pl.email = ?
        """, (email,))
        return [
            {
                'title': row[0],
                'room': row[1],
                'format': row[2],
                'weekday': row[3],
                'time': row[4]
            } for row in cursor.fetchall()
        ]

# Get graded modules for a specific student profile
def get_modules_for_profile(email: str, connection_provider=get_connection):
    with connection_provider() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT module, grade, credits FROM modules WHERE email = ?", (email,))
        return [{'module': m, 'grade': g, 'ects': str(e)} for m, g, e in cursor.fetchall()]

# Get general profile information for a specific student profile
def get_profile_summary(email: str, connection_provider=get_connection):
    with connection_provider() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT firstname, average_grade, total_credits FROM profiles WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row:
            return {
                'firstname': row[0],
                'average_grade': row[1],
                'total_credits': row[2]
            }
        return None

# Get all exams for a specific student profile
def get_exams_for_profile(email: str, connection_provider=get_connection):
    with connection_provider() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.exam_name, e.study_groups, e.examiner, e.exam_date
            FROM exams e
            JOIN profile_exam pe ON e.examiner = pe.examiner AND e.exam_date = pe.exam_date
            WHERE pe.email = ?
        """, (email,))
        return [
            {
                'examName': row[0],
                'studyGroups': row[1],
                'examiner': row[2],
                'examDate': datetime.fromisoformat(row[3])
            } for row in cursor.fetchall()
        ]

# Get the study group for a specific student profile
def get_study_group_for_profile(email: str, connection_provider=get_connection):
    with connection_provider() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT study_group FROM profiles WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row:
            return row[0]
        return None

# Clear student-specific grades (modules) to replace them with new ones
def clear_grades(email: str, connection_provider=get_connection):
    with connection_provider() as conn:
        conn.execute("DELETE FROM modules WHERE email = ?", (email,))
        conn.commit()

# Clear student-specific lecture links to replace them with new ones
def clear_timetable(email: str, connection_provider=get_connection):
    with connection_provider() as conn:
        conn.execute("DELETE FROM profile_lecture WHERE email = ?", (email,))
        conn.commit()

# Clear student-specific exam links to replace them with new ones
def clear_exams(email: str, connection_provider=get_connection):
    with connection_provider() as conn:
        conn.execute("DELETE FROM profile_exam WHERE email = ?", (email,))
        conn.commit()

# Retrieves all exams scheduled for tomorrow.
def get_all_exams_in_seven_days(connection_provider=get_connection):
    in_seven = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    with connection_provider() as conn:
        cursor = conn.cursor()
        # exam_date LIKE '2025-06-14%' findes every exam on the 14th of June 2025, regardless of the time
        cursor.execute("SELECT * FROM exams WHERE exam_date LIKE ?", (f"{in_seven}%",))
        return [
            {
                'examName': row[0],
                'studyGroups': row[1],
                'examiner': row[2],
                'examDate': datetime.fromisoformat(row[3])
            } for row in cursor.fetchall()
        ]
    
# Retrieves all exam takers (firstname, lastname, email) for a specific exam.
def get_all_exam_takers_for_specific_exam(examiner: str, exam_date: datetime, connection_provider=get_connection):
    with connection_provider() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.firstname, p.lastname, p.email
            FROM profiles p
            JOIN profile_exam pe ON p.email = pe.email
            WHERE pe.examiner = ? AND pe.exam_date = ?
        """, (examiner, exam_date.isoformat()))
        return [
            {
                'firstname': row[0],
                'lastname': row[1],
                'email': row[2]
            } for row in cursor.fetchall()
        ]