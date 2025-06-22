import pytest
from datetime import datetime
from student_hub.mailing import find_and_send_exam_reminders, send_exam_reminder_email

def test_find_and_send_exam_reminders(mocker):
    exams = [
        {
            "examiner": "Prof. Max Mustermann",
            "examDate": "2025-07-21T16:30:00",
            "examName": "Algorithmen und Datenstrukturen",
        }
    ]
    exam_takers = [
        {
            "email": "student@example.com",
            "firstname": "Student",
            "lastname": "Tester"
        }
    ]

    # Mock the db calls to return the test data
    mocker.patch("student_hub.mailing.get_all_exams_in_seven_days", return_value=exams)
    mocker.patch("student_hub.mailing.get_all_exam_takers_for_specific_exam", return_value=exam_takers)

    # Mock the email sending function
    send_mock = mocker.patch("student_hub.mailing.send_exam_reminder_email")

    find_and_send_exam_reminders()

    send_mock.assert_called_once()
    args, _ = send_mock.call_args
    assert args[0]["taker_email"] == "student@example.com"
    assert args[0]["exam_name"] == "Algorithmen und Datenstrukturen"

def test_find_and_send_exam_reminders_no_exams(mocker):
    # Mock the db call to return an empty list for exams -> no exams in seven days
    mocker.patch("student_hub.mailing.get_all_exams_in_seven_days", return_value=[])

    # Mock the email sending function and print function
    send_mock = mocker.patch("student_hub.mailing.send_exam_reminder_email")
    mock_print = mocker.patch("builtins.print")

    find_and_send_exam_reminders()

    send_mock.assert_not_called()
    mock_print.assert_called()
    printed = "\n".join(call.args[0] for call in mock_print.call_args_list)
    assert "Nobody takes a exam which is scheduled in seven days." in printed

def test_email_content_printed(mocker):
    info = {
        "taker_email": "student@example.com",
        "taker_name": "Student Tester",
        "exam_name": "Algorithmen und Datenstrukturen",
        "exam_date": datetime.fromisoformat("2025-07-21T16:30:00"),
    }

    # Mock the print function to capture printed output and the SMTP_SSL call
    mock_print = mocker.patch("builtins.print")
    mocker.patch("student_hub.mailing.smtplib.SMTP_SSL")

    send_exam_reminder_email(info)

    mock_print.assert_called()
    printed = "\n".join(call.args[0] for call in mock_print.call_args_list)
    assert "Sending email to: student@example.com" in printed
    assert "Hallo Student Tester," in printed
    assert "Prüfungs Name: Algorithmen und Datenstrukturen" in printed
    assert "Prüfungs Datum: 21.07.2025" in printed
    assert "Beste Grüße," in printed
    assert "Student Hub" in printed
