import pytest
import sqlite3
import tempfile
from types import SimpleNamespace
from student_hub import rating_storing, profile_storing 

@pytest.fixture
def connection_provider(tmp_path):
    # Erstelle temporäre Datei im pytest-Verzeichnis
    db_file = tmp_path / "test.db"

    def provider():
        return sqlite3.connect(db_file)

    # ❗ Initialisiere Tabellen in dieser DB
    profile_storing.initialize_db(connection_provider=provider)
    rating_storing.initialize_db(connection_provider=provider)

    return provider

def test_insert_and_get_professor_rating(connection_provider):
    email = "rate@example.com"
    profile_storing.insert_profile("Max", "Tester", email, "pw", "42", "TestGroup", "1.0", "30", connection_provider=connection_provider)

    rating = SimpleNamespace(
        profKey=123456789,
        profName="Prof. Test",
        stars=4,
        comment="Sehr gut erklärt!"
    )

    rating_storing.insert_rating(email, rating, connection_provider=connection_provider)
    
    ratings = rating_storing.get_all_ratings_for_prof(123456789, connection_provider=connection_provider)
    assert len(ratings) == 1
    assert ratings[0]["stars"] == 4
    assert ratings[0]["comment"] == "Sehr gut erklärt!"
