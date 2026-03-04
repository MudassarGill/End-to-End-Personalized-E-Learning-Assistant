import React, { useState, useCallback } from "react";
import "./App.css";
import UploadForm from "./components/UploadForm";
import SummaryDisplay from "./components/SummaryDisplay";
import Quiz from "./components/Quiz";
import ProgressDashboard from "./components/ProgressDashboard";

const USER_ID = "student_" + Math.random().toString(36).slice(2, 8);

function App() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("upload");
  const [quizScore, setQuizScore] = useState(null);

  const handleUploadSuccess = useCallback((data) => {
    setResults(data);
    setError(null);
    setQuizScore(null);
    setActiveTab("results");
  }, []);

  const handleError = useCallback((msg) => {
    setError(msg);
    setResults(null);
  }, []);

  const handleQuizComplete = useCallback((scoreData) => {
    setQuizScore(scoreData);
  }, []);

  const handleReset = useCallback(() => {
    setResults(null);
    setError(null);
    setQuizScore(null);
    setActiveTab("upload");
  }, []);

  return (
    <div className="App">
      {/* Header */}
      <header className="app-header">
        <div className="header-glow"></div>
        <h1>📚 E-Learning Assistant</h1>
        <p>Upload any document — get AI summary, keywords & quiz instantly</p>
        <span className="user-badge">🎓 {USER_ID}</span>
      </header>

      {/* Navigation */}
      <nav className="app-nav">
        <button
          className={`nav-btn ${activeTab === "upload" ? "active" : ""}`}
          onClick={() => setActiveTab("upload")}
        >
          📤 Upload
        </button>
        <button
          className={`nav-btn ${activeTab === "results" ? "active" : ""}`}
          onClick={() => setActiveTab("results")}
          disabled={!results}
        >
          📊 Results
        </button>
        <button
          className={`nav-btn ${activeTab === "progress" ? "active" : ""}`}
          onClick={() => setActiveTab("progress")}
        >
          📈 Progress
        </button>
      </nav>

      {/* Error Display */}
      {error && (
        <div className="error-banner">
          <span>❌ {error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {/* Loading Overlay */}
      {loading && (
        <div className="loading-overlay">
          <div className="spinner"></div>
          <p>Processing your document...</p>
          <p className="loading-sub">Extracting text → Summarizing → Generating Quiz</p>
        </div>
      )}

      {/* Main Content */}
      <main className="app-main">
        {/* Upload Tab */}
        {activeTab === "upload" && (
          <UploadForm
            userId={USER_ID}
            onSuccess={handleUploadSuccess}
            onError={handleError}
            onLoading={setLoading}
          />
        )}

        {/* Results Tab */}
        {activeTab === "results" && results && (
          <div className="results-container">
            {/* File Info */}
            <div className="card file-info-card">
              <div className="file-info-header">
                <h2>📄 {results.filename || "Processed Document"}</h2>
                <button className="btn-outline" onClick={handleReset}>
                  ↩ Upload New
                </button>
              </div>
              <div className="file-stats">
                <span>📝 {results.words?.toLocaleString()} words</span>
                {results.pages > 0 && <span>📃 {results.pages} pages</span>}
                <span>🔤 {results.characters?.toLocaleString()} characters</span>
              </div>
            </div>

            {/* Summary */}
            <SummaryDisplay
              summary={results.summary}
              keywords={results.keywords}
            />

            {/* Quiz */}
            {results.quiz && results.quiz.questions?.length > 0 && (
              <Quiz
                quiz={results.quiz}
                userId={USER_ID}
                onComplete={handleQuizComplete}
              />
            )}

            {/* Score Card */}
            {quizScore && (
              <div className={`card score-card ${quizScore.grade === "F" ? "score-fail" : "score-pass"}`}>
                <h2>🏆 Quiz Result</h2>
                <div className="score-display">
                  <div className="score-big">{quizScore.percentage}</div>
                  <div className="score-grade">Grade: {quizScore.grade}</div>
                </div>
                <p>
                  {quizScore.correct} / {quizScore.total} correct
                </p>
              </div>
            )}
          </div>
        )}

        {/* Progress Tab */}
        {activeTab === "progress" && (
          <ProgressDashboard userId={USER_ID} />
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>🇵🇰 Built for Pakistani Students | English + اردو Support</p>
      </footer>
    </div>
  );
}

export default App;
