import pytest
from bs4 import BeautifulSoup
from student_hub.scraping import scrape_all_study_groups, scrape_all_professors, scrape_course_plan_for_group, scrape_all_exams

def test_scrape_all_study_groups(mocker):
    # Fake ZPA HTML snippet with study groups
    html = '''
    <select id="id_group">
        <option value="200">WT2</option>
        <option value="220">WT4</option>
    </select>
    '''

    mock_response = mocker.Mock()
    mock_response.ok = True
    mock_response.text = html

    # Mock the requests.get call to return the fake HTML
    mocker.patch("student_hub.scraping.requests.get", return_value=mock_response)

    # Call the function under test and check the result
    result = scrape_all_study_groups()
    assert result == [{'value': '200', 'label': 'WT2'}, {'value': '220', 'label': 'WT4'}]


def test_scrape_all_professors(mocker):
    # Fake HM Professor HTML snippet with professor information
    html = '''
    <div class="_contact">
        <span class="contact_name">Prof. Dr. Test</span>
        <p>T +49 89 123456</p>
    </div>
    '''

    mock_response = mocker.Mock()
    mock_response.ok = True
    mock_response.text = html

    # Mock the requests.get call to return the fake HTML
    mocker.patch("student_hub.scraping.requests.get", return_value=mock_response)

    # Call the function under test and check the result
    result = scrape_all_professors()
    assert {'name': 'Prof. Dr. Test', 'phone': '4989123456'} in result
    assert {'name': 'Max Mustermann', 'phone': '1234'} in result # since he gets added for demo purposes


# todo verbessern
def test_scrape_course_plan_for_group(mocker):
    # Fake session and token response (ZPA Course Plan page - hidden input)
    get_mock = mocker.Mock()
    get_mock.ok = True
    get_mock.text = '''
        <html><input type="hidden" name="csrfmiddlewaretoken" value="fake_token"/></html>
    '''

    # Fake post response with HTML content (ZPA Course Plan page with lectures for a specific group)
    post_mock = mocker.Mock()
    post_mock.ok = True
    lectures_html = """
        <table>
            <tbody class="plan">
                <tr>
                    <td class="time">10:00</td>
                    <td>
                        LECTURE CONTENT WOULD BE HERE
                    </td>
                    <td></td><td></td><td></td>
                </tr>
            </tbody>
        </table>
    """
    post_mock.text = lectures_html

    # Create a mock session that returns the above mocks for GET and POST requests
    session_mock = mocker.Mock()
    session_mock.get.return_value = get_mock
    session_mock.post.return_value = post_mock

    # Mock the requests.Session to return our mock session
    mocker.patch("student_hub.scraping.requests.Session", return_value=session_mock)

    # Mock the extract_lectures_from_html function to return a dummy list of lectures
    mock_extract = mocker.patch("student_hub.scraping.extract_lectures_from_html", return_value=["LECTURE CONTENT WOULD BE HERE"])

    result = scrape_course_plan_for_group("220")

    assert result == ["LECTURE CONTENT WOULD BE HERE"]
    mock_extract.assert_called_once_with(lectures_html)


def test_scrape_all_exams(mocker):
    # Fake ZPA HTML for the case where exams are available
    html = '''
    <form name="form_exam_plan" id="form_exam_plan">
        <table class="sortable">
            <thead>
                <tr>
                    <th>Nr.</th>
                    <th>Modul</th>
                    <th>Gruppen</th>
                    <th>Prüfer</th>
                    <th>Termin</th>
                </tr>
            </thead>
            <tbody>
                <tr></tr>
                <tr><td>1</td><td>Algorithmen und Datenstrukturen</td><td>WT4A</td><td>Prof. Dr. Test (FK07)</td><td>21.07.2025 16:00</td></tr>
            </tbody>
        </table>
    </form>
    '''

    # Mock the extract_exam_date function to return a fixed date (matching the Exam Date in the HTML)
    mocker.patch("student_hub.scraping.extract_exam_date", return_value="2025-07-21T16:00:00")


    mock_response = mocker.Mock()
    mock_response.ok = True
    mock_response.text = html

    # Mock the requests.get call to return the fake HTML
    mocker.patch("student_hub.scraping.requests.get", return_value=mock_response)

    # Call the function under test and check the result - should return the exam of the HTML
    result = scrape_all_exams()
    assert result == [{
        'examName': 'Algorithmen und Datenstrukturen',
        'studyGroups': 'WT4A',
        'examiner': 'Prof. Dr. Test (FK07)',
        'examDate': '2025-07-21T16:00:00'
    }]


def test_scrape_all_exams_when_planning_not_finished(mocker):
    # Fake ZPA HTML for the case where exam planning is not finished
    html = '''
    <form id="form_exam_plan">
        <h2>Die Prüfungsplanung ist noch nicht abgeschlossen</h2>
    </form>
    '''

    mock_response = mocker.Mock()
    mock_response.ok = True
    mock_response.text = html

    # Mock the requests.get call to return the fake HTML
    mocker.patch("student_hub.scraping.requests.get", return_value=mock_response)

    # Call the function under test and check the result - should return an empty list
    result = scrape_all_exams()
    assert result == []