# Upload & processing endpoints
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.text_extraction import extract_text_from_pdf
from app.services.summarizer import generate_summary
from app.services.keywords import extract_keywords
from app.services.quiz_generator import generate_quiz

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a PDF and process it for summaries, keywords, and quizzes."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    content = await file.read()

    # Extract text
    text = extract_text_from_pdf(content)

    # Generate outputs
    summary = generate_summary(text)
    keywords = extract_keywords(text)
    quiz = generate_quiz(text)

    return {
        "filename": file.filename,
        "summary": summary,
        "keywords": keywords,
        "quiz": quiz,
    }
