import axios from 'axios';
import type {
    Exam,
    HomePageInformation,
    Lecture, ProfessorOverview, ProfessorRating,
    Registration,
    StudyGroup,
} from "./types.ts";

const apiClient = axios.create({
    baseURL: 'http://localhost:8000',
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json'
    }
});

const apiService = {
    uploadTranscript: async (email: string, file: File) => {
        const formData = new FormData();
        formData.append('file', file);

        const response = await apiClient.post(`/transcript?email=${email}`, formData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
                withCredentials: true,
            })
        return response.data
    },

    getStudyGroups: async (): Promise<StudyGroup[]> => {
        const response = await apiClient.get('/studygroups')
        return response.data
    },

    getTimetable: async (studyGroup: string): Promise<Lecture[]> => {
        const response = await apiClient.get(`/timetable?group_id=${studyGroup}`)
        return response.data
    },

    getProfessorNames: async (): Promise<{name: string, phone: string}[]> => {
        const response = await apiClient.get('/prof-names')
        return response.data
    },

    createAccount: async (accountData: Registration) => {
        await apiClient.post('/account', accountData)
    },

    login: async (accountData: {email: string, password: string}) => {
        await apiClient.post('/login', accountData)
    },

    updateLectures: async (email: string, lectures: Lecture[]) => {
        await apiClient.post(`/timetable?email=${email}`, lectures)
    },

    getHomepageInformation: async (email: string): Promise<HomePageInformation> => {
        const response = await apiClient.get(`/account?email=${email}`)
        return response.data
    },

    getExams: async (email: string): Promise<Exam[]> => {
        const response = await apiClient.get(`/exams?email=${email}`)
        return response.data
    },

    updateExams: async (email: string, exams: Exam[]) => {
        await apiClient.post(`/exams?email=${email}`, exams)
    },

    updateStudyGroup: async(email: string, newStudyGroupId: string, newStudyGroup: string, lectures: Lecture[]) => {
        await apiClient.post(`/studygroups?email=${email}&new_study_group_id=${newStudyGroupId}&new_study_group=${newStudyGroup}`, lectures)
    },

    submitRating: async(email: string, rating: ProfessorRating) => {
        await apiClient.post(`/rating?email=${email}`, rating)
    },

    getRatings: async (profId: string): Promise<ProfessorOverview> => {
        const response = await apiClient.get(`/rating?prof_id=${profId}`)
        return response.data
    }
}

export default apiService;

