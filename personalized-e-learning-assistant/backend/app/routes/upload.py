"""
API Routes - Upload, Quiz, Progress Endpoints
All endpoints return consistent format: {success, data, message, error}
"""

import os
import uuid
import logging
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

from app.models.user import (
    UserModel, PDFModel, QuizModel, AttemptModel, ProgressModel,
)
from app.services.text_extraction import PDFTextExtractor, extract_text
from app.services.summarizer import Summarizer
from app.services.keywords import KeywordExtractor
from app.services.quiz_generator import QuizGenerator
from app.services.s3_upload import s3_uploader
from app.services.mlflow_tracking import mlflow_tracker
from app.utils import validate_file, format_response, format_error

logger = logging.getLogger("elearning.routes")
router = APIRouter()

# ─── Constants ───
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".pptx", ".xlsx", ".csv", ".md",
                      ".png", ".jpg", ".jpeg"}

# ─── Service Instances ───
pdf_extractor = PDFTextExtractor()
summarizer = Summarizer()
keyword_extractor = KeywordExtractor()
quiz_generator = QuizGenerator()


# ═══════════════════════════════════════════════
#  Request Models
# ═══════════════════════════════════════════════
class TextUploadRequest(BaseModel):
    text: str
    user_id: Optional[str] = "anonymous"
    title: Optional[str] = "Text Input"


class QuizSubmitRequest(BaseModel):
    user_id: str
    quiz_id: str
    answers: dict  # {question_id: selected_option}
    time_taken_seconds: Optional[int] = 0


# ═══════════════════════════════════════════════
#  POST /upload — Upload File & Process
# ═══════════════════════════════════════════════
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Form(default="anonymous"),
):
    """
    Upload a PDF/document → get summary, keywords, and quiz.
    Max size: 10MB. Supported: PDF, DOCX, TXT, PPTX, XLSX, images.
    """
    logger.info(f"Upload: {file.filename} by user={user_id}")

    # ── 1. Validate File ──
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return format_error(
            f"Unsupported file type: {ext}. Supported: {', '.join(ALLOWED_EXTENSIONS)}",
            status_code=400,
        )

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE:
        size_mb = len(file_bytes) / (1024 * 1024)
        return format_error(
            f"File too large: {size_mb:.1f}MB. Maximum: 10MB.",
            status_code=400,
        )

    if len(file_bytes) == 0:
        return format_error("Empty file uploaded.", status_code=400)

    # ── 2. Upload to S3 (non-blocking, best-effort) ──
    s3_url = ""
    if s3_uploader.is_available:
        s3_result = s3_uploader.upload(
            file_bytes,
            f"{uuid.uuid4().hex}_{file.filename}",
            prefix="uploads/",
            content_type=file.content_type or "application/octet-stream",
        )
        s3_url = s3_result.get("url", "")

    # ── 3. Extract Text ──
    try:
        if ext == ".pdf":
            result = pdf_extractor.extract_from_bytes(file_bytes)
            if not result["success"]:
                return format_error(f"Text extraction failed: {result['error']}")
            extracted_text = result["cleaned_text"]
            pages = result["pages"]
        else:
            extracted_text = extract_text(file_bytes, file.filename)
            pages = 0
    except Exception as e:
        logger.error(f"Extraction error: {e}")
        return format_error(f"Could not extract text: {str(e)}")

    if not extracted_text or len(extracted_text.strip()) < 20:
        return format_error(
            "Very little or no text extracted. File may be scanned/empty."
        )

    # ── 4. Generate Summary ──
    summary_method = "extractive"
    compression_ratio = 0.0
    try:
        summary_result = summarizer.summarize(extracted_text)
        summary = summary_result["summary"]
        summary_method = summary_result.get("method", "extractive")
        compression_ratio = summary_result.get("compression_ratio", 0.0)
    except Exception as e:
        logger.error(f"Summarization error: {e}")
        summary = extracted_text[:500] + "..."

    # ── 5. Extract Keywords ──
    keyword_method = "frequency"
    try:
        kw_result = keyword_extractor.extract_keywords(extracted_text)
        keywords = kw_result["keywords"]
        keyword_method = kw_result.get("method", "frequency")
    except Exception as e:
        logger.error(f"Keyword error: {e}")
        keywords = []

    # ── 6. Generate Quiz ──
    try:
        quiz_result = quiz_generator.generate_quiz(extracted_text, keywords)
        questions = quiz_result["questions"]
    except Exception as e:
        logger.error(f"Quiz generation error: {e}")
        questions = []

    # ── 7. Log processing metrics to MLflow ──
    mlflow_tracker.log_processing_run(
        filename=file.filename,
        text_length=len(extracted_text),
        summary_length=len(summary),
        summary_method=summary_method,
        compression_ratio=compression_ratio,
        keyword_count=len(keywords),
        keyword_method=keyword_method,
        quiz_question_count=len(questions),
    )

    # ── 8. Save to MongoDB ──
    pdf_record = None
    quiz_record = None
    try:
        # Save PDF record
        pdf_record = await PDFModel.create(
            user_id=user_id,
            filename=f"{uuid.uuid4().hex}_{file.filename}",
            original_filename=file.filename,
            pages=pages,
            size_bytes=len(file_bytes),
            text_content=extracted_text,
            summary=summary,
            keywords=keywords,
            s3_url=s3_url,
        )

        # Save Quiz
        if questions:
            quiz_record = await QuizModel.create(
                user_id=user_id,
                pdf_id=pdf_record["id"],
                title=f"Quiz: {file.filename}",
                questions=questions,
            )
    except Exception as e:
        logger.warning(f"MongoDB save warning: {e}")

    # ── 9. Return Response ──
    return format_response(
        data={
            "filename": file.filename,
            "file_type": ext,
            "pages": pages,
            "characters": len(extracted_text),
            "words": len(extracted_text.split()),
            "text_preview": extracted_text[:300],
            "summary": summary,
            "keywords": keywords,
            "quiz": {
                "quiz_id": quiz_record["id"] if quiz_record else None,
                "questions": questions,
                "total_questions": len(questions),
            },
            "pdf_id": pdf_record["id"] if pdf_record else None,
        },
        message=f"Processed {file.filename}: {len(extracted_text.split())} words, "
                f"{len(questions)} quiz questions generated.",
    )


