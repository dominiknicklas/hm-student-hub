import React, {type ReactNode, useEffect, useState} from "react";
import { Gauge } from '@mui/x-charts/Gauge';
import { WeekCalendar } from '../components/WeekCalendar.tsx';
import type {Exam, Lecture, ModuleEntry, MyEvent, StudyGroup} from '../types.ts';
import Navbar from "../components/Navbar.tsx";
import Toolbar from "@mui/material/Toolbar";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Footer from "../components/Footer.tsx";
import CachedIcon from '@mui/icons-material/Cached';
import dayjs, { Dayjs } from 'dayjs';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone'; 
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { de } from 'date-fns/locale';

import {
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle,
    Grid, IconButton, List, ListItem, MenuItem,
    Paper, Select,
    TextField,
    ToggleButton,
    ToggleButtonGroup
} from "@mui/material";
import profBackground from '../../public/background_prof.png'
import GradesTable from "../components/GradeGrid.tsx";
import ProfSearch from "../components/ProfSearch.tsx";
import apiService from "../apiService.ts";
import sortLecturesByTime, {convertLecturesToEvents} from "../utils.ts";
import {useNavigate} from "react-router-dom";
import PdfUploader from "../components/PdfUploader.tsx";
import DeleteIcon from "@mui/icons-material/Delete";

const Item = ({ children, height }: { children: ReactNode; height: number }) => (
    <Paper sx={{ p: 2, textAlign: 'center', height }}>{children}</Paper>
);

