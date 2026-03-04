import React from 'react';

function SummaryDisplay({ summary, keywords }) {
    return (
        <div className="card">
            <h2>📝 Summary</h2>
            <p style={{ lineHeight: '1.8', color: '#b2b2d0' }}>{summary}</p>

            <h2 style={{ marginTop: '1.5rem' }}>🔑 Keywords</h2>
            <div className="keywords-list">
                {keywords && keywords.map((kw, index) => (
                    <span key={index} className="keyword-tag">{kw}</span>
                ))}
            </div>
        </div>
    );
}

export default SummaryDisplay;
