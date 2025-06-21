import { Dayjs } from 'dayjs';

export type MyEvent = {
    id?: string;
    module: string;
    room: string;
    format: string;
    start: Date;
    end: Date;
};

export type ModuleEntry = {
    module: string;
    grade: string;
    ects: string;
};

export type TranscriptResult = {
    modules: ModuleEntry[];
    ects_total: string;
    average_grade: string;
};

export type StudyGroup = {
    value: string;
    label: string;
}

export type Lecture = {
    format: string;
    room: string;
    time: string;
    title: string;
    weekday: string;
}

export type Registration = {
    firstName: string;
    lastName: string;
    email: string;
    password: string;
    studyGroupId: string;
    studyGroup: string;
}

export type HomePageInformation = {
    firstName: string;
    averageGrade: string;
    totalCredits: string;
    lectures: Lecture[];
    modules: ModuleEntry[];
    exams: Exam[];
}

export type ProfessorRating = {
    profName?: string,
    profKey?: string,
    id?: number,
    stars: number,
    comment: string
}

export type ProfessorOverview = {
    averageStars: number,
    ratings: ProfessorRating[]
}

export type Exam = {
    examName: string,
    studyGroups: string
    examiner: string,
    examDate: Dayjs | null
}
