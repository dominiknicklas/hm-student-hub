import os
import tempfile
import pytest
import sqlite3
from datetime import datetime, timedelta
from student_hub import profile_storing
from student_hub.util_classes import LoginData, Lecture, Exam

TEST_USER = {
    "firstname": "Max",
    "lastname": "Mustermann",
    "email": "max@example.com",
    "password": "securepw",
    "study_group_id": "220",
    "study_group": "WT4A",
    "average_grade": "1.4",
    "total_credits": "90",
}

@pytest.fixture
def connection_provider(tmp_path):
    # Create a temporary SQLite database file for each test
    # This ensures that each test runs with a fresh database
    db_file = tmp_path / "test.db"

    def provider():
        return sqlite3.connect(db_file)

    # Initialize the temp database schema
    profile_storing.initialize_db(connection_provider=provider)

    return provider

def test_profile_insertion_and_login(connection_provider):
    # Insert student profile
    profile_storing.insert_profile(**TEST_USER, connection_provider=connection_provider)

    # Check if login with correct credentials works
    login = LoginData(email="max@example.com", password="securepw")
    assert profile_storing.check_login_data(login, connection_provider=connection_provider)


def test_profile_insertion_and_login_wrong_credentials(connection_provider):
    # Insert student profile
    profile_storing.insert_profile(**TEST_USER, connection_provider=connection_provider)

    # Check if login with wrong password fails
    login = LoginData(email="max@example.com", password="wrongpw")
    assert profile_storing.check_login_data(login, connection_provider=connection_provider) is False


def test_login_with_non_existent_profile(connection_provider):
    # Check if login with non-existent profile fails
    login = LoginData(email="nouser@example.com", password="nopassword")
    assert profile_storing.check_login_data(login, connection_provider=connection_provider) is False


def test_duplicate_profile_insertion_raises(connection_provider):
    # Insert student profile
    profile_storing.insert_profile(**TEST_USER, connection_provider=connection_provider)

    # Try to insert the same profile again (profile with same email), should raise ValueError
    with pytest.raises(ValueError) as e:
        profile_storing.insert_profile(**TEST_USER, connection_provider=connection_provider)

    assert "Es existiert bereits ein Account mit der E-Mail-Adresse: max@example.com" in str(e.value)


def test_update_and_read_modules(connection_provider):
    # Insert student profile
    profile_storing.insert_profile(**TEST_USER, connection_provider=connection_provider)
    
    # Update grades/modules for the profile
    profile_storing.update_grades(TEST_USER["email"], [
        {"module": "Software Entwicklung", "grade": "1.0", "ects": 5},
        {"module": "Wirtschaftsinformatik", "grade": "1.7", "ects": 10}
    ],
        connection_provider=connection_provider
    )
    
    # Read modules for the profile and check if the values are correct
    result = profile_storing.get_modules_for_profile(TEST_USER["email"], connection_provider=connection_provider)
    assert len(result) == 2
    assert result[0]["module"] == "Software Entwicklung"
    assert result[1]["grade"] == "1.7"


def test_update_study_progress_and_get_profile_summary(connection_provider):
    # Insert student profile
    profile_storing.insert_profile(**TEST_USER, connection_provider=connection_provider)

    # Update study progress
    profile_storing.update_study_progress(TEST_USER["email"], avg="1.5", total="130", connection_provider=connection_provider)

    # Get profile summary and check if the values are updated
    result = profile_storing.get_profile_summary(TEST_USER["email"], connection_provider=connection_provider)
    assert result["firstname"] == TEST_USER["firstname"]
    assert result["average_grade"] == "1.5"
    assert result["total_credits"] == "130"


def test_update_and_get_study_group(connection_provider):
    # Insert student profile
    profile_storing.insert_profile(**TEST_USER, connection_provider=connection_provider)

    # Update study group
    profile_storing.update_study_group(TEST_USER["email"], new_group_id="230", new_group="WT5A", connection_provider=connection_provider)

    # Get study group for the profile and check if it is updated
    group = profile_storing.get_study_group_for_profile(TEST_USER["email"], connection_provider=connection_provider)
    assert group == "WT5A"


