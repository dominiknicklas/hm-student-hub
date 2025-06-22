from fastapi import FastAPI, Query, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import status
from fastapi.responses import StreamingResponse
import pdfplumber
import io
import student_hub.scraping as scraping
import student_hub.profile_storing as profile_storing
import student_hub.rating_storing as rating_storing
from student_hub.util_classes import *
from student_hub.util_functions import extract_data_from_transcript_text, extract_suiting_exams_for_student
from student_hub.predicting import is_toxic, load_model_and_vectorizer
from student_hub.exporting import get_ics_file_for_user_timetable
from student_hub.mailing import find_and_send_exam_reminders
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler to start the scheduler, initialize the db and load ml files when the app starts.
    The Schedular will run the `find_and_send_exam_reminders` function every weekday at 8:00.
    Also, the schedular will run immediately when the app starts.
    """
    load_model_and_vectorizer()  # Load the model and vectorizer for toxicity detection
    profile_storing.initialize_db()  # Ensure the database is initialized
    rating_storing.initialize_db()  # Ensure the database is initialized

    find_and_send_exam_reminders()
    scheduler.add_job(find_and_send_exam_reminders, trigger='cron', hour=8, minute=0, day_of_week='mon-fri')
    scheduler.start()

    yield

    scheduler.shutdown(wait=False)

app = FastAPI(lifespan=lifespan)

# Allow frontend access (from port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Defined endpoints:
@app.post("/account")
async def create_account(registration: Registration):
    try:
        profile_storing.insert_profile(registration.firstName, registration.lastName, registration.email, registration.password, registration.studyGroupId, registration.studyGroup, '', '')
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@app.get("/account")
async def get_account_information(email: str = Query(...)):
    profile_summary = profile_storing.get_profile_summary(email)
    return {
        "firstName": profile_summary["firstname"],
        "averageGrade": profile_summary["average_grade"],
        "totalCredits": profile_summary["total_credits"],
        "lectures": profile_storing.get_lectures_for_profile(email),
        "modules": profile_storing.get_modules_for_profile(email),
        "exams": profile_storing.get_exams_for_profile(email)
    }

@app.post("/login")
async def login(loginData: LoginData):
    profile_storing.check_login_data(loginData)
    if profile_storing.check_login_data(loginData):
        return {"message": "Login successful"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

@app.get("/studygroups")
async def get_studygroups():
    return scraping.scrape_all_study_groups()

@app.post("/studygroups")
async def update_studygroup_for_student(lectures: List[Lecture], email: str = Query(...), new_study_group_id: str = Query(...), new_study_group: str = Query(...)):
    profile_storing.update_study_group(email, new_study_group_id, new_study_group)
    profile_storing.update_timetable(email, lectures)
    profile_storing.clear_exams(email) # to remove exams that are not relevant anymore since the study group has changed

@app.get("/timetable")
async def get_timetable_for_studygroup(group_id: str = Query(...)):
    return scraping.scrape_course_plan_for_group(group_id)

@app.post("/timetable")
async def update_lectures_for_student(lectures: List[Lecture], email: str = Query(...)):
    profile_storing.update_timetable(email, lectures)

@app.post("/transcript")
async def upload_transcript(email: str = Query(...), file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    content = await file.read()

    with pdfplumber.open(io.BytesIO(content)) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

    transcript_information = extract_data_from_transcript_text(text)
    profile_storing.update_study_progress(email, transcript_information["average_grade"], transcript_information["ects_total"])
    profile_storing.update_grades(email, transcript_information["modules"])

@app.post("/exams")
async def update_exams_for_student(exams: List[Exam], email: str = Query(...)):
    profile_storing.update_exams(email, exams)

@app.get("/exams")
async def get_all_exams_for_students_studygroup(email: str = Query(...)):
    all_exams = scraping.scrape_all_exams()
    if len(all_exams) == 0: return all_exams
    exams_for_student = extract_suiting_exams_for_student(all_exams, email)
    return exams_for_student

@app.get("/export/calendar")
async def export_timetable_for_student_ics(email: str = Query(...)):
    calendar = get_ics_file_for_user_timetable(email)
    ics_content = calendar.serialize()

    # Convert to a stream for download
    file_stream = io.StringIO(ics_content)
    response = StreamingResponse(file_stream, media_type="text/calendar")
    response.headers["Content-Disposition"] = "attachment; filename=schedule.ics"
    return response

@app.get("/prof-names")
async def get_all_professor_names():
    return scraping.scrape_all_professors()

@app.post("/rating")
async def rate_professor(rating: Rating, email: str = Query(...)):
    if is_toxic(rating.comment): 
        raise HTTPException(status_code=400, detail="Toxic comment detected.")
    rating_storing.insert_rating(email, rating)

@app.get("/rating")
async def get_all_ratings_for_professor(prof_id: str = Query(...)):
    ratings = rating_storing.get_all_ratings_for_prof(prof_id)
    average_stars = None
    if len(ratings) > 0: average_stars = sum(d["stars"] for d in ratings) / len(ratings)
    return {
        "averageStars": average_stars,
        "ratings": ratings
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("student_hub.main:app", host="0.0.0.0", port=8000, reload=True)
