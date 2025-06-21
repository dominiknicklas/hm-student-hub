import { Box, Typography } from '@mui/material';

const Footer = () => {
    return (
        <Box
            component="footer"
            sx={{
                width: '100%',
                padding: '1rem',
                marginTop: 'auto',
                textAlign: 'center',
                backgroundColor: '#f5f5f5',
                borderTop: '1px solid #ddd',
            }}
        >
            <Typography variant="body2" color="text.secondary">
                Dominik Nicklas – Informationssysteme II – Modularbeit
            </Typography>
        </Box>
    );
};

export default Footer;
