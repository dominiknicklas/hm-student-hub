import re
from datetime import datetime
import zoneinfo
from student_hub.profile_storing import get_study_group_for_profile, update_grades, update_study_progress
from bs4 import BeautifulSoup
import pdfplumber
import io
from typing import List
from student_hub.util_classes import Exam

def parse_pdf_and_save_to_profile(content: bytes, email: str):
    """
    Extracts total achieved ECTS, average grade and modules from the uploaded transcript and stores them to the profile of the given email.

    Args:
        email (str): The profile of the student who uploaded the transcript.
    """
    # Extract all readable text from a PDF and summarize it in a string.
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

    try:
        # Extract the relevant data from the transcript text
        transcript_information = extract_data_from_transcript_text(text)
    except ValueError:
        raise # raise error to main -> http handling
    
    update_study_progress(email, transcript_information["average_grade"], transcript_information["ects_total"])
    update_grades(email, transcript_information["modules"])


def extract_data_from_transcript_text(text: str):
    """
    Extracts total achieved ECTS, average grade and modules (which are already graded) from the transcript text (of the transcript PDF).

    Args:
        text (str): The text content of the transcript.

    Returns:
        transcript_content (dict): A dictionary containing:
            - 'modules' (list[dict]): List of modules with 'module', 'grade', and 'ects'.
            - 'ects_total' (str): The total achieved ECTS.
            - 'average_grade' (str): The average grade.
    """

    modules = []
    ects_total = None
    average_grade = None

    lines = text.splitlines()

    # Regex pattern that matches module entries in the format: e.g., "Software Entwicklung I    1,0    5    5,0"
    # Captures: module name, grade, ECTS points in individual groups ignoring whitespaces between them and the "Gewichtung" between grade and ECTS.
    module_pattern = re.compile(r"^(.*?)\s+(\d,\d)\s+\d+\s+(\d+,\d)$")

    # Loop through each line of the transcript text
    for line in lines:
        # Try to match the line against the module pattern -> if successful, extract module name, grade and ECTS (stored in groups 1, 2 and 3)
        # and append it to the modules list
        if match := module_pattern.match(line):
            module_name, grade, ects = match.groups()
            modules.append({
                "module": module_name.strip(),
                "grade": grade.replace(",", "."),
                "ects": ects.replace(",", ".")
            })

        # If the line contains "ECTS-Gesamt", extract the total ECTS points
        if "ECTS-Gesamt" in line:
            # Regex to find the total ECTS points in the format "ECTS-Gesamt: X..,X.." and stores the value in a group
            ects_total = re.search(r"ECTS-Gesamt:\s*(\d+,\d+)", line)
            if ects_total:
                ects_total = ects_total.group(1).replace(",", ".")

        # If the line contains "Ø-Note", extract the average grade
        if "Ø-Note" in line:
            # Regex to find the average grade in the format "Ø-Note: X..,X.." and stores the value in a group
            avg = re.search(r"Ø-Note:\s*(\d+,\d+)", line)
            if avg:
                average_grade = avg.group(1).replace(",", ".")

    if average_grade is None or ects_total is None:
        raise ValueError("Missing value: average grade or total ECTS not found in the PDF. - The uploaded Transcript appears to be not valid")
    
    return {
        "modules": modules,
        "ects_total": ects_total,
        "average_grade": average_grade
    }


def extract_lectures_from_html(html: str):
    """
    Extracts lecture information from the HTML content of a course plan page.

    Args:
        html (str): The HTML content of the course plan page.

    Returns:
        lectures (list[dict]): A list of dictionaries containing lecture details with keys:
            - 'weekday' (str): Day of the week.
            - 'time' (str): Time of the lecture.
            - 'title' (str): Title of the lecture.
            - 'format' (str): Type of session (e.g., Vorlesung or Praktikum).
            - 'room' (str): Room where the lecture takes place.
    """
    
    soup = BeautifulSoup(html, 'html.parser')

    # Select all rows of the timetable (each row represents a time slot in the first column of the row and the weekdays in the columns 1 to 6)
    rows = soup.select('tbody.plan tr')

    timetable = []

    for row in rows:
        # Extract the time from the first cell (td) of the row
        time_cell = row.find('td', class_='time')
        time = time_cell.get_text(strip=True) if time_cell else "?"

        # Extract all day cells (td) in the row, skipping the first cell which contains the time
        day_cells = row.find_all('td')[1:]
        weekdays = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag']

        # Iterate over each day cell (Monday to Friday) containing the lectures or practicals on that day at the defined time
        for i, cell in enumerate(day_cells):
            # Select all lecture or practical blocks within the cell (on a specific day at the defined time) and iterate over them
            for slot in cell.select('div.timeslot_blue, div.timeslot_red'):
                
                # Extract the title of the lecture
                title_el = slot.find('strong')
                title = title_el.get_text(strip=True) if title_el else "?"

                # Determine the type by the class of the div -> "Vorlesung" for blue and "Praktikum" for red
                if 'timeslot_red' in slot.get('class', []):
                    format = "Praktikum"
                elif 'timeslot_blue' in slot.get('class', []):
                    format = "Vorlesung"

                timetable.append({
                    'weekday': weekdays[i],
                    'time': time,
                    'title': title,
                    'format': format,
                    'room': slot.get_text(separator=" ", strip=True).split()[-1],
                })

    return timetable


def extract_exam_date(date_str: str):
    """
    Extracts the date from a string formatted as 'DD.MM.YYYY \n HH:MM'.
    
    Args:
        date_str (str): The date string to extract from.
        
    Returns:
        date (datetime): The extracted date in datetime format with timezone set to Europe/Berlin.
    """
    date_part = date_str.split('\n')[0] # Get the first part which is the date
    time_part = date_str.split('\n')[-1]  # Get the last part which is the time
    
    datetime_str = f"{date_part.strip()} {time_part.strip()}"
    dt_naive = datetime.strptime(datetime_str, "%d.%m.%Y %H:%M")

    # Set the timezone to Europe/Berlin
    berlin_tz = zoneinfo.ZoneInfo("Europe/Berlin")
    dt_berlin = dt_naive.replace(tzinfo=berlin_tz)

    return dt_berlin

def extract_suiting_exams_for_student(all_exams: List[Exam], email: str):
    """
    Extracts exams that match the student's study group from the list of all exams.
    
    Args:
        all_exams (List): List of all exams.
        email (str): The student's email to determine their study group.
        
    Returns:
        exams (List[Exam]): List of exams that match the student's study group.
    """
    # Assuming profile_storing.get_study_group(email) returns the study group for the student
    study_group = get_study_group_for_profile(email)
    if not study_group:
        return []

    # Filter exams based on the student's study group
    return [exam for exam in all_exams if study_group in exam.studyGroups]