import sqlite3
from student_hub.util_classes import Rating

DB_NAME = "studenthub.db"

def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_db(connection_provider=get_connection):
    with connection_provider() as conn:
        c = conn.cursor()

        # Professors table (stores all professors which are rated - the id is the phone number of the professor)
        c.execute("""
        CREATE TABLE IF NOT EXISTS professors (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
        """)

        # Ratings table (stores all ratings - a rating is always linked to a professor and a profile / author)
        c.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            professor_id INTEGER NOT NULL,
            overall_rating INTEGER NOT NULL CHECK (overall_rating BETWEEN 1 AND 5),
            comment TEXT,
            FOREIGN KEY (email) REFERENCES profiles(email),
            FOREIGN KEY (professor_id) REFERENCES professors(id)
        )
        """)

        conn.commit()


# Insert a professor into the database if they do not already exist.
def insert_professor(id: str, prof_name: str, connection_provider=get_connection):
    with connection_provider() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO professors (id, name)
            VALUES (?, ?)
        """, (id, prof_name))
        conn.commit()

# Insert a rating for a professor by a student profile (as author).
def insert_rating(email: str, rating: Rating, connection_provider=get_connection):
    insert_professor(rating.profKey, rating.profName, connection_provider=connection_provider)
    with connection_provider() as conn:
        conn.execute("""
            INSERT INTO ratings (email, professor_id, overall_rating, comment)
            VALUES(?, ?, ?, ?)
        """, (email, rating.profKey, rating.stars, rating.comment))
        conn.commit()

# Retrieve all ratings for a specific professor by their ID.
def get_all_ratings_for_prof(prof_id: int, connection_provider=get_connection):
    with connection_provider() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, overall_rating, comment
            FROM ratings
            WHERE professor_id = ?
        """, (prof_id,))
        return [
            {
                'id': row[0],
                'stars': row[1],
                'comment': row[2],
            } for row in cursor.fetchall()
        ]