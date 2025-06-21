import Box from "@mui/material/Box";
import type {ModuleEntry} from "../types.ts";
import { DataGrid, type GridColDef } from '@mui/x-data-grid';

type Props = {
    modules: ModuleEntry[];
};

export default function GradesTable({ modules }: Props) {
    const columns: GridColDef[] = [
        { field: 'module', headerName: 'Modul', flex: 3 },
        { field: 'grade', headerName: 'Note', flex: 1 },
        { field: 'ects', headerName: 'ECTS', flex: 1 },
    ];

    const rows = modules.map((m, index) => ({
        id: index,
        module: m.module,
        grade: m.grade,
        ects: m.ects,
    }));

    return (
        <Box sx={{ height: '400px', width: '100%', mt: 2 }}>
            <DataGrid
                rows={rows}
                columns={columns}
                hideFooterPagination
                hideFooterSelectedRowCount
                disableColumnFilter
                disableColumnMenu
                disableColumnSelector
                autoHeight={false}
            />
        </Box>
    );
}