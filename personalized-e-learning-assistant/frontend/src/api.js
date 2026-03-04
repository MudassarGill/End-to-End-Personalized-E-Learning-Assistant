/**
 * API Service - Communicates with FastAPI backend
 * Base URL: http://localhost:8000/api
 */

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000/api";

/**
 * Upload a file (PDF, DOCX, TXT, etc.)
 */
export async function uploadFile(file, userId = "anonymous") {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("user_id", userId);

    const response = await fetch(`${API_BASE}/upload`, {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.message || `Upload failed (${response.status})`);
    }

    return response.json();
}

/**
 * Upload raw text for processing
 */
export async function uploadText(text, userId = "anonymous", title = "Text Input") {
    const response = await fetch(`${API_BASE}/upload/text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, user_id: userId, title }),
    });

    if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.message || "Text processing failed");
    }

    return response.json();
}

/**
 * Submit quiz answers
 */
export async function submitQuiz(quizId, answers, userId = "anonymous", timeTaken = 0) {
    const response = await fetch(`${API_BASE}/submit-quiz`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            quiz_id: quizId,
            answers,
            user_id: userId,
            time_taken_seconds: timeTaken,
        }),
    });

    if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.message || "Quiz submission failed");
    }

    return response.json();
}

/**
 * Get user progress
 */
export async function getProgress(userId) {
    const response = await fetch(`${API_BASE}/progress/${userId}`);
    if (!response.ok) throw new Error("Could not fetch progress");
    return response.json();
}

/**
 * Get a specific quiz
 */
export async function getQuiz(quizId) {
    const response = await fetch(`${API_BASE}/quiz/${quizId}`);
    if (!response.ok) throw new Error("Quiz not found");
    return response.json();
}

/**
 * Get all quizzes for a user
 */
export async function getUserQuizzes(userId, page = 1, limit = 10) {
    const response = await fetch(
        `${API_BASE}/user/${userId}/quizzes?page=${page}&limit=${limit}`
    );
    if (!response.ok) throw new Error("Could not fetch quizzes");
    return response.json();
}

/**
 * Health check
 */
export async function healthCheck() {
    try {
        const response = await fetch("http://localhost:8000/health");
        return response.json();
    } catch {
        return { success: false, data: { status: "offline" } };
    }
}
