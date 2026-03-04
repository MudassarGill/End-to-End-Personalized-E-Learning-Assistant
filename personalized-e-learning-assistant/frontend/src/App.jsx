import React, { useState } from 'react';
import UploadForm from './components/UploadForm';
import SummaryDisplay from './components/SummaryDisplay';
import Quiz from './components/Quiz';
import ProgressDashboard from './components/ProgressDashboard';
import './App.css';

function App() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUploadSuccess = (data) => {
    setResults(data);
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>📚 Personalized E-Learning Assistant</h1>
        <p>Upload a PDF to get AI-powered summaries, keywords, and quizzes</p>
      </header>

      <main className="app-main">
        <UploadForm onSuccess={handleUploadSuccess} setLoading={setLoading} />

        {loading && <div className="loading">Processing your document...</div>}

        {results && (
          <div className="results-container">
            <SummaryDisplay summary={results.summary} keywords={results.keywords} />
            <Quiz questions={results.quiz} />
            <ProgressDashboard />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
