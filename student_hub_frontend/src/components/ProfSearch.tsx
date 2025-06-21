import React, {useEffect, useState} from 'react';
import {
    Autocomplete,
    TextField,
    IconButton,
    Box,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import apiService from "../apiService.ts";
import Typography from "@mui/material/Typography";
import {useNavigate} from "react-router-dom";

export default function SearchBar() {
    const [selectedOption, setSelectedOption] = React.useState({label: 'Professor Name', value: 'default'});
    const [allProfessors, setAllProfessors] = useState<{label: string, value: string}[]>([]);
    const [error, setError] = useState(false);
    const navigate = useNavigate()

    useEffect(() => {
        async function getProfs() {
            const profs = await apiService.getProfessorNames()
            const options = profs.map(prof => ({
                label: prof.name,
                value: prof.phone
            }));
            setAllProfessors(options)
        }
        getProfs()
    }, []);

    const handleSearch = () => {
        if (selectedOption.label === 'Professor Name') setError(true)
        navigate('/professor', {state: selectedOption})
    };

    return (
        <Box>
            <Box sx={{display: 'flex', alignItems: 'center', gap: 1}}>
            <Autocomplete
                disablePortal
                disableClearable
                options={allProfessors}
                value={selectedOption}
                onChange={(_, newValue) => setSelectedOption(newValue)}
                isOptionEqualToValue={(option, value) => option.value === value.value}
                getOptionLabel={(option) => option.label}
                sx={{flex: 1}}
                renderInput={(params) => (
                    <TextField
                        {...params}
                        sx={{
                            backgroundColor: 'white',
                            borderRadius: 1,
                            width: "350px"
                        }}
                    />
                )}
            />
            <IconButton
                onClick={handleSearch}
                sx={{
                    backgroundColor: '#1976d2',
                    color: 'white',
                    '&:hover': {
                        backgroundColor: '#115293',
                    },
                    width: 40,
                    height: 40
                }}
            >
                <SearchIcon/>
            </IconButton>
        </Box>
            {error && <Typography color="error">Es muss ein Professor gewählt werden</Typography>}
        </Box>
    );
}
