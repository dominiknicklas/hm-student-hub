import Box from "@mui/material/Box";
import Navbar from "../components/Navbar.tsx";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import {useLocation, useNavigate} from "react-router-dom";
import {useEffect, useState} from "react";
import {
    Button,
    CircularProgress,
    Dialog, DialogActions,
    DialogContent,
    DialogTitle, Divider, List, ListItem, ListItemText, Paper, Rating,
    TextField
} from "@mui/material";
import type {ProfessorRating} from "../types.ts"
import apiService from "../apiService.ts";
import Footer from "../components/Footer.tsx";
import type {AxiosError} from "axios";

export default function Professor() {
    const navigate = useNavigate()
    const location = useLocation()
    const [open, setOpen] = useState(false);
    const [ratingStars, setRatingStars] = useState<number | null>(3)
    const [ratingComment, setRatingComment] = useState('')
    const [ratings, setRatings] = useState<ProfessorRating[]>([])
    const [averageRating, setAverageRating] = useState<number | null>(null)
    const [submitError, setSubmitError] = useState('')

    useEffect(() => {
        if (!location.state) {
            setTimeout(() => {
                navigate("/", { replace: true });
            }, 1500);
        }
    }, [location.state, navigate]);

    useEffect(() => {
        fetchProfessorOverview()
    }, []);

    async function fetchProfessorOverview() {
        const response = await apiService.getRatings(value)
        setAverageRating(response.averageStars)
        setRatings(response.ratings)
    }

    if (!location.state) {
        return (
            <>
                <Navbar />
                <Toolbar/>
                <Box
                    sx={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexDirection: 'column',
                        mt: '64px'
                    }}
                >
                    <CircularProgress color="primary" />
                    <Typography variant="h5" sx={{ mt: 2 }}>
                        Weiterleitung…
                    </Typography>
                    <Typography>Diese Seite kann nur über das Professor-Suchfeld auf dem Dashboard erreicht werden!</Typography>
                </Box>
            </>
        );
    }

    const { label, value } = location.state;

    const handleClickOpen = () => {
        setOpen(true);
    };

    const handleClose = () => {
        setRatingStars(3)
        setRatingComment('')
        setSubmitError('')
        setOpen(false);
    };

    const handleRatingSubmission = async() => {
        const rating: ProfessorRating = {
            profKey: value,
            profName: label,
            stars: Number(ratingStars),
            comment: ratingComment
        }
        try {
            await apiService.submitRating(localStorage.getItem('email') ?? '', rating)
            handleClose()
            fetchProfessorOverview()
        } catch (e) {
            const error = e as AxiosError
            let message = "";
            if (error.response) {
                // @ts-ignore
                if (error.response.status === 400 && error.response.data.detail === "Toxic comment detected.") {
                    message = "Das ML Model hat ihren Kommentar als TOXISCH eingestuft - Bewertung kann so nicht abgegeben werden."
                } else {
                    message = "Es lief etwas schief."
                }
            }
            setSubmitError(message)
        }
    }

    return (
        <Box sx={{ display: "flex", flexDirection: "column", minHeight: '100vh' }}>
            <Navbar/>
            <Toolbar/>
            <Typography sx={{ textAlign: 'center', mt: 2}} variant="h4">Bewertungen für</Typography>
            <Typography sx={{ textAlign: 'center'}} variant="h3">{label}</Typography>
            <Box sx={{ alignItems: 'center', display: 'flex', flexDirection: 'column', mt: 4}}>
                {(averageRating === null && ratings.length === 0) ?
                    (<Typography variant="h5">Bisher gibt es noch keine Bewertungen</Typography>) :
                    (<Box sx={{ alignItems: 'center', display: 'flex', flexDirection: 'column' }}>
                        <Typography component="legend">Durchschnittliche Gesamtbewertung:</Typography>
                        <Rating name="read-only" value={averageRating} precision={0.25} readOnly />
                    </Box>)
                }
                <Button variant="outlined" sx={{ mt: 2 }} onClick={handleClickOpen}>
                    Bewerten
                </Button>
                {(averageRating !== null && ratings.length !== 0) && <Box sx={{ alignItems: 'center', display: 'flex', flexDirection: 'column'}}>
                    <Divider sx={{ width: '100%', my: 2 }} />
                <Typography variant={"h5"}>Alle Bewertungen:</Typography>
                <List>
                    {ratings.map((r, index) => (
                        <ListItem key={index} disableGutters>
                            <Paper
                                elevation={2}
                                sx={{
                                    width: '550px',
                                    p: 2,
                                    mb: 2,
                                }}
                            >
                                <ListItemText
                                    primary={<Rating value={r.stars} readOnly />}
                                    secondary={
                                        <Typography
                                            component="span"
                                            variant="body2"
                                            color="textSecondary"
                                            sx={{ whiteSpace: 'pre-line' }}
                                        >
                                            {r.comment}
                                        </Typography>
                                    }
                                />
                            </Paper>
                        </ListItem>
                    ))}
                </List></Box>}

            </Box>

            <Dialog
                open={open}
                onClose={handleClose}
            >
                <DialogTitle>Bewertung für {label} abgeben</DialogTitle>
                <DialogContent>
                    <Typography component="legend">Gesamtbewertung</Typography>
                    <Rating
                        name="simple-controlled"
                        value={ratingStars}
                        onChange={(_, newValue) => {
                            setRatingStars(newValue);
                        }}
                    />

                    <Typography mt={1.5} component="legend">Hinweis zum Freitext</Typography>
                    <Typography component="legend">Bitte bleiben Sie bei der Bewertung sachlich und respektvoll. Beleidigungen, diskriminierende Aussagen oder unsachliche Kommentare sind nicht erlaubt und werden entfernt. Ihre Rückmeldung soll zur Verbesserung der Lehre beitragen – formulieren Sie daher konstruktiv.</Typography>
                    <TextField
                        id="outlined-multiline-static"
                        label="Kommentar"
                        multiline
                        sx={{ mt: 1 }}
                        rows={4}
                        fullWidth
                        value={ratingComment}
                        onChange={(e) => setRatingComment(e.target.value)}
                        placeholder="Schreiben Sie hier Ihren Kommentar"
                    />
                    {submitError !== '' && <Typography color="red">{submitError}</Typography>}

                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose}>Abbrechen</Button>
                    <Button type="submit" onClick={handleRatingSubmission}>Bewerten</Button>
                </DialogActions>
            </Dialog>
            <Footer/>
        </Box>
    )
}