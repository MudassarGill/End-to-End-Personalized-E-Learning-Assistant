# FastAPI main application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import upload

app = FastAPI(
    title="Personalized E-Learning Assistant",
    description="An AI-powered e-learning platform that provides personalized summaries, keywords, and quizzes from uploaded PDFs.",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["Upload & Processing"])


@app.get("/")
async def root():
    return {"message": "Welcome to the Personalized E-Learning Assistant API"}