def test_update_timetable_and_get_lectures(connection_provider):
    # Insert student profile
    profile_storing.insert_profile(**TEST_USER, connection_provider=connection_provider)

    lectures = [
        Lecture(title="Informationssysteme 2", room="R0.007", format="Praktukum", weekday="Freitag", time="10:00"),
        Lecture(title="Algorithmen und Datenstrukturen", room="R1.009", format="Vorlesung", weekday="Mittwoch", time="11:45"),
    ]

    # Update timetable with lectures
    profile_storing.update_timetable(TEST_USER["email"], lectures, connection_provider=connection_provider)

    # Get lectures for the profile and check if they are correctly stored
    result = profile_storing.get_lectures_for_profile(TEST_USER["email"], connection_provider=connection_provider)
    assert len(result) == 2
    assert result[0]["title"] == "Informationssysteme 2"
    assert result[1]["format"] == "Vorlesung"


def test_update_exams_and_get_exams(connection_provider):
    # Insert student profile
    profile_storing.insert_profile(**TEST_USER, connection_provider=connection_provider)

    exams = [
        Exam(examName="Datenmanagement Klausur", studyGroups="WT4A", examiner="Dr. Tester", examDate=datetime(2025, 7, 18)),
        Exam(examName="Algorithmen Klausur", studyGroups="WT4A", examiner="Prof. Max", examDate=datetime(2025, 7, 21)),
    ]
    # Update exams for the profile
    profile_storing.update_exams(TEST_USER["email"], exams, connection_provider=connection_provider)

    # Get exams for the profile and check if they are correctly stored
    result = profile_storing.get_exams_for_profile(TEST_USER["email"], connection_provider=connection_provider)
    assert len(result) == 2
    assert result[0]["examName"] == "Datenmanagement Klausur"
    assert result[1]["examiner"] == "Prof. Max"


def test_get_all_exams_in_seven_days(connection_provider):
    # Insert student profile
    profile_storing.insert_profile(**TEST_USER, connection_provider=connection_provider)

    date_in_7_days = (datetime.now() + timedelta(days=7)).replace(hour=10, minute=0, second=0, microsecond=0)
    exam = Exam(
        examName="Mathematik I",
        studyGroups="1,2,3",
        examiner="Prof. Euler",
        examDate=date_in_7_days
    )

    # Update exams for the profile to include an exam in 7 days
    profile_storing.update_exams(TEST_USER["email"], [exam], connection_provider=connection_provider)

    # Get all exams scheduled in the next 7 days and check if the exam is included
    results = profile_storing.get_all_exams_in_seven_days(connection_provider=connection_provider)
    assert any(e["examName"] == "Mathematik I" and e["examiner"] == "Prof. Euler" for e in results)


def test_get_all_exam_takers_for_specific_exam(connection_provider):
    # Insert two student profiles
    profile_storing.insert_profile(**TEST_USER, connection_provider=connection_provider)
    profile_storing.insert_profile(
        firstname="Joe",
        lastname="Schmoe",
        email="joe@example.com",
        password="anothersecurepw",
        study_group_id="220",
        study_group="WT4A",
        average_grade="2.0",
        total_credits="60",
        connection_provider=connection_provider
    )

    exam_date = datetime(2025, 6, 30, 9, 0, 0)
    exam = Exam(
        examName="Programmierung",
        studyGroups="1",
        examiner="Prof. Turing",
        examDate=exam_date
    )

    # Update exams for both profiles to include the same exam
    profile_storing.update_exams(TEST_USER["email"], [exam], connection_provider=connection_provider)
    profile_storing.update_exams("joe@example.com", [exam], connection_provider=connection_provider)

    # Get all exam takers for the specific exam and check if both profiles are included
    takers = profile_storing.get_all_exam_takers_for_specific_exam("Prof. Turing", exam_date, connection_provider=connection_provider)
    assert len(takers) == 2
    assert takers[0]["email"] == TEST_USER["email"]
    assert takers[0]["firstname"] == TEST_USER["firstname"]