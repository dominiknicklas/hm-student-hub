from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# this data models are used in the FastAPI endpoints and represent the data which is sent by the frontend

class Lecture(BaseModel):
    id: Optional[str] = None
    format: str
    room: str
    time: str
    title: str
    weekday: str

class Registration(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    password: str
    studyGroupId: str
    studyGroup: str

class LoginData(BaseModel):
    email: EmailStr
    password: str

class Rating(BaseModel):
    profName: str
    profKey: str
    stars: int
    comment: str

class Exam(BaseModel):
    examName: str
    studyGroups: str
    examiner: str
    examDate: datetime
