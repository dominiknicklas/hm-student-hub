import pytest
import sqlite3
from student_hub.util_classes import Rating
from student_hub import rating_storing, profile_storing 

@pytest.fixture
def connection_provider(tmp_path):
    # Create a temporary SQLite database file for each test
    # This ensures that each test runs with a fresh database
    db_file = tmp_path / "test.db"

    def provider():
        return sqlite3.connect(db_file)

    # Initialize the temp database schema
    profile_storing.initialize_db(connection_provider=provider)
    rating_storing.initialize_db(connection_provider=provider)

    return provider

def test_insert_and_get_professor_rating(connection_provider):
    # Insert student who publishes a rating
    email = "max@example.com"
    profile_storing.insert_profile("Max", "Mustermann", email, "pw", "220", "WT4A", "1.0", "30", connection_provider=connection_provider)

    rating = Rating(
        profKey="123456789",
        profName="Prof. Test",
        stars=4,
        comment="Sehr gut erklärt!"
    )

    # Add rating
    rating_storing.insert_rating(email, rating, connection_provider=connection_provider)
    
    # Get all ratings for the prof and check if the response matches the published rating
    ratings = rating_storing.get_all_ratings_for_prof(123456789, connection_provider=connection_provider)
    assert len(ratings) == 1
    assert ratings[0]["stars"] == 4
    assert ratings[0]["comment"] == "Sehr gut erklärt!"
