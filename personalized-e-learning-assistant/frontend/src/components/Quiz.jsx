import React, { useState } from "react";
import { submitQuiz } from "../api";

export default function Quiz({ quiz, userId, onComplete }) {
    const [answers, setAnswers] = useState({});
    const [submitted, setSubmitted] = useState(false);
    const [feedback, setFeedback] = useState(null);
    const [submitting, setSubmitting] = useState(false);
    const [currentQ, setCurrentQ] = useState(0);

    const questions = quiz.questions || [];

    if (questions.length === 0) return null;

    const handleSelect = (questionId, optionLabel) => {
        if (submitted) return;
        setAnswers((prev) => ({ ...prev, [String(questionId)]: optionLabel }));
    };

    const handleSubmit = async () => {
        if (Object.keys(answers).length < questions.length) {
            alert("Please answer all questions before submitting!");
            return;
        }

        setSubmitting(true);
        try {
            const result = await submitQuiz(quiz.quiz_id, answers, userId);
            if (result.success) {
                setSubmitted(true);
                setFeedback(result.data);
                onComplete(result.data);
            }
        } catch (err) {
            alert("Error submitting quiz: " + err.message);
        } finally {
            setSubmitting(false);
        }
    };

    const q = questions[currentQ];
    const totalAnswered = Object.keys(answers).length;

    return (
        <div className="card quiz-card">
            <div className="quiz-header">
                <h2>❓ Quiz</h2>
                <span className="quiz-progress">
                    {totalAnswered}/{questions.length} answered
                </span>
            </div>

            {/* Progress Bar */}
            <div className="progress-bar">
                <div
                    className="progress-fill"
                    style={{ width: `${(totalAnswered / questions.length) * 100}%` }}
                ></div>
            </div>

            {/* Question Navigation */}
            <div className="question-nav">
                {questions.map((_, i) => (
                    <button
                        key={i}
                        className={`q-dot ${i === currentQ ? "active" : ""} ${answers[String(questions[i].id)] ? "answered" : ""
                            } ${submitted && feedback?.feedback?.[i]?.is_correct
                                ? "correct"
                                : submitted && feedback?.feedback?.[i]?.is_correct === false
                                    ? "incorrect"
                                    : ""
                            }`}
                        onClick={() => setCurrentQ(i)}
                    >
                        {i + 1}
                    </button>
                ))}
            </div>

            {/* Question */}
            <div className="quiz-question">
                <p className="q-number">Question {currentQ + 1} of {questions.length}</p>
                <p className="q-text">{q.question}</p>

                <ul className="quiz-options">
                    {(q.options || []).map((opt) => {
                        const isSelected = answers[String(q.id)] === opt.label;
                        let optClass = "";

                        if (submitted && feedback) {
                            const fb = feedback.feedback?.find(
                                (f) => String(f.question_id) === String(q.id)
                            );
                            if (fb) {
                                if (opt.label === fb.correct_answer) optClass = "correct";
                                else if (isSelected && !fb.is_correct) optClass = "incorrect";
                            }
                        } else if (isSelected) {
                            optClass = "selected";
                        }

                        return (
                            <li
                                key={opt.label}
                                className={optClass}
                                onClick={() => handleSelect(q.id, opt.label)}
                            >
                                <span className="opt-label">{opt.label}</span>
                                <span className="opt-text">{opt.text}</span>
                            </li>
                        );
                    })}
                </ul>

                {/* Explanation after submit */}
                {submitted && feedback && (
                    <div className="explanation">
                        {feedback.feedback?.find(
                            (f) => String(f.question_id) === String(q.id)
                        )?.is_correct ? (
                            <p className="correct-msg">✅ Correct!</p>
                        ) : (
                            <p className="incorrect-msg">
                                ❌ Incorrect. Correct answer:{" "}
                                {feedback.feedback?.find(
                                    (f) => String(f.question_id) === String(q.id)
                                )?.correct_answer}
                            </p>
                        )}
                    </div>
                )}
            </div>

            {/* Navigation */}
            <div className="quiz-actions">
                <button
                    className="btn-outline"
                    onClick={() => setCurrentQ(Math.max(0, currentQ - 1))}
                    disabled={currentQ === 0}
                >
                    ← Previous
                </button>

                {currentQ < questions.length - 1 ? (
                    <button
                        className="btn-primary"
                        onClick={() => setCurrentQ(currentQ + 1)}
                    >
                        Next →
                    </button>
                ) : !submitted ? (
                    <button
                        className="upload-btn"
                        onClick={handleSubmit}
                        disabled={submitting || totalAnswered < questions.length}
                    >
                        {submitting ? "⏳ Submitting..." : "✅ Submit Quiz"}
                    </button>
                ) : null}
            </div>
        </div>
    );
}
