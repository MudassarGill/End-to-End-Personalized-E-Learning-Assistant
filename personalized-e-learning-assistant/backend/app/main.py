"""
FastAPI Main Application - Personalized E-Learning Assistant
MongoDB Atlas integration, CORS, and complete lifecycle management.
"""

import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# ─── Load Environment Variables ───
# __file__ = backend/app/main.py → .parent.parent.parent = personalized-e-learning-assistant/
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# ─── Logging Setup ───
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("elearning")

# ─── MongoDB Connection (imported from models) ───
from app.models.user import db_manager


# ─── App Lifecycle ───
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events for MongoDB."""
    logger.info("Starting Personalized E-Learning Assistant...")
    await db_manager.connect()
    logger.info("MongoDB connected!")
    yield
    logger.info("Shutting down...")
    await db_manager.close()
    logger.info("MongoDB connection closed.")


# ─── FastAPI App ───
app = FastAPI(
    title="Personalized E-Learning Assistant",
    description=(
        "Upload PDFs, get AI summaries, keywords, and quizzes. "
        "Supports English and Urdu. Built for Pakistani students."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ─── CORS Middleware ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",     # React dev server
        "http://localhost:5173",     # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Prometheus Metrics ───
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        excluded_handlers=["/health", "/metrics"],
    ).instrument(app).expose(app, endpoint="/metrics", tags=["Monitoring"])
    logger.info("Prometheus metrics enabled at /metrics")
except ImportError:
    logger.info("prometheus-fastapi-instrumentator not installed. Metrics disabled.")


# ─── Include Routers ───
from app.routes.upload import router as upload_router

app.include_router(upload_router, prefix="/api", tags=["Upload & Processing"])


# ─── Root Endpoint ───
@app.get("/", tags=["Health"])
async def root():
    """Welcome endpoint."""
    return {
        "success": True,
        "message": "Personalized E-Learning Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "data": {
            "endpoints": {
                "upload_pdf": "POST /api/upload",
                "upload_text": "POST /api/upload/text",
                "submit_quiz": "POST /api/submit-quiz",
                "get_progress": "GET /api/progress/{user_id}",
                "get_quiz": "GET /api/quiz/{quiz_id}",
                "user_quizzes": "GET /api/user/{user_id}/quizzes",
                "supported_formats": "GET /api/supported-formats",
                "health": "GET /health",
            }
        },
    }


# ─── Health Check ───
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint — verifies MongoDB connectivity."""
    db_status = "disconnected"
    try:
        if db_manager.client:
            await db_manager.client.admin.command("ping")
            db_status = "connected"
    except Exception:
        db_status = "error"

    return {
        "success": db_status == "connected",
        "data": {
            "status": "healthy" if db_status == "connected" else "degraded",
            "database": db_status,
            "api": "running",
        },
        "message": (
            "All systems operational"
            if db_status == "connected"
            else "API running but database unavailable"
        ),
    }


# ─── Global Exception Handler ───
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler for unhandled errors."""
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "data": None,
            "message": "Internal server error",
            "error": str(exc),
        },
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "data": None,
            "message": f"Endpoint not found: {request.url.path}",
            "error": "Not Found",
        },
    )


@app.exception_handler(422)
async def validation_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "data": None,
            "message": "Invalid request data",
            "error": str(exc),
        },
    )


# ─── Run with uvicorn ───
if __name__ == "__main__":
    import uvicorn

    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", 8000))

    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
