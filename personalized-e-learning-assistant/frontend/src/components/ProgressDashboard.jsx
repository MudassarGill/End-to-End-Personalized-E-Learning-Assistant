import React from 'react';

function ProgressDashboard() {
    // Placeholder progress data — connect to backend for real tracking
    const progress = {
        documentsProcessed: 1,
        quizzesTaken: 0,
        averageScore: 0,
    };

    return (
        <div className="card">
            <h2>📊 Your Progress</h2>

            <div style={{ marginBottom: '1rem' }}>
                <p>Documents Processed: <strong>{progress.documentsProcessed}</strong></p>
            </div>

            <div style={{ marginBottom: '1rem' }}>
                <p>Quizzes Taken: <strong>{progress.quizzesTaken}</strong></p>
                <div className="progress-bar">
                    <div
                        className="progress-fill"
                        style={{ width: `${progress.quizzesTaken * 10}%` }}
                    />
                </div>
            </div>

            <div>
                <p>Average Score: <strong>{progress.averageScore}%</strong></p>
                <div className="progress-bar">
                    <div
                        className="progress-fill"
                        style={{ width: `${progress.averageScore}%` }}
                    />
                </div>
            </div>
        </div>
    );
}

export default ProgressDashboard;
