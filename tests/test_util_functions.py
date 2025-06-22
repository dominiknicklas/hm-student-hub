import pytest
from student_hub.util_functions import extract_data_from_transcript_text, extract_lectures_from_html, extract_exam_date, extract_suiting_exams_for_student

def test_extract_data_from_transcript_text():
    # Fake transcript text for testing
    text = """
        Software Entwicklung I    1,0    5    5,0
        Informationssysteme I    1,3    5    5,0
        Ø-Note: 1,4
        ECTS-Gesamt: 90,0
    """

    # Call the function to extract data from the transcript text - this should return a dictionary with modules, average grade and total ECTS
    result = extract_data_from_transcript_text(text)
    assert result["average_grade"] == "1.4"
    assert result["ects_total"] == "90.0"
    assert len(result["modules"]) == 2
    assert result["modules"][0]["module"] == "Software Entwicklung I"
    assert result["modules"][0]["grade"] == "1.0"


def test_extract_lectures_from_html():
    # Fake HTML content (ZPA Course Plan page) for testing
    html = """
    <table>
        <tbody class="plan">
            <tr>
                <td class="time">10:00</td>
                <td></td><td></td><td></td><td></td>
                <td>
                    <div class="timeslot_red"><strong>Informationssysteme 2</strong>R0.007</div>
                </td>
            </tr>
            <tr>
                <td class="time">11:45</td>
                <td></td><td></td><td></td><td></td>
                <td>
                    <div class="timeslot_blue"><strong>Informationssysteme 2</strong>R1.007</div>
                </td>
            </tr>
        </tbody>
    </table>
    """

    # Call the function to extract lectures from the HTML content - this should return a list of dictionaries with the given lecture details
    result = extract_lectures_from_html(html)
    assert len(result) == 2
    assert result[0]["title"] == "Informationssysteme 2"
    assert result[0]["format"] == "Praktikum"
    assert result[0]["room"] == "R0.007"
    assert result[0]["weekday"] == "Freitag"

    assert result[1]["title"] == "Informationssysteme 2"
    assert result[1]["format"] == "Vorlesung"
    assert result[1]["room"] == "R1.007"
    assert result[1]["weekday"] == "Freitag"


def test_extract_exam_date():
    # Test with a date string formatted as 'DD.MM.YYYY \n HH:MM' - this should return a datetime object with timezone set to Europe/Berlin
    result = extract_exam_date("21.07.2025 \n 16:00")
    assert result.isoformat() == "2025-07-21T16:00:00+02:00"


def test_extract_suiting_exams_for_student(mocker):
    exams = [
        {'examName': 'Datenmanagement', 'studyGroups': 'WT4A WT4B'},
        {'examName': 'Wirtschaftsmathe 2', 'studyGroups': 'WT2'},
    ]

    # Mock the get_study_group_for_profile function to return a specific study group for the test
    mocker.patch("student_hub.util_functions.get_study_group_for_profile", return_value="WT4A")

    # Call the function to extract exams for a student with a specific email - this should return only the exams that match the study group
    result = extract_suiting_exams_for_student(exams, "max@example.com")
    assert len(result) == 1
    assert result[0]["examName"] == "Datenmanagement"
