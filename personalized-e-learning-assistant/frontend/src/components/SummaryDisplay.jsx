import React, { useState } from "react";

export default function SummaryDisplay({ summary, keywords }) {
    const [expanded, setExpanded] = useState(false);

    if (!summary && (!keywords || keywords.length === 0)) return null;

    return (
        <div className="results-grid">
            {/* Summary Card */}
            {summary && (
                <div className="card summary-card glass-card">
                    <div className="card-accent-bg"></div>
                    <div className="card-header-row">
                        <span className="card-header-icon">📝</span>
                        <h2>Summary</h2>
                    </div>
                    <div className="summary-meta">
                        <span className="meta-badge">
                            {summary.split(/\s+/).length} words
                        </span>
                        <span className="meta-badge">
                            {summary.length} chars
                        </span>
                    </div>
                    <div className="summary-text">
                        {expanded || summary.length <= 300
                            ? summary
                            : summary.slice(0, 300) + "..."}
                    </div>
                    {summary.length > 300 && (
                        <button
                            className="btn-link"
                            onClick={() => setExpanded(!expanded)}
                        >
                            {expanded ? "Show Less ▲" : "Read More ▼"}
                        </button>
                    )}
                </div>
            )}

            {/* Keywords Card */}
            {keywords && keywords.length > 0 && (
                <div className="card keywords-card glass-card">
                    <div className="card-accent-bg keywords-accent"></div>
                    <div className="card-header-row">
                        <span className="card-header-icon">🔑</span>
                        <h2>Keywords</h2>
                    </div>
                    <div className="summary-meta">
                        <span className="meta-badge">
                            {keywords.length} extracted
                        </span>
                    </div>
                    <div className="keywords-list">
                        {keywords.map((kw, i) => (
                            <span
                                key={i}
                                className="keyword-tag animate-in"
                                style={{ animationDelay: `${i * 0.06}s` }}
                            >
                                {kw}
                            </span>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
