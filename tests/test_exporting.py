import pytest
from student_hub.exporting import get_ics_file_for_user_timetable
from ics import Calendar

@pytest.fixture
def mock_lectures():
    return [
        {
            "title": "Informationssysteme 2",
            "room": "R1.007",
            "format": "Vorlesung",
            "weekday": "Freitag",
            "time": "11:45 - 13:15"
        },
        {
            "title": "Algorithmen und Datenstrukturen",
            "room": "R2.014",
            "format": "Vorlesung",
            "weekday": "Mittwoch",
            "time": "11:45 - 13:15"
        }
    ]

def test_ics_generation_with_mocked_lectures(mock_lectures, mocker):
    # mock db call to return the mock lectures
    mocker.patch(
        "student_hub.exporting.get_lectures_for_profile",
        return_value=mock_lectures
    )

    calendar = get_ics_file_for_user_timetable("student@example.com")
    
    assert len(calendar.events) == 2

    events_by_name = {event.name: event for event in calendar.events}

    assert "Informationssysteme 2" in events_by_name
    assert events_by_name["Informationssysteme 2"].location == "R1.007"
    assert events_by_name["Informationssysteme 2"].description == "Vorlesung"

    assert "Algorithmen und Datenstrukturen" in events_by_name
    assert events_by_name["Algorithmen und Datenstrukturen"].location == "R2.014"
    assert events_by_name["Algorithmen und Datenstrukturen"].description == "Vorlesung"

