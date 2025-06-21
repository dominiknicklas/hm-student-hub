import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import CssBaseline from '@mui/material/CssBaseline';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
//import {useNavigate} from "react-router-dom";
import HMLogo from '../../public/Hochschule_Muenchen_Logo.svg.png';
import {Button} from "@mui/material";
import {useLocation, useNavigate} from "react-router-dom";

type NavbarProps = {
    handleTranscriptUpdate?: () => void,
    handleStudyGroupUpdate?: () => void,
}

export default function Navbar({ handleTranscriptUpdate, handleStudyGroupUpdate }: NavbarProps) {

    const navigate = useNavigate()
    const location = useLocation()
    const path = location.pathname

    // function goHome() {
    //     navigate('/');
    // }

    return (
        <Box>
            <Box  style={{ justifyContent: "center"}}>
                <CssBaseline/>
                <AppBar position="fixed"
                        sx={{
                            top: 0,
                            bottom: "auto",
                            height: '64px'
                        }} color="inherit">
                    <Toolbar
                        sx={{
                            height: '100%',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                        }}
                    >
                        {/* Left side: Logo and title */}
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <img
                                src={HMLogo}
                                alt="Logo"
                                style={{ width: 90, height: 45 }}
                            />
                            <Typography
                                variant="h6"
                                component="div"
                                sx={{
                                    color: "#fb5455",
                                    fontSize: '2.5rem',
                                    fontWeight: '500',
                                    marginLeft: 1,
                                    cursor: 'pointer',
                                    transition: 'color 0.3s ease',
                                    '&:hover': {
                                        color: '#fb5455',
                                    }
                                }}
                            >
                                - Studentenhub FK07
                            </Typography>
                        </Box>

                        {/* Right side: Optional buttons */}
                        <Box sx={{ display: 'flex', gap: 1 }}>
                            {path === '/home' && <Box sx={{ display: 'flex', gap: 1 }}><Button
                                variant="outlined"
                                color="primary"
                                onClick={handleStudyGroupUpdate}
                            >
                                Studiengruppe aktualisieren
                            </Button>
                            <Button
                                variant="outlined"
                                color="primary"
                                onClick={handleTranscriptUpdate}
                            >
                                Notenblatt aktualisieren
                            </Button></Box>}
                            {path === '/professor' && <Button
                                variant="outlined"
                                color="primary"
                                onClick={() => navigate('/home')}
                            >
                                Dashboard
                            </Button>}
                            {path !== '/' && <Button
                                variant="contained"
                                color="error"
                                onClick={() => {
                                    navigate('/')
                                    localStorage.removeItem('email')
                                }}
                            >
                                Logout
                            </Button>}
                        </Box>
                    </Toolbar>


                </AppBar>
            </Box>
        </Box>
    );
}