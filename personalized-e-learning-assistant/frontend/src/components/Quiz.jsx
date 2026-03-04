import React, { useState } from 'react';

function Quiz({ questions }) {
    const [answers, setAnswers] = useState({});
    const [showResults, setShowResults] = useState(false);

    const handleSelect = (questionId, option) => {
        if (showResults) return;
        setAnswers({ ...answers, [questionId]: option });
    };

    const handleSubmit = () => {
        setShowResults(true);
    };

    const getScore = () => {
        let correct = 0;
        questions.forEach((q) => {
            if (answers[q.id] === q.correct_answer) correct++;
        });
        return correct;
    };

    if (!questions || questions.length === 0) {
        return null;
    }

    return (
        <div className="card">
            <h2>❓ Quiz</h2>

            {questions.map((q) => (
                <div key={q.id} className="quiz-question">
                    <p><strong>Q{q.id}:</strong> {q.question}</p>
                    <ul className="quiz-options">
                        {q.options.map((opt) => {
                            let className = '';
                            if (answers[q.id] === opt.label) className += ' selected';
                            if (showResults) {
                                if (opt.label === q.correct_answer) className += ' correct';
                                else if (answers[q.id] === opt.label) className += ' incorrect';
                            }
                            return (
                                <li
                                    key={opt.label}
                                    className={className.trim()}
                                    onClick={() => handleSelect(q.id, opt.label)}
                                >
                                    <strong>{opt.label}.</strong> {opt.text}
                                </li>
                            );
                        })}
                    </ul>
                </div>
            ))}

            {!showResults ? (
                <button className="upload-btn" onClick={handleSubmit}>
                    Submit Quiz
                </button>
            ) : (
                <p style={{ fontSize: '1.2rem', color: '#00b894' }}>
                    Score: {getScore()} / {questions.length}
                </p>
            )}
        </div>
    );
}

export default Quiz;
