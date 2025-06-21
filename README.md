# Student Hub FK07

## 🎓 Purpose of the Application

**Student Hub FK07** is a fullstack information system for students of the Computer Science and Mathematics faculty (FK07) at Hochschule München. It's developed using a React + TypeScript frontend, a Python backend (FastAPI), and an SQLite database.

The application allows students to:
- Register a personal profile
- Upload their official transcript of records
- Automatically extract and visualize academic data (grades, average grade, ECTS, etc.)
- Retrieve and display their current timetable based on their study group
- Update their study group and academic record to reflect the current semester
- Rate professors of the faculty -> therefore a self-trained machine learning model is used to detect toxic language in professor reviews, allowing only respectful feedback to be published.

To ensure up-to-date information, the system scrapes data from the public pages of the [ZPA](https://zpa.cs.hm.edu/public/) and [FK07 professor page](https://cs.hm.edu/fakultaet/personen/professuren.de.html) to fetch:
- Available study groups
- All lectures of a particular study group
- Professor details




## 🚀 How to Start the Application

You can run the application locally in two ways:

### Option 1: Manually
Start a terminal window in the root folder of the project

```bash
# 1. Backend setup
cd student_hub
pip install -r requirements.txt
python3 main.py

# 2. Frontend setup 
cd ../student_hub_frontend
npm install
npm run dev
```

### Option 2: with Docker
Start a terminal window in the root folder of the project and insure that the docker engine is running

Execute: `docker compose up --build`

This will automaticly start the pyhton 'backend' and react frontend in containers


## 🖥️ How to use the Application
### Accessing the Application

- When the app is running, open your browser and go to: [http://localhost:5173](http://localhost:5173)
- You will land on the welcome screen where you can log in or register.

**Registration:**
1. Enter personal information  
2. Upload a valid official transcript of records (PDF)  
3. Select the courses you are currently attending (fetched based on your selected study group)


### Features After Logging In

- View your academic progress: Grades, Average grade, Total ECTS (study progress)
- View and download your personal timetable (importable into calendar apps)
- Update your transcript and study group information
- Search for professors and submit reviews


### Professor Review System

- Search for a professor to visit their profile page (all professors of the FK07 are available + "Max Mustermann" for testing purposes)
- View existing reviews for the selected professor from other students
- Submit your own review and rating
  - A machine learning model checks the text for toxicity - Toxic comments will be rejected and not published
