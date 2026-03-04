import React, { useState } from 'react';
import { uploadPDF } from '../api';

function UploadForm({ onSuccess, setLoading }) {
    const [file, setFile] = useState(null);
    const [error, setError] = useState('');

    const handleFileChange = (e) => {
        const selected = e.target.files[0];
        if (selected && selected.type === 'application/pdf') {
            setFile(selected);
            setError('');
        } else {
            setError('Please select a valid PDF file.');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!file) {
            setError('Please select a file first.');
            return;
        }

        setLoading(true);
        setError('');

        try {
            const data = await uploadPDF(file);
            onSuccess(data);
        } catch (err) {
            setError(err.message || 'Something went wrong.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="card upload-form">
            <h2>📄 Upload Your PDF</h2>
            <form onSubmit={handleSubmit}>
                <div className="upload-area">
                    <input type="file" accept=".pdf" onChange={handleFileChange} />
                    {file && <p>Selected: {file.name}</p>}
                </div>
                <button type="submit" className="upload-btn" disabled={!file}>
                    Upload & Process
                </button>
            </form>
            {error && <p style={{ color: '#e17055', marginTop: '1rem' }}>{error}</p>}
        </div>
    );
}

export default UploadForm;
