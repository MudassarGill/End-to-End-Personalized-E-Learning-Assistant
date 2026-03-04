# 📚 Personalized E-Learning Assistant

An AI-powered e-learning platform that lets users upload PDFs and receive **personalized summaries**, **keyword extraction**, and **auto-generated quizzes** to enhance their learning experience.

## 🏗️ Architecture

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI (Python) |
| **Frontend** | React.js |
| **Database** | MongoDB |
| **ML/NLP** | HuggingFace Transformers, scikit-learn |
| **Containerization** | Docker & Docker Compose |
| **Orchestration** | Kubernetes |
| **Data Versioning** | DVC |

## 📁 Project Structure

```
personalized-e-learning-assistant/
├─ backend/                  # FastAPI backend
│  ├─ app/
│  │  ├─ main.py             # App entry point
│  │  ├─ routes/upload.py    # Upload & processing API
│  │  ├─ models/user.py      # MongoDB user models
│  │  ├─ services/           # AI/ML processing services
│  │  └─ utils.py            # Shared utilities
│  ├─ requirements.txt
│  └─ Dockerfile
├─ frontend/                 # React frontend
│  ├─ src/
│  │  ├─ components/         # UI components
│  │  ├─ App.jsx
│  │  ├─ api.js
│  │  └─ App.css
│  ├─ package.json
│  └─ Dockerfile
├─ ml_models/                # Saved ML/NLP models
├─ dvc/                      # DVC tracked data & models
├─ k8s/                      # Kubernetes manifests
├─ docker-compose.yml
└─ README.md
```

## 🚀 Quick Start

### Using Docker Compose
```bash
docker-compose up --build
```
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

### Manual Setup

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

## 🔑 Features

- **PDF Upload** — Upload study materials in PDF format
- **AI Summarization** — Get concise summaries using BART
- **Keyword Extraction** — Identify key topics with TF-IDF
- **Quiz Generation** — Auto-generated MCQs to test understanding
- **Progress Tracking** — Dashboard to monitor learning progress

## 📄 License

MIT
