import Box from "@mui/material/Box";
import Navbar from "../components/Navbar.tsx";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import {useNavigate} from "react-router-dom";

export default function AccessDenied() {
    const navigate = useNavigate();

    return (
        <Box>
            <Navbar/>
            <Box
                display="flex"
                flexDirection="column"
                justifyContent="center"
                alignItems="center"
                textAlign="center"
                minHeight="100vh"
            >
                <Typography variant="h5" fontWeight="900" sx={{ marginBottom: '5px'}}>
                    Du musst angemeldet sein um auf diesen Content zuzugreifen!
                </Typography>
                <Box
                    display="flex"
                    justifyContent="center"
                >
                    <Button variant="contained"
                            onClick={() => navigate('/')}
                    >
                        Startseite
                    </Button>
                </Box>
            </Box>
        </Box>
    )
}