# ═══════════════════════════════════════════════
#  POST /upload/text — Process Raw Text
# ═══════════════════════════════════════════════
@router.post("/upload/text")
async def upload_text(request: TextUploadRequest):
    """Upload raw text and get summary, keywords, quiz."""
    text = request.text.strip()

    if len(text) < 50:
        return format_error("Text too short. Please provide at least 50 characters.")

    # Summarize
    try:
        summary_result = summarizer.summarize(text)
        summary = summary_result["summary"]
    except Exception as e:
        summary = text[:300] + "..."

    # Keywords
    try:
        kw_result = keyword_extractor.extract_keywords(text)
        keywords = kw_result["keywords"]
    except Exception:
        keywords = []

    # Quiz
    try:
        quiz_result = quiz_generator.generate_quiz(text, keywords)
        questions = quiz_result["questions"]
    except Exception:
        questions = []

    # Save to DB
    quiz_record = None
    try:
        pdf_record = await PDFModel.create(
            user_id=request.user_id,
            filename=f"text_{uuid.uuid4().hex[:8]}",
            original_filename=request.title,
            text_content=text,
            summary=summary,
            keywords=keywords,
        )
        if questions:
            quiz_record = await QuizModel.create(
                user_id=request.user_id,
                pdf_id=pdf_record["id"],
                title=f"Quiz: {request.title}",
                questions=questions,
            )
    except Exception as e:
        logger.warning(f"DB save warning: {e}")

    return format_response(
        data={
            "summary": summary,
            "keywords": keywords,
            "quiz": {
                "quiz_id": quiz_record["id"] if quiz_record else None,
                "questions": questions,
                "total_questions": len(questions),
            },
            "words": len(text.split()),
        },
        message="Text processed successfully.",
    )


