import pytest
from student_hub.mailing import find_and_send_exam_reminders, send_exam_reminder_email

def test_find_and_send_exam_reminders(mocker):
    # Beispiel-Daten vorbereiten
    exams = [
        {
            "examiner": "Prof. X",
            "examDate": "2025-06-28T10:00:00",
            "examName": "Algorithmen"
        }
    ]
    exam_takers = [
        {
            "email": "student@example.com",
            "firstname": "Ada",
            "lastname": "Lovelace"
        }
    ]

    # Return-Werte der gemockten Methoden
    mocker.patch("student_hub.mailing.get_all_exams_in_seven_days", return_value=exams)
    mocker.patch("student_hub.mailing.get_all_exam_takers_for_specific_exam", return_value=exam_takers)

    # Mock für den Emailversand
    send_mock = mocker.patch("student_hub.mailing.send_exam_reminder_email")

    # Call
    find_and_send_exam_reminders()

    # Assertions
    send_mock.assert_called_once()
    args, _ = send_mock.call_args
    assert args[0]["taker_email"] == "student@example.com"
    assert args[0]["exam_name"] == "Algorithmen"

def test_find_and_send_exam_reminders_no_exams(mocker):
    # Mock für keine anstehenden Prüfungen
    mocker.patch("student_hub.mailing.get_all_exams_in_seven_days", return_value=[])

    # Mock für den Emailversand
    send_mock = mocker.patch("student_hub.mailing.send_exam_reminder_email")
    mock_print = mocker.patch("builtins.print")

    # Call
    find_and_send_exam_reminders()

    # Assertions
    send_mock.assert_not_called()
    mock_print.assert_called()
    printed = "\n".join(call.args[0] for call in mock_print.call_args_list)
    assert "Nobody takes a exam which is scheduled in seven days." in printed

def test_email_content_printed(mocker):
    info = {
        "taker_email": "test@example.com",
        "taker_name": "Test Person",
        "exam_name": "Mathe 2",
        "exam_date": "2025-06-28T14:00:00"
    }

    mock_print = mocker.patch("builtins.print")

    # SMTP-Versand auch mocken!
    mocker.patch("student_hub.mailing.smtplib.SMTP_SSL")

    send_exam_reminder_email(info)

    mock_print.assert_called()
    printed = "\n".join(call.args[0] for call in mock_print.call_args_list)
    assert "Sending email to: test@example.com" in printed
    assert "Hallo Test Person," in printed
    assert "Prüfungs Name: Mathe 2" in printed
    assert "Prüfungs Datum: 28.06.2025" in printed
    assert "Beste Grüße," in printed
    assert "Student Hub" in printed
