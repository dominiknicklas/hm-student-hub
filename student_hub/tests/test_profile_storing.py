import os
import tempfile
import pytest
import sqlite3
from datetime import datetime, timedelta
from student_hub import profile_storing
from student_hub.util_classes import LoginData, Lecture, Exam

@pytest.fixture
def connection_provider(tmp_path):
    # Erstelle temporäre Datei im pytest-Verzeichnis
    db_file = tmp_path / "test.db"

    def provider():
        return sqlite3.connect(db_file)

    # ❗ Initialisiere Tabellen in dieser DB
    profile_storing.initialize_db(connection_provider=provider)

    return provider

def test_profile_insertion_and_login(connection_provider):
    profile_storing.insert_profile(
        firstname="Ada",
        lastname="Lovelace",
        email="ada@example.com",
        password="securepw",
        study_group_id="1",
        study_group="Mathematik",
        average_grade="1.1",
        total_credits="60",
        connection_provider=connection_provider
    )

    login = LoginData(email="ada@example.com", password="securepw")
    assert profile_storing.check_login_data(login, connection_provider=connection_provider)

def test_profile_insertion_and_login_wrong_credentials(connection_provider):
    profile_storing.insert_profile(
        firstname="Adaa",
        lastname="Lovelace",
        email="ada@example.com",
        password="securepw",
        study_group_id="1",
        study_group="Mathematik",
        average_grade="1.1",
        total_credits="60",
        connection_provider=connection_provider
    )

    login = LoginData(email="ada@example.com", password="securepwd")
    assert profile_storing.check_login_data(login, connection_provider=connection_provider) is False

def test_login_with_non_existent_profile(connection_provider):
    login = LoginData(email="nouser@example.com", password="nopassword")
    assert profile_storing.check_login_data(login, connection_provider=connection_provider) is False

def test_duplicate_profile_insertion_raises(connection_provider):
    profile_storing.insert_profile(
        "Alan", "Turing", "alan@example.com", "pw123", "G2", "Informatik", "1.0", "90", connection_provider=connection_provider
    )

    with pytest.raises(ValueError) as e:
        profile_storing.insert_profile(
            "Alan", "Turing", "alan@example.com", "pw123", "G2", "Informatik", "1.0", "90", connection_provider=connection_provider
        )
    assert "Es existiert bereits ein Account mit der E-Mail-Adresse: alan@example.com" in str(e.value)

def test_update_and_read_modules(connection_provider):
    email = "susi@example.com"
    profile_storing.insert_profile("Susi", "Schlau", email, "pw", "1", "Bio", "2.0", "30", connection_provider=connection_provider)
    
    profile_storing.update_grades(email, [
        {"module": "Biologie", "grade": "1.3", "ects": 5},
        {"module": "Chemie", "grade": "2.0", "ects": 6}
    ],
        connection_provider=connection_provider
    )
    
    result = profile_storing.get_modules_for_profile(email, connection_provider=connection_provider)
    assert len(result) == 2
    assert result[0]["module"] == "Biologie"
    assert result[1]["grade"] == "2.0"

def test_update_study_progress_and_get_profile_summary(connection_provider):
    email = "user1@example.com"
    profile_storing.insert_profile("Uli", "User", email, "pw", "G1", "BWL", "3.0", "10", connection_provider=connection_provider)

    profile_storing.update_study_progress(email, avg="1.3", total="60", connection_provider=connection_provider)

    result = profile_storing.get_profile_summary(email, connection_provider=connection_provider)
    assert result["firstname"] == "Uli"
    assert result["average_grade"] == "1.3"
    assert result["total_credits"] == "60"

def test_update_and_get_study_group(connection_provider):
    email = "student@example.com"
    profile_storing.insert_profile("Stella", "Studier", email, "pw", "G1", "Informatik", "2.3", "20", connection_provider=connection_provider)

    profile_storing.update_study_group(email, new_group_id="X9", new_group="Data Science", connection_provider=connection_provider)

    group = profile_storing.get_study_group_for_profile(email, connection_provider=connection_provider)
    assert group == "Data Science"

def test_update_timetable_and_get_lectures(connection_provider):
    email = "timetable@example.com"
    profile_storing.insert_profile("Lisa", "Lehrplan", email, "pw", "D1", "Mathe", "1.7", "40", connection_provider=connection_provider)

    lectures = [
        Lecture(title="Mathematik I", room="H1", format="Vorlesung", weekday="Montag", time="08:00"),
        Lecture(title="Statistik", room="H2", format="Übung", weekday="Mittwoch", time="10:00"),
    ]

    profile_storing.update_timetable(email, lectures, connection_provider=connection_provider)
    result = profile_storing.get_lectures_for_profile(email, connection_provider=connection_provider)

    assert len(result) == 2
    assert result[0]["title"] == "Mathematik I"

def test_update_exams_and_get_exams(connection_provider):
    email = "exams@example.com"
    profile_storing.insert_profile("Tom", "Test", email, "pw", "X1", "Physik", "1.5", "60", connection_provider=connection_provider)

    exams = [
        Exam(examName="Physik Klausur", studyGroups="X1", examiner="Dr. Müller", examDate=datetime(2025, 7, 1)),
        Exam(examName="Mathe Test", studyGroups="X1", examiner="Prof. Schmidt", examDate=datetime(2025, 7, 15)),
    ]

    profile_storing.update_exams(email, exams, connection_provider=connection_provider)
    result = profile_storing.get_exams_for_profile(email, connection_provider=connection_provider)

    assert len(result) == 2
    assert result[0]["examName"] == "Physik Klausur"

def test_get_all_exams_in_seven_days(connection_provider):
    # Setup
    email = "test@example.com"
    profile_storing.insert_profile("Max", "Mustermann", email, "pw", "1", "Math", "1.0", "30", connection_provider=connection_provider)

    date_in_7_days = (datetime.now() + timedelta(days=7)).replace(hour=10, minute=0, second=0, microsecond=0)
    exam = Exam(
        examName="Mathematik I",
        studyGroups="1,2,3",
        examiner="Prof. Euler",
        examDate=date_in_7_days
    )

    profile_storing.update_exams(email, [exam], connection_provider=connection_provider)

    # Test
    results = profile_storing.get_all_exams_in_seven_days(connection_provider=connection_provider)
    assert any(e["examName"] == "Mathematik I" and e["examiner"] == "Prof. Euler" for e in results)


def test_get_all_exam_takers_for_specific_exam(connection_provider):
    # Setup
    email = "student@example.com"
    profile_storing.insert_profile("Emma", "Musterfrau", email, "pw", "1", "Informatik", "2.0", "60", connection_provider=connection_provider)

    exam_date = datetime(2025, 6, 30, 9, 0, 0)
    exam = Exam(
        examName="Programmierung",
        studyGroups="1",
        examiner="Prof. Turing",
        examDate=exam_date
    )

    profile_storing.update_exams(email, [exam], connection_provider=connection_provider)

    # Test
    takers = profile_storing.get_all_exam_takers_for_specific_exam("Prof. Turing", exam_date, connection_provider=connection_provider)
    assert len(takers) == 1
    assert takers[0]["email"] == email
    assert takers[0]["firstname"] == "Emma"