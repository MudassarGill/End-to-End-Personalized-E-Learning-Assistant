// API helper for communicating with the backend
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export const uploadPDF = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Upload failed');
    }

    return response.json();
};
