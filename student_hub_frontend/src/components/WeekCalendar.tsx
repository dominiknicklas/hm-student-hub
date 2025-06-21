import {
    Calendar,
    dateFnsLocalizer,
} from "react-big-calendar";
import { de } from "date-fns/locale";
import {
    format,
    parse,
    startOfWeek,
    getDay,
} from "date-fns";
import "react-big-calendar/lib/css/react-big-calendar.css";
import type {MyEvent} from "../types.ts";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import { Button } from "@mui/material";
import DownloadIcon from '@mui/icons-material/Download';

const locales = {
    de: de,
};

const localizer = dateFnsLocalizer({
    format,
    parse,
    startOfWeek,
    getDay,
    locales,
});

type WeekCalendarProps = {
    myEvents: MyEvent[];
    downloadCalendar: () => void;
};

export const WeekCalendar = ({ myEvents, downloadCalendar }: WeekCalendarProps) => {

    return (
        <Box >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '5px' }}>
                {/* Top left heading */}
                <Typography variant="h5" fontWeight="bold">
                    Wochenkalender
                </Typography>

                {/* Middle - download Button */}
                <Button onClick={downloadCalendar}>
                    <DownloadIcon sx={{marginRight: '5px'}}/>
                    Kalender laden
                </Button>

                {/* Top right legend */}
                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                        <Box sx={{ width: 16, height: 16, backgroundColor: '#ad7131', borderRadius: '2px', mr: 1 }} />
                        <Typography variant="body2">Praktikum</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Box sx={{ width: 16, height: 16, backgroundColor: '#3174ad', borderRadius: '2px', mr: 1 }} />
                        <Typography variant="body2">Vorlesung</Typography>
                    </Box>
                </Box>
            </Box>
            <Box style={{ height: "790px" }}>
                <Calendar
                    localizer={localizer}
                    events={myEvents}
                    defaultView={'work_week'}
                    views={['day', 'work_week']}
                    defaultDate={new Date(2025, 4, 12)}
                    step={60}
                    timeslots={1}
                    toolbar={false}
                    formats={{
                        dayFormat: (date) => format(date, 'EEEE'),
                        timeGutterFormat: "HH:mm",
                        eventTimeRangeFormat: ({ start, end }) => `${format(start, 'HH:mm')} – ${format(end, 'HH:mm')}`,
                    }}
                    min={new Date(2025, 4, 12, 8, 0)}
                    max={new Date(2025, 4, 12, 21, 0)}
                    style={{ height: "100%", width: "100%" }}
                    components={{
                        work_week: {
                            header: ({ date }) => (
                                <div style={{ textAlign: 'center', fontWeight: 700, fontSize: 15 , minWidth: 150 }}>
                                    {new Intl.DateTimeFormat('de-DE', { weekday: 'long' }).format(date)}
                                </div>
                            )
                        },
                        event: ({ event }) => (
                            <div style={{ padding: '2px 4px', height: '100%', width: '100%', boxSizing: 'border-box' }}>
                                <strong>{event.module}</strong>
                            </div>
                        )
                    }}
                    eventPropGetter={(event) => {
                        const style = {
                            backgroundColor: event.format === "Praktikum" ? "#ad7131" : "#3174ad",
                            color: "white",
                            borderRadius: "4px",
                            border: "none",
                            display: "block",
                            padding: "2px 4px",
                        };
                        return { style };
                    }}
                    dayLayoutAlgorithm="no-overlap"
                />
            </Box>
        </Box>
    );
};