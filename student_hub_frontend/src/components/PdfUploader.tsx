// PdfUploader.tsx
import { useDropzone } from 'react-dropzone';
import { Box, Typography, Button } from '@mui/material';
import { useCallback } from 'react';

type PdfUploaderProps = {
    onFileSelect: (file: File | null) => void;
    selectedFile: File | null;
};

export default function PdfUploader({ onFileSelect, selectedFile }: PdfUploaderProps) {
    const onDrop = useCallback((acceptedFiles: File[]) => {
        const file = acceptedFiles[0];
        if (file?.type === 'application/pdf') {
            onFileSelect(file);
        }
    }, [onFileSelect]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        multiple: false,
        accept: { 'application/pdf': ['.pdf'] },
    });

    return (
        <Box
            {...getRootProps()}
            sx={{
                p: 2,
                border: '2px dashed #ccc',
                borderRadius: 2,
                textAlign: 'center',
                backgroundColor: isDragActive ? '#f0f0f0' : 'transparent',
                cursor: 'pointer',
            }}
        >
            <input {...getInputProps()} />
            <Typography variant="body1">
                {selectedFile ? selectedFile.name : 'PDF hier ablegen oder klicken zum Hochladen'}
            </Typography>
            {selectedFile && (
                <Button onClick={(e) => { e.stopPropagation(); onFileSelect(null); }} sx={{ mt: 1 }} color="error">
                    Entfernen
                </Button>
            )}
        </Box>
    );
}
