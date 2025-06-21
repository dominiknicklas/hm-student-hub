from ics import Calendar, Event
from ics.grammar.parse import ContentLine
from datetime import date
from datetime import datetime, timedelta
import arrow
from student_hub import profile_storing

# Map weekday string to weekday number
weekday_map = {
    "Montag": 0,
    "Dienstag": 1,
    "Mittwoch": 2,
    "Donnerstag": 3,
    "Freitag": 4,
}

# Approximately end dates for semesters
SUMMER_SEMESTER_END = '07-31'
WINTER_SEMESTER_END = '01-31'

def get_ics_file_for_user_timetable(email):
    """
    Generates an ICS calendar file for the student's timetable.
    :param email: Student's email address to identify their profile and lectures.
    :return: An ics.Calendar object containing the student's lectures recurring weekly till the semester end.
    """

    # Retrieve lectures for the given profile
    lectures = profile_storing.get_lectures_for_profile(email)

    calendar = Calendar()

    # Create events for each lecture and add them to the calendar
    for lecture in lectures:
        e = create_event_for_lecture(lecture)
        calendar.events.add(e)

    return calendar


def get_next_semester_end():
    """
    Determines the end date of the current semester based on today's date.
    :return: A date object representing the end of the current semester.
    """
    today = date.today()
    current_year = today.year
    month = today.month

    if 2 <= month <= 7:
        # Between February and July -> summer semester
        return date.fromisoformat(f"{current_year}-{SUMMER_SEMESTER_END}")
    elif month >= 8:
        # Between August and December -> winter semester -> semester ends in January next year
        return date.fromisoformat(f"{current_year + 1}-{WINTER_SEMESTER_END}")
    else:
        # January -> winter semester
        return date.fromisoformat(f"{current_year}-{WINTER_SEMESTER_END}")


def create_event_for_lecture(lecture): 
    """
    Creates an ICS event for a given lecture.
    :param lecture: A dictionary containing lecture details like title, room, format, weekday, and time.
    :return: An ics.Event object representing the lecture.
    """
    today = datetime.today()

    # Get the corresponding weekday number to the lecture's weekday string
    weekday_num = weekday_map[lecture["weekday"]]

    # Find the next date with that weekday
    days_ahead = (weekday_num - today.weekday() + 7) % 7
    first_date = today + timedelta(days=days_ahead)

    # Parse time
    start_str, end_str = lecture["time"].split(" - ")
    start_time = datetime.strptime(start_str, "%H:%M").time()
    end_time = datetime.strptime(end_str, "%H:%M").time()

    # Combine date and time and set timezone to Europe/Berlin
    start_date = arrow.get(datetime.combine(first_date, start_time)).replace(tzinfo='Europe/Berlin')
    end_date = arrow.get(datetime.combine(first_date, end_time)).replace(tzinfo='Europe/Berlin')

    # Create event
    e = Event()
    e.name = lecture["title"]
    e.location = lecture["room"]
    e.description = lecture["format"]
    e.begin = start_date
    e.end = end_date

    # Set weekly recurrence until semester end (in UTC format)
    rrule_until = arrow.get(get_next_semester_end()).format("YYYYMMDDT000000Z")
    e.extra.append(ContentLine(name="RRULE", value=f"FREQ=WEEKLY;UNTIL={rrule_until}"))

    return e