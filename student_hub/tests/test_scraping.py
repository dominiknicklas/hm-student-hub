import pytest
from bs4 import BeautifulSoup
from student_hub.scraping import scrape_all_study_groups, scrape_all_professors, scrape_course_plan_for_group, scrape_all_exams

def test_scrape_all_study_groups(mocker):
    html = '''
    <select id="id_group">
        <option value="wt1">WT1</option>
        <option value="wt2">WT2</option>
    </select>
    '''

    mock_response = mocker.Mock()
    mock_response.ok = True
    mock_response.text = html

    mocker.patch("student_hub.scraping.requests.get", return_value=mock_response)

    result = scrape_all_study_groups()
    assert result == [{'value': 'wt1', 'label': 'WT1'}, {'value': 'wt2', 'label': 'WT2'}]

def test_scrape_all_professors(mocker):
    html = '''
    <div class="_contact">
        <span class="contact_name">Prof. Dr. Test</span>
        <p>T +49 89 123456</p>
    </div>
    '''

    mock_response = mocker.Mock()
    mock_response.ok = True
    mock_response.text = html

    mocker.patch("student_hub.scraping.requests.get", return_value=mock_response)

    result = scrape_all_professors()

    assert {'name': 'Prof. Dr. Test', 'phone': '4989123456'} in result
    assert {'name': 'Max Mustermann', 'phone': '1234'} in result # since he gets added for demo purposes


# todo verbessern
def test_scrape_course_plan_for_group(mocker):
    # 1. Fake session and token response
    get_mock = mocker.Mock()
    get_mock.ok = True
    get_mock.text = '''
        <html><input name="csrfmiddlewaretoken" value="fake_token"/></html>
    '''

    # 2. Fake post response with HTML content
    post_mock = mocker.Mock()
    post_mock.ok = True
    post_mock.text = '<html>Lecture Data</html>'

    # 3. Session mock
    session_mock = mocker.Mock()
    session_mock.get.return_value = get_mock
    session_mock.post.return_value = post_mock

    # Patch requests.Session to return your fake session
    mocker.patch("student_hub.scraping.requests.Session", return_value=session_mock)

    # Patch helper function to just check HTML input
    mock_extract = mocker.patch("student_hub.scraping.extract_lectures_from_html", return_value=["Lecture1"])

    result = scrape_course_plan_for_group("wt1")

    assert result == ["Lecture1"]
    mock_extract.assert_called_once_with('<html>Lecture Data</html>')

def test_scrape_all_exams(mocker):
    # 1. Fake HTML für den Fall, dass Prüfungsplanung abgeschlossen ist
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

    # 2. Fake `extract_exam_date()` Rückgabe
    mocker.patch("student_hub.scraping.extract_exam_date", return_value="2025-07-21T16:00:00")

    # 3. Erstelle eine gefälschte Session mit .get() → Rückgabeobjekt
    mock_response = mocker.Mock()
    mock_response.ok = True
    mock_response.text = html

    session_mock = mocker.Mock()
    session_mock.get.return_value = mock_response

    mocker.patch("student_hub.scraping.requests.Session", return_value=session_mock)

    # 4. Importiere die Methode unter Test
    result = scrape_all_exams()

    assert result == [{
        'examName': 'Algorithmen und Datenstrukturen',
        'studyGroups': 'WT4A',
        'examiner': 'Prof. Dr. Test (FK07)',
        'examDate': '2025-07-21T16:00:00'
    }]

def test_scrape_all_exams_when_planning_not_finished(mocker):
    html = '''
    <form id="form_exam_plan">
        <h2>Die Prüfungsplanung ist noch nicht abgeschlossen</h2>
    </form>
    '''

    mock_response = mocker.Mock()
    mock_response.ok = True
    mock_response.text = html

    session_mock = mocker.Mock()
    session_mock.get.return_value = mock_response

    mocker.patch("student_hub.scraping.requests.Session", return_value=session_mock)

    result = scrape_all_exams()

    assert result == []