export const Home = () => {
    const [events, setEvents] = useState<MyEvent[]>([]);
    const [grades, setGrades] = useState<ModuleEntry[]>([])
    const [firstName, setFirstName] = useState<string>('')
    const [averageGrade, setAverageGrade] = useState<string>('')
    const [totalCredits, setTotalCredits] = useState<string>('0')
    const [alignment, setAlignment] = useState('exam');
    const navigate = useNavigate();
    const [transcriptUpload, setTranscriptUpload] = React.useState(false);
    const [studyGroupUpdate, setStudyGroupUpdate] = React.useState(false);
    const [newTranscript, setNewTranscript] = useState<File | null>(null);
    const [email, setEmail] = useState<string | null>(null)
    const [studyGroups, setStudyGroups] = useState<StudyGroup[] | null>(null);
    const [selectedStudyGroup, setSelectedStudyGroup] = useState('')
    const [lectures, setLectures] = useState<Lecture[]>([]);
    const [exams, setExams] = useState<Exam[]>([]);
    const [examSelector, setExamSelector] = useState(false);
    const [manualExams, setManualExams] = useState<Exam[]>([]);
    const [isFormValid, setIsFormValid] = useState(true);

    dayjs.extend(utc);
    dayjs.locale('de');
    dayjs.extend(timezone);
   

    const handleTranscriptUploadClickOpen = () => {
        setTranscriptUpload(true);
    };

    const handleTranscriptUploadClose = () => {
        setTranscriptUpload(false);
    };

    const handleStudyGroupUpdateClickOpen = async () => {
        setStudyGroupUpdate(true);
        fetchStudyGroups()
    };

    const handleStudyGroupUpdateClose = () => {
        setStudyGroupUpdate(false);
        setSelectedStudyGroup('')
        setLectures([])
    };

    async function fetchStudyGroups() {
        const data = await apiService.getStudyGroups();
        setStudyGroups(data)
    }

    const getTimetable = async (value: string) => {
        const data = await apiService.getTimetable(value);
        const sortedLectures = sortLecturesByTime(data);
        console.log(sortedLectures)
        setLectures(sortedLectures)
    }

    const handleDelete = (indexToDelete: number) => {
        setLectures(prev => prev.filter((_, i) => i !== indexToDelete));
    };

    const handleNewTranscriptUpload = async () => {
        if (!newTranscript) return alert("Bitte PDF auswählen");

        try {
            await apiService.uploadTranscript(email ?? '', newTranscript);
        } catch (e) {
            alert("Fehler beim Upload" + e);
        }
        fetchAccountData(email ?? '')
        setTranscriptUpload(false)
        setNewTranscript(null)
    };

    const handleStudyGroupUpdate = async () => {
        await apiService.updateStudyGroup(email ?? '', selectedStudyGroup, studyGroups?.find(group => group.value === selectedStudyGroup)?.label || '', lectures)
        setExams([])
        fetchAccountData(email ?? '')
        setStudyGroupUpdate(false)
        setSelectedStudyGroup('')
        setLectures([])
    }

    useEffect(() => {
        const email =  localStorage.getItem('email');
        if (email == null) navigate('/')
        setEmail(email)
        fetchAccountData(email ?? '')

        window.scrollTo({ top: 0, behavior: 'auto' });
    }, []);

    async function fetchAccountData(email: string) {
        const accountInformation = await apiService.getHomepageInformation(email);
        setGrades(accountInformation.modules)
        setEvents(convertLecturesToEvents(accountInformation.lectures))
        setFirstName(accountInformation.firstName)
        setAverageGrade(accountInformation.averageGrade)
        setTotalCredits(accountInformation.totalCredits)
        const dayjsExams = accountInformation.exams.map(exam => ({
            ...exam,
            examDate: dayjs(exam.examDate)  // ensure it's a Dayjs instance
        }));
        const sortedExams = dayjsExams.sort((a, b) => a.examDate.valueOf() - b.examDate.valueOf());
        setExams(sortedExams)
    }

    const handleChange = (_: React.MouseEvent<HTMLElement>, newAlignment: string) => {
        if (newAlignment === null) {
            return;
        }
        setAlignment(newAlignment);
    };

    async function selectNewStudygroup(value: string) {
        setSelectedStudyGroup(value)
        await getTimetable(value)
    }

    const downloadCalendar = async () => {
        const response = await fetch(`http://localhost:8000/export/calendar?email=${email}`);

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        const link = document.createElement("a");
        link.href = url;
        link.download = "university_timetable.ics";
        document.body.appendChild(link);
        link.click();
        link.remove();
    };

    const loadExams = async () => {
        const data = await apiService.getExams(email ?? '');
        // @ts-ignore
        const sortedExams = data.sort((a, b) => a.examDate.valueOf() - b.examDate.valueOf());
        setExams(sortedExams)
        setExamSelector(true);
    };

    const handleDeleteExam = (indexToDelete: number) => {
        setExams(prev => prev.filter((_, i) => i !== indexToDelete));
    };

    const handleExamSelectorSubmit = async () => {
        const allExams = [...exams, ...manualExams];
        // @ts-ignore
        const sortedExams = allExams.sort((a, b) => a.examDate.valueOf() - b.examDate.valueOf());
        setExams(sortedExams);
        await apiService.updateExams(email ?? '', allExams);
        setExamSelector(false);
    };

    const handleExamSelectorClose = () => {
        setExamSelector(false);
        setManualExams([]);
        setExams(prev => [...prev])
    };

    useEffect(() => {
        const allValid = manualExams.every(
            (e) =>
            e.examName.trim() !== '' &&
            e.examiner.trim() !== '' &&
            e.examDate !== null &&
            dayjs(e.examDate).isValid()
        );
        setIsFormValid(allValid);
    }, [manualExams]);

    const handleAddManualExam = () => {
        setManualExams([
            ...manualExams,
            { examName: '', examiner: '', studyGroups: '', examDate: dayjs() },
        ]);
    };

    const handleManualExamChange = (
        index: number,
        field: keyof Exam,
        value: string | Dayjs | null
        ) => {
        const updated = [...manualExams];
        updated[index][field] = value as never;
        setManualExams(updated);
    };

    const handleDeleteManualExam = (index: number) => {
        const updated = [...manualExams];
        updated.splice(index, 1);
        setManualExams(updated);
    };

    return (
        <Box>
            <Navbar handleTranscriptUpdate={handleTranscriptUploadClickOpen} handleStudyGroupUpdate={handleStudyGroupUpdateClickOpen}/>
            <Toolbar />
            <Box sx={{ padding: '1rem' }}>
                <h1 style={{marginBottom: '-0.5rem'}}>Willkommen {firstName}</h1>

                <Box sx={{ flexGrow: 1, paddingTop: 2 }}>
                    <Grid container spacing={2}>
                        {/* Linke Spalte mit Kachel 1 und 2 in eigener Column */}
                        <Grid container direction="column" spacing={2} size={4}>
                            <Grid>
                                <Item height={326}>
                                    <Box style={{display: "column"}}>
                                        <Typography variant="h5" fontWeight="bold">Studienfortschritt</Typography>
                                        <Box style={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
                                            <Gauge
                                                value={Number(totalCredits)}
                                                startAngle={-110}
                                                endAngle={110}
                                                valueMax={210}
                                                sx={{
                                                    height: 200,
                                                    '& .MuiGauge-valueText': {
                                                        fontSize: '1.5rem',
                                                    },
                                                }}
                                                text={({value}) => `${value} / 210 ECTS`}
                                            />
                                            <Typography sx={{fontSize: '1.5rem', marginTop: 1}}>
                                                Note: {averageGrade}
                                            </Typography>
                                        </Box>
                                    </Box>
                                </Item>
                            </Grid>
                            <Grid>
                                <Item height={526}>
                                    <ToggleButtonGroup
                                        color="primary"
                                        value={alignment}
                                        exclusive
                                        onChange={handleChange}
                                        aria-label="Platform"
                                        sx={{
                                            display: 'flex',
                                            width: '100%'
                                        }}
                                    >
                                        <ToggleButton
                                            value="exam"
                                            sx={{ flex: 1, textTransform: 'none' }}
                                        >
                                            Prüfungstermine
                                        </ToggleButton>
                                        <ToggleButton
                                            value="grades"
                                            sx={{ flex: 1, textTransform: 'none' }}
                                        >
                                            Alle Noten
                                        </ToggleButton>
                                    </ToggleButtonGroup>

                                    {alignment === 'exam' && 
                                        <Box>
                                            {exams.length === 0 && 
                                                <Box
                                                    sx={{
                                                        textAlign: 'center',
                                                        marginTop: '40px',
                                                        cursor: 'pointer',      
                                                        userSelect: 'none',     
                                                    }}
                                                    onClick={() => loadExams()}
                                                    >
                                                    <CachedIcon fontSize="large" />
                                                    <Typography variant="body1" color="textSecondary">
                                                        Prüfungstermine suchen
                                                    </Typography>
                                                </Box>
                                            }
                                            {exams.length > 0 && 
                                                <Box sx={{ maxHeight: '400px', overflowY: 'auto', mt: 2 }}>
                                                    <List>
                                                        {exams.map((exam, index) => {
                                                            const now = dayjs().tz('Europe/Berlin').startOf('day');
                                                            const examDate = dayjs(exam.examDate).tz('Europe/Berlin').startOf('day');
                                                            const daysDiff = examDate.diff(now, 'day'); // can be negative

                                                            const relativeText =
                                                                daysDiff > 0
                                                                    ? `in ${daysDiff} Tagen`
                                                                    : daysDiff === 0
                                                                    ? `Heute`
                                                                    : `vor ${Math.abs(daysDiff)} Tagen`;

                                                            return (
                                                                <ListItem
                                                                    key={index}
                                                                    sx={{
                                                                        display: 'flex',
                                                                        flexDirection: 'row',
                                                                        alignItems: 'center',
                                                                        border: '1px solid #ccc',
                                                                        borderRadius: 2,
                                                                        mb: 1.5,
                                                                        p: 1.5,
                                                                    }}
                                                                >
                                                                    {/* Left 2/3: Exam info */}
                                                                    <Box sx={{ flex: 2 }}>
                                                                        <Typography variant="subtitle1" fontWeight="bold">
                                                                            {exam.examName}
                                                                        </Typography>
                                                                        <Typography variant="body2" color="text.secondary">
                                                                            {exam.examiner}
                                                                        </Typography>
                                                                        <Typography variant="body2" color="text.secondary">
                                                                            {dayjs(exam.examDate).tz('Europe/Berlin').format('DD.MM.YYYY, HH:mm')}                                                                
                                                                        </Typography>   
                                                                    </Box>

                                                                    {/* Right 1/3: Days until exam */}
                                                                    <Box sx={{ flex: 1, textAlign: 'right' }}>
                                                                        <Typography variant="body1" fontWeight="bold">
                                                                            {relativeText}
                                                                        </Typography>
                                                                    </Box>
                                                                </ListItem>
                                                            );
                                                        })}
                                                    </List>

                                                    <Box
                                                        sx={{
                                                            textAlign: 'center',
                                                            cursor: 'pointer',      
                                                            userSelect: 'none',     
                                                        }}
                                                        onClick={() => loadExams()}
                                                        >
                                                        <CachedIcon fontSize="large" />
                                                        <Typography variant="body1" color="textSecondary">
                                                            Prüfungstermine aktualisieren
                                                        </Typography>
                                                </Box>
                                                </Box>
                                            }
                                        </Box>
                                    }

                                    {alignment === 'grades' && <GradesTable modules={grades}/>}

                                </Item>
                            </Grid>
                        </Grid>

                        {/* Rechte Spalte: großes Feld */}
                        <Grid size={8}>
                            <Item height={870}>
                                <WeekCalendar myEvents={events} downloadCalendar={downloadCalendar}/>
                            </Item>
                        </Grid>

                        {/* Unteres großes Feld */}
                        <Grid size={12}>
                            <Item height={500}>

                                <Box style={{
                                    backgroundImage: `url(${profBackground})`,
                                    backgroundSize: 'cover',
                                    backgroundPosition: 'center',
                                    height: '100%',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    width: '100%'
                                }}>

                                    <Box sx={{textAlign: 'center'}}>
                                        <Typography variant="h5" fontWeight="bold" marginBottom="10px">Professor bewerten</Typography>
                                        <ProfSearch/>
                                    </Box>
                                </Box>
                            </Item>

                        </Grid>
                    </Grid>
                </Box>
            </Box>
            <Footer />

            {/* Notenblatt aktualisieren */}
            <Dialog
                open={transcriptUpload}
                onClose={handleTranscriptUploadClose}
            >
                <DialogTitle>Neues Notenblatt hochladen</DialogTitle>
                <DialogContent>
                    <DialogContentText sx={{ marginBottom: '15px' }}>
                        Die aktuellen Informationen bezüglich des Studienfortschrittes und der Noten werden vollständig durch das
                        neu hochgeladene Notenblatt ersetzt.
                    </DialogContentText>
                    <PdfUploader
                        selectedFile={newTranscript}
                        onFileSelect={(file) => setNewTranscript(file)}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleTranscriptUploadClose}>Abbrechen</Button>
                    <Button type="submit" onClick={handleNewTranscriptUpload}>Hochladen</Button>
                </DialogActions>
            </Dialog>

            {/* Studiengruppe aktualisieren */}
            <Dialog
                open={studyGroupUpdate}
                onClose={handleStudyGroupUpdateClose}
            >
                <DialogTitle>Studiengruppe und Stundenplan aktualisieren</DialogTitle>
                <DialogContent>
                    <Box>
                        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                            <Typography fontWeight="bold">Neue Studiengruppe wählen:</Typography>
                            <Select
                                labelId="study-group-label"
                                value={selectedStudyGroup}
                                onChange={(e) => selectNewStudygroup(e.target.value)}
                                sx={{ width: '100px' }}
                            >
                                {studyGroups?.map((group) => (
                                    <MenuItem key={group.value} value={group.value}>
                                        {group.label}
                                    </MenuItem>
                                ))}
                            </Select>
                        </Box>
                        {lectures.length >= 1 && <Box maxWidth="sm" sx={{marginTop: "40px", justifyContent: 'center', alignItems: 'center'}}>
                        <Typography fontWeight="bold" sx={{ mb: 2, textAlign: 'center' }}>Löschen sie die Vorlesungen aus ihrer neuen Studiengruppe die sie nicht belegen</Typography>
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
                        </Box>}
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleStudyGroupUpdateClose}>Abbrechen</Button>
                    <Button type="submit" disabled={selectedStudyGroup === '' || lectures.length === 0} onClick={handleStudyGroupUpdate}>Aktualisieren</Button>
                </DialogActions>
            </Dialog>

            {/* Prüfungstermine Dialog */}
            <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={de}>
                <Dialog
                open={examSelector}
                onClose={handleExamSelectorClose}
                
                >
                    <DialogTitle>Prüfungstermine</DialogTitle>
                    <DialogContent>
                        <Box>
                            {exams.length === 0 && (
                                <Typography sx={{ textAlign: 'center', marginTop: '20px' }}>
                                    Keine Prüfungen gefunden – die Prüfungstermine wurden noch nicht veröffentlicht oder für Ihre Studiengruppe existieren keine Prüfungstermine.
                                </Typography>
                            )}
                            {exams.length >= 1 && (
                                <Box maxWidth="sm" sx={{ marginTop: "40px" }}>
                                    <Typography fontWeight="bold" sx={{ mb: 2, textAlign: 'center' }}>
                                        Folgende Prüfungen wurden für Ihre Studiengruppe gefunden – löschen Sie die Prüfungen, an denen Sie nicht teilnehmen.
                                    </Typography>
                                    <List>
                                        {exams.map((exam, index) => (
                                            <ListItem key={index} sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', border: '1px solid #ccc', borderRadius: 2, mb: 2, p: 2, position: 'relative' }}>
                                                <IconButton onClick={() => handleDeleteExam(index)} sx={{ position: 'absolute', right: 8, top: 8 }}>
                                                    <DeleteIcon color="error" />
                                                </IconButton>
                                                <Typography variant="subtitle1" fontWeight="bold">
                                                    {exam.examName}
                                                </Typography>
                                                <Typography variant="body2" color="text.secondary">
                                                    {exam.examiner} -- {dayjs(exam.examDate).tz('Europe/Berlin').format('DD.MM.YYYY, HH:mm')}
                                                </Typography>
                                            </ListItem>
                                        ))}
                                    </List>
                                </Box>
                            )}

                            {manualExams.map((manual, index) => (
                                <Box key={index} sx={{ mt: 2, mb: 2, p: 2, border: '1px dashed grey', borderRadius: 2, position: 'relative' }}>
                                    <IconButton onClick={() => handleDeleteManualExam(index)} sx={{ position: 'absolute', right: 8, top: 8 }}>
                                        <DeleteIcon color="error" />
                                    </IconButton>
                                    <Typography variant="subtitle1" fontWeight="bold">
                                        Manuell hinzugefügter Termin
                                    </Typography>
                                    <TextField
                                        fullWidth
                                        label="Prüfungsname"
                                        value={manual.examName}
                                        onChange={(e) => handleManualExamChange(index, 'examName', e.target.value)}
                                        sx={{ mb: 2, mt: 1.5 }}
                                    />
                                    <TextField
                                        fullWidth
                                        label="Prüfer*in"
                                        value={manual.examiner}
                                        onChange={(e) => handleManualExamChange(index, 'examiner', e.target.value)}
                                        sx={{ mb: 2 }}
                                    />
                                    <DateTimePicker
                                        label="Datum und Uhrzeit"
                                        value={manual.examDate?.toDate() ?? null}
                                        format="dd.MM.yyyy HH:mm"
                                        ampm={false}
                                        onChange={(val) => handleManualExamChange(index, 'examDate', dayjs(val))}
                                        slotProps={{ textField: { fullWidth: true } }}
                                    />
                                </Box>
                            ))}

                            <Button fullWidth variant="outlined" onClick={handleAddManualExam}>
                                Leistungstermin manuell hinzufügen
                            </Button>
                        </Box>
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={handleExamSelectorClose}>
                            Abbrechen
                        </Button>
                        <Button onClick={handleExamSelectorSubmit} disabled={!isFormValid}>
                            Fertig
                        </Button>
                    </DialogActions>
                </Dialog>
            </LocalizationProvider>
        </Box>
    );
};

export default Home;