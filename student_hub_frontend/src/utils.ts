import type {Lecture, MyEvent} from "./types.ts";

const weekdayToDate: Record<string, [number, number, number]> = {
    Montag: [2025, 4, 12],
    Dienstag: [2025, 4, 13],
    Mittwoch: [2025, 4, 14],
    Donnerstag: [2025, 4, 15],
    Freitag: [2025, 4, 16],
};

const weekdayOrder = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"];

// Function to parse time strings in "HH:MM" format to [hour, minute] pairs
function parseTimeString(time: string): [number, number] {
    const [hourStr, minuteStr] = time.split(':');
    return [parseInt(hourStr, 10), parseInt(minuteStr, 10)];
}

export function convertLecturesToEvents(lectures: Lecture[]): MyEvent[] {
    return lectures.map((lecture) => {
        const [startStr, endStr] = lecture.time.split(' - ');
        const [year, month, day] = weekdayToDate[lecture.weekday];
        const [startHour, startMinute] = parseTimeString(startStr);
        const [endHour, endMinute] = parseTimeString(endStr);

        return {
            module: lecture.title.replace(/\s+-\s+(Vorlesung|Praktikum)$/, ''),
            start: new Date(year, month, day, startHour, startMinute),
            end: new Date(year, month, day, endHour, endMinute),
            format: lecture.format,
            room: lecture.room
        };
    });
}

export function parseEvents(rawEvents: MyEvent[]): MyEvent[] {
    return rawEvents.map((e) => ({
        id: e.id,
        module: e.module,
        room: e.room,
        format: e.format,
        start: new Date(e.start), 
        end: new Date(e.end),    
    }));
}

// Helper: get index of weekday in the predefined order
function getWeekdayIndex(weekday: string): number {
    return weekdayOrder.indexOf(weekday);
}

// Helper: extract start time as a Date object (or number of minutes)
function getStartTimeMinutes(time: string): number {
    const [start] = time.split(" - ");
    const [hours, minutes] = start.split(":").map(Number);
    return hours * 60 + minutes;
}

export default function sortLecturesByTime(lectures: Lecture[]): Lecture[] {
    return lectures.sort((a, b) => {
        const weekdayDiff = getWeekdayIndex(a.weekday) - getWeekdayIndex(b.weekday);
        if (weekdayDiff !== 0) return weekdayDiff;

        return getStartTimeMinutes(a.time) - getStartTimeMinutes(b.time);
    });
}