import React, { useState, useEffect } from "react";
import { getProgress } from "../api";

export default function ProgressDashboard({ userId }) {
    const [progress, setProgress] = useState(null);
    const [attempts, setAttempts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchProgress();
    }, [userId]);

    const fetchProgress = async () => {
        setLoading(true);
        try {
            const result = await getProgress(userId);
            if (result.success) {
                setProgress(result.data.progress);
                setAttempts(result.data.recent_attempts || []);
            } else {
                setError(result.message);
            }
        } catch (err) {
            setError("Could not load progress. Is the backend running?");
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="card">
                <p className="loading">Loading progress...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="card">
                <h2>📈 Progress Dashboard</h2>
                <p className="error-text">{error}</p>
                <button className="btn-outline" onClick={fetchProgress}>
                    🔄 Retry
                </button>
            </div>
        );
    }

    const avgScore = progress?.avg_score || 0;
    const bestScore = progress?.best_score || 0;
    const totalAttempts = progress?.total_attempts || 0;
    const recentScores = progress?.recent_scores || [];

    return (
        <div className="progress-container">
            {/* Stats Grid */}
            <div className="stats-grid">
                <div className="card stat-card">
                    <div className="stat-icon">📊</div>
                    <div className="stat-value">{avgScore.toFixed(0)}%</div>
                    <div className="stat-label">Average Score</div>
                    <div className="progress-bar">
                        <div
                            className="progress-fill"
                            style={{ width: `${avgScore}%` }}
                        ></div>
                    </div>
                </div>

                <div className="card stat-card">
                    <div className="stat-icon">🏆</div>
                    <div className="stat-value">{bestScore.toFixed(0)}%</div>
                    <div className="stat-label">Best Score</div>
                    <div className="progress-bar">
                        <div
                            className="progress-fill best"
                            style={{ width: `${bestScore}%` }}
                        ></div>
                    </div>
                </div>

                <div className="card stat-card">
                    <div className="stat-icon">📝</div>
                    <div className="stat-value">{totalAttempts}</div>
                    <div className="stat-label">Total Attempts</div>
                </div>

                <div className="card stat-card">
                    <div className="stat-icon">🎯</div>
                    <div className="stat-value">
                        {avgScore >= 70 ? "Good" : avgScore >= 50 ? "Fair" : "Needs Work"}
                    </div>
                    <div className="stat-label">Performance</div>
                </div>
            </div>

            {/* Score History */}
            {recentScores.length > 0 && (
                <div className="card">
                    <h2>📈 Score History (Last 10)</h2>
                    <div className="score-chart">
                        {recentScores.map((score, i) => (
                            <div key={i} className="chart-bar-wrapper">
                                <div
                                    className={`chart-bar ${score >= 70 ? "bar-good" : score >= 50 ? "bar-ok" : "bar-low"
                                        }`}
                                    style={{ height: `${Math.max(score, 5)}%` }}
                                >
                                    <span className="bar-label">{score.toFixed(0)}%</span>
                                </div>
                                <span className="bar-index">#{i + 1}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Strengths & Weaknesses */}
            <div className="sw-grid">
                {progress?.strengths?.length > 0 && (
                    <div className="card strength-card">
                        <h2>💪 Strengths</h2>
                        <div className="keywords-list">
                            {progress.strengths.slice(0, 10).map((s, i) => (
                                <span key={i} className="keyword-tag strength-tag">{s}</span>
                            ))}
                        </div>
                    </div>
                )}

                {progress?.weaknesses?.length > 0 && (
                    <div className="card weakness-card">
                        <h2>📖 Needs Improvement</h2>
                        <div className="keywords-list">
                            {progress.weaknesses.slice(0, 10).map((w, i) => (
                                <span key={i} className="keyword-tag weakness-tag">{w}</span>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* Recent Attempts List */}
            {attempts.length > 0 && (
                <div className="card">
                    <h2>🕐 Recent Attempts</h2>
                    <div className="attempts-list">
                        {attempts.map((a, i) => (
                            <div key={i} className="attempt-row">
                                <span className="attempt-score">
                                    {a.score?.toFixed(0)}%
                                </span>
                                <span>
                                    {a.correct_count}/{a.total_questions} correct
                                </span>
                                <span className="attempt-date">
                                    {new Date(a.date).toLocaleDateString()}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Empty State */}
            {totalAttempts === 0 && (
                <div className="card empty-state">
                    <p>🎯 No quiz attempts yet!</p>
                    <p>Upload a document and take a quiz to see your progress here.</p>
                </div>
            )}
        </div>
    );
}
