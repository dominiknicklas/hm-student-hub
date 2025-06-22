import requests
from bs4 import BeautifulSoup
import re
from student_hub.util_functions import extract_exam_date, extract_lectures_from_html

# Base URLs for scraping
ZPA_PUBLIC_URL = "https://zpa.cs.hm.edu/public/"
FK07_PROFESSOR_URL = "https://cs.hm.edu/fakultaet/personen/professuren.de.html"

def scrape_all_study_groups():
    """
    Scrapes all available study groups from the course plan page of the ZPA.

    Returns:
        study_groups (list[dict]): A list of dictionaries with 'value' and 'label' for each study group.
    """

    response = requests.get(ZPA_PUBLIC_URL + "course_plan/")
    if not response.ok:
        raise Exception(f"Failed to fetch page: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the select (dropdown) box with id="id_group" -> this contains the study groups
    group_select = soup.find('select', {'id': 'id_group'})

    if not group_select:
        raise Exception("<select> not found")

    # Extract all <option> entries -> each represents a study group
    study_group_options = []
    for option in group_select.find_all('option'):
        value = option.get('value') # unique identifier for the group
        label = option.text.strip() # name of the group (e.g. WT4A)
        if value and label:  # ignore empty option
            study_group_options.append({'value': value, 'label': label})

    return study_group_options


def scrape_course_plan_for_group(group_id: str):
    """
    Scrapes the course plan / timetable for a specific study group.

    Args:
        group_id (str): The unique identifier for the study group.

    Returns:
        lectures (list[dict]): A list of all lectures for the specified group.
    """

    # The timetable for each study group is loaded via a POST request, which is triggered when selecting a group from the dropdown on the course plan page (a form).
    # This POST request includes the selected study group ID and a CSRF token (which is embedded as a hidden input field in the HTML of the page)
    # Therefore, we must first send a GET request to the course plan page to retrieve the CSRF token, and then send a POST request containing both the group ID and the token.

    # A session is required because the initial GET request sets cookies which are necessary for the server to validate the CSRF token during the POST request.
    # Without using a session, the GET and POST requests would be stateless, and the server would reject the POST request due to missing or invalid cookies.
    session = requests.Session()

    # Step 1: Send an initial GET request to fetch the CSRF token and required cookies
    response = session.get(ZPA_PUBLIC_URL + "course_plan/")
    if not response.ok:
        raise Exception(f"Failed to fetch page: {response.status_code}")

    # Step 2: Parse the HTML to extract the CSRF token from the hidden input field
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find("input", {"name": "csrfmiddlewaretoken"})["value"]

    # Step 3: Prepare the POST payload with the CSRF token and selected study group ID
    payload = {
        "csrfmiddlewaretoken": csrf_token,
        "group": group_id
    }

    # Step 4: Define headers to mimic a real browser (important for CSRF validation)
    headers = {
        "Referer": ZPA_PUBLIC_URL + "course_plan/",
        "User-Agent": "Mozilla/5.0"
    }

    # Step 5: Send the POST request to load the timetable for the selected group
    post_response = session.post(ZPA_PUBLIC_URL + "course_plan/", data=payload, headers=headers)
    if not post_response.ok:
        raise Exception(f"Failed to fetch course plan: {post_response.status_code}")

    # Step 6: Parse the returned HTML using a helper function that extracts the lecture data
    return extract_lectures_from_html(post_response.text)


def scrape_all_professors():
    """
    Scrapes all professors names and phone numbers (used as unique identifiers) from the FK07 professor page.

    Returns:
        professors (list[dict]): A list of dictionaries, each containing:
            - name (str): The professor's full name.
            - phone (str): The professor's phone number used as a unique identifier.
    """

    response = requests.get(FK07_PROFESSOR_URL)
    if not response.ok:
        raise Exception(f"Failed to fetch page: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all sections with class '_contact' which contain professor information
    sections = soup.find_all('div', class_='_contact')

    prof_names = []
    # For each section (representing one professor) extract name and phone number
    for s in sections:
        name_tag = s.find('span', class_='contact_name')
        name = name_tag.get_text(strip=True).replace('\n', ' ') if name_tag else None

        phone_number = None
        for p in s.find_all('p'):
            text = p.get_text()
            # the paragraph containing the phone number starts with 'T +' -> if 'T +' exists in the paragraph we can assume it contains the phone number
            if 'T +' in text:
                # Regex-Search for the phone number:
                # T: fixed Character T (short for "Telefon")
                # \s*: spaces before the number (optional)
                # \+?: optional plus sign (e.g. for international numbers)
                # ([\d\s\-]+): the phone number itself, which can contain digits, spaces, and dashes (stored in group 1)
                match = re.search(r'T\s*\+?([\d\s\-]+)', text)
                # If we found a match, extract the phone number
                if match:
                    number_str = match.group(1)
                    phone_number = re.sub(r'\D', '', number_str)  # remove non-digits - "49 89 123456" -> "4989123456" or "49-89-123456" -> "4989123456"
                break
        
        # add the professor to the list if both name and phone number are found
        if name and phone_number:
            prof_names.append({
                'name': name,
                'phone': phone_number
            })

    # adds extra demo professor for showcasting toxicity prediction
    prof_names.append({
        'name': 'Max Mustermann',
        'phone': '1234'
    })

    return prof_names


def scrape_all_exams():
    """
    Scrapes all exams from the ZPA exam planning page.

    Returns:
        exams (list[dict]): A list of dictionaries containing exam details, including:
            - examName (str): Name of the exam.
            - studyGroups (str): Associated study groups.
            - examiner (str): Name of the examiner.
            - examDate (datetime): Scheduled date and time of the exam.
    """

    response = requests.get(ZPA_PUBLIC_URL + "exam_plan/")
    if not response.ok:
        raise Exception(f"Failed to fetch page: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')    

    exam_form = soup.find('form', {'id': 'form_exam_plan'})
    h2 = exam_form.find('h2')

    if h2 and 'Die Prüfungsplanung' in h2.text and 'ist noch nicht abgeschlossen' in h2.text:
        return []
    else:
        exams = []

        # Locate the HTML table containing exam information
        exam_table = exam_form.find('table')
        exam_table_body = exam_table.find('tbody')
        # Each top-level row corresponds to one exam entry
        for row in exam_table_body.find_all('tr'):
            cells = row.find_all('td')

            # Rows with fewer than 5 cells usually belong to nested tables (e.g. room details)
            # -> Skip these rows as they don't represent complete exam data
            if len(cells) < 5:
                continue

            # Extract exam details from the relevant columns
            exam_name = cells[1].get_text(strip=True)
            study_groups = cells[2].get_text(strip=True)
            examiner = cells[3].get_text(strip=True)
            exam_date = cells[4].get_text(strip=True)

            # Convert the exam date string to a datetime object
            extracted_date = extract_exam_date(exam_date)

            exams.append({
                    'examName': exam_name,
                    'studyGroups': study_groups,
                    'examiner': examiner,
                    'examDate': extracted_date
                })

        return exams
