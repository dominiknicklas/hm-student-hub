import Box from "@mui/material/Box";
import Toolbar from "@mui/material/Toolbar";
import {Button, Container, FormControl, IconButton, InputLabel, MenuItem, Select, TextField, List, ListItem} from "@mui/material";
import DeleteIcon from '@mui/icons-material/Delete';
import Typography from "@mui/material/Typography";
import React, {useEffect, useState} from "react";
import Navbar from "../components/Navbar.tsx";
import PdfUploader from "../components/PdfUploader.tsx";
import type {Lecture, Registration, StudyGroup} from "../types.ts";
import apiService from "../apiService.ts";
import Footer from "../components/Footer.tsx";
import {useNavigate} from "react-router-dom";
import type {AxiosError} from "axios";
import sortLecturesByTime from "../utils.ts";

export default function Startup() {
    const [registrationFormData, setRegistrationFormData] = useState({
        firstName: '',
        lastName: '',
        email: '',
        password: '',
        studyGroupId: '',
        transcript: null as File | null,
    });
    const [loginFormData, setLoginFormData] = useState({
        email: '',
        password: ''
    })
    const [studyGroups, setStudyGroups] = useState<StudyGroup[] | null>(null);
    const [lectures, setLectures] = useState<Lecture[]>([]);
    const [secondPage, setSecondPage] = useState(false);
    const navigate = useNavigate();
    const [loginErrorMessage, setLoginErrorMessage] = useState<string | null>(null)
    const [registrationErrorMessage, setRegistrationErrorMessage] = useState<string | null>(null)
    const [transcriptError, setTranscriptError] = useState<boolean>(false)
    const [transcriptUploadError, setTranscriptUploadError] = useState<boolean>(false)

    useEffect(() => {
        async function fetch() {
            const data = await apiService.getStudyGroups();
            setStudyGroups(data)
        }
        fetch()
    }, []);

    const getTimetable = async () => {
        const data = await apiService.getTimetable(registrationFormData.studyGroupId);
        setLectures(sortLecturesByTime(data))
    }

    const createAccount = async () => {
        const registration: Registration = {
            firstName: registrationFormData.firstName,
            lastName: registrationFormData.lastName,
            email: registrationFormData.email,
            password: registrationFormData.password,
            studyGroupId: registrationFormData.studyGroupId,
            studyGroup: studyGroups?.find(group => group.value === registrationFormData.studyGroupId)?.label || '',
        }
        if (!registrationFormData.transcript) {
            setTranscriptError(true);
            return false;
        } else {
            setTranscriptError(false);
        }
        setTranscriptUploadError(false)
        setRegistrationErrorMessage("")

        try {
            await apiService.createAccount(registration, registrationFormData.transcript);
            return true;
        } catch (e) {
            const error = e as AxiosError
            let message = "";
            if (error.response) {
                const code = error.response.status;
                if (code === 400) {
                    message = "Zu der angegebenen E-Mail-Adresse existiert bereits ein Account."
                } else if (code ===422) {
                    setTranscriptUploadError(true)
                } else {
                    message = "Es lief etwas schief."
                }
            }
            setRegistrationErrorMessage(message)
        }
    }

    const handleRegistrationSubmit = async(event: React.FormEvent) => {
        event.preventDefault();
        const success = await createAccount()
        if (success) {
            getTimetable()
            setSecondPage(true)
        }
    }

    const handleLoginSubmit = async (event: React.FormEvent) => {
        event.preventDefault()
        setLoginFormData((prevState) => ({
            ...prevState,
            password: ''
        }))
        try {
            await apiService.login({email: loginFormData.email, password: loginFormData.password})
            localStorage.setItem('email', loginFormData.email)
            navigate('/home')
        } catch (e) {
            const error = e as AxiosError
            let message = "";
            if (error.response) {
                const code = error.response.status;
                if (code === 401) {
                    message = "Email oder Passwort falsch - oder es existiert noch kein Account."
                } else {
                    message = "Es lief etwas schief."
                }
            }
            setLoginErrorMessage(message)
        }
    }

    const handleDelete = (indexToDelete: number) => {
        setLectures(prev => prev.filter((_, i) => i !== indexToDelete));
    };

    const completeConfiguration = () => {
        localStorage.setItem('email', registrationFormData.email)
        //handleUpload()
        apiService.updateLectures(registrationFormData.email, lectures)
        navigate('/home')
    }

    return (
        <Box sx={{ display: "flex", flexDirection: "column", minHeight: '100vh' }}>
            <Navbar/>
            <Toolbar/>
            <Typography variant="h3" textAlign="center" sx={{marginTop: "40px"}}>Willkommen beim Studentenhub</Typography>
            {!secondPage && <Container sx={{marginTop: "40px"}}>
                <Box
                    display="flex"
                    flexDirection={{ xs: "column", md: "row" }}
                    gap={{ xs: 4, md: 15}}
                    >
                    {/* Registrierung - 2/3 */}
                    <Box flex={{ md: 2 }}>
                        <Typography variant="h5" gutterBottom textAlign="center">
                            Registrieren
                        </Typography>
                        <Box component="form" onSubmit={handleRegistrationSubmit} display="grid"
                            gridTemplateColumns={{xs: "1fr", sm: "1fr 1fr"}} gap={2}>
                            {/* Vorname und Nachname */}
                            <TextField
                                required
                                fullWidth
                                label="Vorname"
                                value={registrationFormData.firstName}
                                onChange={(e) => setRegistrationFormData(prev => ({...prev, firstName: e.target.value}))}
                            />
                            <TextField
                                required
                                fullWidth
                                label="Nachname"
                                value={registrationFormData.lastName}
                                onChange={(e) => setRegistrationFormData(prev => ({...prev, lastName: e.target.value}))}
                            />

                            {/* E-Mail und Passwort */}
                            <TextField
                                required
                                fullWidth
                                label="HM-E-Mail"
                                type="email"
                                value={registrationFormData.email}
                                onChange={(e) => setRegistrationFormData(prev => ({...prev, email: e.target.value}))}
                            />
                            <TextField
                                required
                                fullWidth
                                label="Passwort"
                                type="password"
                                value={registrationFormData.password}
                                onChange={(e) => setRegistrationFormData(prev => ({...prev, password: e.target.value}))}
                            />

                            {/* Studiengruppe */}
                            <FormControl required fullWidth>
                                <InputLabel id="study-group-label">Studiengruppe</InputLabel>
                                <Select
                                    labelId="study-group-label"
                                    value={registrationFormData.studyGroupId}
                                    label="Studiengruppe"
                                    onChange={(e) =>
                                        setRegistrationFormData((prev) => ({...prev, studyGroupId: e.target.value}))
                                    }
                                >
                                    {studyGroups?.map((group) => (
                                        <MenuItem key={group.value} value={group.value}>
                                            {group.label}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                            {registrationErrorMessage != null && <Box gridColumn={{xs: "span 1", sm: "span 2"}}><Typography color="red">{registrationErrorMessage}</Typography></Box>}

                            {/* Notenblatt Upload */}
                            <Box gridColumn={{sm: "span 2"}}>
                                <Typography>Notenblatt (PDF) hochladen</Typography>
                                <PdfUploader
                                    selectedFile={registrationFormData.transcript}
                                    onFileSelect={(file) => setRegistrationFormData(prev => ({...prev, transcript: file}))}
                                />
                            </Box>
                            {transcriptError && <Box gridColumn={{xs: "span 1", sm: "span 2"}}><Typography color="red">Bitte Notenblatt hochladen</Typography></Box>}
                            {transcriptUploadError && <Box gridColumn={{xs: "span 1", sm: "span 2"}}><Typography color="red">Es scheint als wäre das hochgeladene Notenblatt kein offizielles Notenblatt aus dem Primuss Tool der HM!</Typography></Box>}
                            {/* Submit Button */}
                            <Box gridColumn={{xs: "span 1", sm: "span 2"}}>
                                <Button type="submit" fullWidth variant="contained" color="primary">
                                    Weiter
                                </Button>
                            </Box>
                        </Box>
                    </Box>

                    {/* Login - 1/3 */}
                    <Box flex={{ md: 1 }}>
                        <Typography variant="h5" textAlign="center" gutterBottom marginTop={{sx: '60px'}}>Login</Typography>
                        <Box component="form" onSubmit={handleLoginSubmit} display="grid"
                            gridTemplateColumns={{xs: "1fr", sm: "1fr 1fr", md: "1fr"}} gap={2}>
                            {/* E-Mail und Passwort */}
                            <TextField
                                required
                                fullWidth
                                label="HM-E-Mail"
                                type="email"
                                value={loginFormData.email}
                                onChange={(e) => setLoginFormData(prev => ({...prev, email: e.target.value}))}
                            />
                            <TextField
                                required
                                fullWidth
                                label="Passwort"
                                type="password"
                                value={loginFormData.password}
                                onChange={(e) => setLoginFormData(prev => ({...prev, password: e.target.value}))}
                            />
                            {loginErrorMessage != null && <Box gridColumn={{xs: "span 1", sm: "span 2"}}><Typography color="red">{loginErrorMessage}</Typography></Box>}
                            {/* Submit Button */}
                            <Box gridColumn={{xs: "span 1", sm: "span 2", md: "span 1"}}>
                                <Button type="submit" fullWidth variant="contained" color="primary" sx={{ marginBottom: "15px" }}>
                                    Login
                                </Button>
                            </Box>
                        </Box>
                    </Box>
                </Box>

            </Container>}
            {secondPage && <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                <Box maxWidth="sm" sx={{marginTop: "40px", justifyContent: 'center', alignItems: 'center'}}>
                    <Typography variant="h5" sx={{ mb: 2, textAlign: 'center' }}>Löschen sie die Vorlesungen aus ihrer Studiengruppe die sie nicht belegen</Typography>
                    <List>
                        {lectures?.map((lecture, index) => (
                            <ListItem
                                key={index}
                                sx={{
                                    display: 'flex',
                                    flexDirection: 'column',
                                    alignItems: 'flex-start',
                                    border: '1px solid #ccc',
                                    borderRadius: 2,
                                    mb: 2,
                                    p: 2,
                                    position: 'relative'
                                }}
                            >
                                <IconButton
                                    onClick={() => handleDelete(index)}
                                    sx={{ position: 'absolute', right: 8, top: 8 }}
                                >
                                    <DeleteIcon color="error" />
                                </IconButton>
                                <Typography variant="subtitle1" fontWeight="bold">
                                    {lecture.title} - {lecture.format}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    {lecture.weekday}, {lecture.time}
                                </Typography>
                            </ListItem>
                        ))}
                    </List>
                    <Button fullWidth variant="contained" sx={{ marginBottom: '15px' }} onClick={completeConfiguration}>Abschließen</Button>
                </Box>
            </Box>
            }
            <Footer/>
        </Box>
    );
}