# ═══════════════════════════════════════════════
#  POST /submit-quiz — Submit Quiz Answers
# ═══════════════════════════════════════════════
@router.post("/submit-quiz")
async def submit_quiz(request: QuizSubmitRequest):
    """Submit quiz answers, calculate score, update progress."""
    # Get quiz
    quiz = await QuizModel.get_by_id(request.quiz_id)
    if not quiz:
        return format_error("Quiz not found.", status_code=404)

    # Calculate score
    questions = quiz["questions"]
    correct_count = 0
    total = len(questions)
    feedback = []
    keywords_correct = []
    keywords_wrong = []

    for q in questions:
        q_id = str(q.get("id", ""))
        user_answer = request.answers.get(q_id)
        correct = q.get("correct_answer")

        is_correct = str(user_answer) == str(correct)
        if is_correct:
            correct_count += 1

        feedback.append({
            "question_id": q_id,
            "question": q.get("question", ""),
            "your_answer": user_answer,
            "correct_answer": correct,
            "is_correct": is_correct,
            "explanation": q.get("explanation", ""),
        })

    score = (correct_count / total * 100) if total > 0 else 0

    # Save attempt
    try:
        attempt = await AttemptModel.create(
            user_id=request.user_id,
            quiz_id=request.quiz_id,
            answers=request.answers,
            score=score,
            correct_count=correct_count,
            total_questions=total,
            time_taken_seconds=request.time_taken_seconds,
        )

        # Update progress
        await ProgressModel.update_after_attempt(
            user_id=request.user_id,
            score=score,
        )
    except Exception as e:
        logger.warning(f"DB save warning: {e}")
        attempt = {"id": None}

    return format_response(
        data={
            "attempt_id": attempt.get("id"),
            "score": round(score, 2),
            "correct": correct_count,
            "total": total,
            "percentage": f"{score:.0f}%",
            "grade": _get_grade(score),
            "feedback": feedback,
        },
        message=f"Score: {correct_count}/{total} ({score:.0f}%)",
    )


# ═══════════════════════════════════════════════
#  GET /progress/{user_id} — User Progress
# ═══════════════════════════════════════════════
@router.get("/progress/{user_id}")
async def get_progress(user_id: str):
    """Get user's learning progress and statistics."""
    try:
        progress = await ProgressModel.get_or_create(user_id)
        attempts = await AttemptModel.get_by_user(user_id, limit=10)
        quiz_count = await QuizModel.count_by_user(user_id)

        return format_response(
            data={
                "progress": progress,
                "recent_attempts": attempts,
                "total_quizzes": quiz_count,
            },
            message="Progress retrieved.",
        )
    except Exception as e:
        return format_error(f"Could not fetch progress: {e}")


# ═══════════════════════════════════════════════
#  GET /quiz/{quiz_id} — Get Quiz
# ═══════════════════════════════════════════════
@router.get("/quiz/{quiz_id}")
async def get_quiz(quiz_id: str):
    """Get a specific quiz by ID."""
    quiz = await QuizModel.get_by_id(quiz_id)
    if not quiz:
        return format_error("Quiz not found.", status_code=404)

    return format_response(data=quiz, message="Quiz retrieved.")


# ═══════════════════════════════════════════════
#  GET /user/{user_id}/quizzes — User's Quizzes
# ═══════════════════════════════════════════════
@router.get("/user/{user_id}/quizzes")
async def get_user_quizzes(user_id: str, page: int = 1, limit: int = 10):
    """Get all quizzes for a user with pagination."""
    skip = (page - 1) * limit
    try:
        quizzes = await QuizModel.get_by_user(user_id, limit=limit, skip=skip)
        total = await QuizModel.count_by_user(user_id)

        return format_response(
            data={
                "quizzes": quizzes,
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": (total + limit - 1) // limit,
            },
            message=f"Found {total} quizzes.",
        )
    except Exception as e:
        return format_error(f"Could not fetch quizzes: {e}")


# ═══════════════════════════════════════════════
#  DELETE /quiz/{quiz_id} — Delete Quiz
# ═══════════════════════════════════════════════
@router.delete("/quiz/{quiz_id}")
async def delete_quiz(quiz_id: str):
    """Delete a quiz by ID."""
    deleted = await QuizModel.delete(quiz_id)
    if not deleted:
        return format_error("Quiz not found.", status_code=404)

    return format_response(data=None, message="Quiz deleted.")


# ═══════════════════════════════════════════════
#  GET /supported-formats
# ═══════════════════════════════════════════════
@router.get("/supported-formats")
async def supported_formats():
    """List all supported upload file formats."""
    return format_response(
        data={
            "formats": list(ALLOWED_EXTENSIONS),
            "max_size_mb": MAX_FILE_SIZE / (1024 * 1024),
        },
        message="Supported formats listed.",
    )


# ─── Helpers ───
def _get_grade(score: float) -> str:
    if score >= 90:
        return "A+"
    elif score >= 80:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 50:
        return "D"
    else:
        return "F"
