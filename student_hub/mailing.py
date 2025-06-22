from student_hub.profile_storing import get_all_exam_takers_for_specific_exam, get_all_exams_in_seven_days
from datetime import datetime
import smtplib
import ssl
import certifi
from email.message import EmailMessage
from email.utils import formataddr

def get_all_examtakers_for_exams_in_seven():
    """
    Retrieves all exam takers for exams scheduled in seven days.
    
    Returns:
        examtakers (list): List of dictionaries containing exam taker information.
    """
    exams = get_all_exams_in_seven_days()
    all_exam_takers = []
    
    for exam in exams:
        exam_takers = get_all_exam_takers_for_specific_exam(exam["examiner"], exam["examDate"])
        for taker in exam_takers:
            all_exam_takers.append({
                "exam_date": exam["examDate"],
                "exam_name": exam["examName"],
                "taker_email": taker["email"],
                "taker_name": f"{taker['firstname']} {taker['lastname']}"
            })
    
    return all_exam_takers

def send_exam_reminder_email(exam_taker_info):
    """
    Sends an email reminder to an exam taker about their upcoming exam.
    
    Args:
        exam_taker_info (dict): Dictionary containing exam taker information.
    """
    subject = f"Reminder: Anstehende Prüfung - {exam_taker_info['exam_name']}"

    # Parse the exam date and format it to German date format
    exam_date = exam_taker_info['exam_date']
    formatted_date = exam_date.strftime("%d.%m.%Y %H:%M")

    # Create email body
    body = f"""
    Hallo {exam_taker_info['taker_name']},

    Das ist eine Erinnerung für Ihre bevorstehende Prüfung:

    Prüfungs Name: {exam_taker_info['exam_name']}
    Prüfungs Datum: {formatted_date}

    Beste Grüße,
    Student Hub
    """

    print(f"Sending email to: {exam_taker_info['taker_email']}\nSubject: {subject}\nBody:\n{body}")

    # Set up email parameters
    sender_email = "dominikcnicklas@gmail.com"
    sender_password = "hulo idav akjo ogwr"
    receiver_email = exam_taker_info['taker_email']

    # Create email message
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = formataddr(("Student Hub", "noreply-studenthub@hm.edu"))
    msg['To'] = receiver_email
    msg.set_content(body)

    # Send email
    context = ssl.create_default_context(cafile=certifi.where())
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
    except Exception as e:
        print(e)

def find_and_send_exam_reminders():
    """
    Finds all exam takers for exams scheduled in seven days and sends them reminder emails.
    """
    # Get all exam takers and exam information for exams scheduled in the seven days
    exam_takers = get_all_examtakers_for_exams_in_seven()
    
    if not exam_takers:
        print("Nobody takes a exam which is scheduled in seven days.")
        return
    
    # Send reminder emails to all exam takers
    for exam_taker in exam_takers:
        send_exam_reminder_email(exam_taker)
