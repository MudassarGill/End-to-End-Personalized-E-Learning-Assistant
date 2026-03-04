"""
╔══════════════════════════════════════════════════════════════╗
║   Personalized E-Learning Assistant - Complete Setup Script  ║
║   Windows Compatible | AWS S3 | DVC | Auto-Install          ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import json
import shutil
import subprocess
import hashlib
from pathlib import Path
from getpass import getpass

# ─────────────────────────────────────────────
#  COLORS & HELPERS
# ─────────────────────────────────────────────
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

def cprint(msg, color=Colors.RESET):
    print(f"{color}{msg}{Colors.RESET}")

def success(msg):
    cprint(f"  ✅ {msg}", Colors.GREEN)

def error(msg):
    cprint(f"  ❌ {msg}", Colors.RED)

def info(msg):
    cprint(f"  ℹ️  {msg}", Colors.CYAN)

def warning(msg):
    cprint(f"  ⚠️  {msg}", Colors.YELLOW)

def header(phase, title):
    print()
    cprint("=" * 60, Colors.MAGENTA)
    cprint(f"  PHASE {phase}: {title}", Colors.BOLD)
    cprint("=" * 60, Colors.MAGENTA)
    print()

def progress_bar(current, total, prefix="", length=40):
    pct = current / total if total > 0 else 1
    filled = int(length * pct)
    bar = "█" * filled + "░" * (length - filled)
    print(f"\r  📊 {prefix} |{bar}| {pct*100:.0f}%", end="", flush=True)
    if current >= total:
        print()

def run_cmd(cmd, cwd=None, check=True, capture=True):
    """Run shell command with error handling"""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, check=check,
            capture_output=capture, text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        error(f"Command failed: {cmd}")
        if e.stderr:
            error(f"  {e.stderr.strip()[:200]}")
        return None

# ─────────────────────────────────────────────
#  PROJECT ROOT
# ─────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.resolve()
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
ML_MODELS_DIR = PROJECT_ROOT / "ml_models"
DVC_DIR = PROJECT_ROOT / "dvc"
SAMPLE_DATA_DIR = BACKEND_DIR / "app" / "services" / "sample_data"
DATA_DIR = PROJECT_ROOT / "data" / "raw"

S3_BUCKET_NAME = "personalized-elearning-data"


# ═══════════════════════════════════════════════
#  PHASE 1: ENVIRONMENT SETUP
# ═══════════════════════════════════════════════
def phase1_environment_setup():
    header(1, "ENVIRONMENT SETUP")

    # ── Step 1.1: Create .env file ──
    info("Creating .env configuration file...")
    env_path = PROJECT_ROOT / ".env"

    print()
    cprint("  🔑 AWS Credentials Setup", Colors.BOLD)
    cprint("  (Press Enter to skip if you don't have AWS credentials yet)", Colors.YELLOW)
    print()

    aws_access_key = input("  AWS Access Key ID: ").strip()
    aws_secret_key = ""
    if aws_access_key:
        aws_secret_key = getpass("  AWS Secret Key: ").strip()
    aws_region = input("  AWS Region [us-east-1]: ").strip() or "us-east-1"

    mongo_url = input("  MongoDB URL [mongodb://localhost:27017]: ").strip() or "mongodb://localhost:27017"

    env_content = f"""# -------------------------------------------
# Personalized E-Learning Assistant - Config
# -------------------------------------------

# AWS Configuration
AWS_ACCESS_KEY_ID={aws_access_key}
AWS_SECRET_ACCESS_KEY={aws_secret_key}
AWS_REGION={aws_region}
S3_BUCKET_NAME={S3_BUCKET_NAME}

# MongoDB Configuration
MONGO_URL={mongo_url}
DATABASE_NAME=elearning_db

# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000/api
"""
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(env_content)
    success(f".env file created at: {env_path}")

    # ── Step 1.2: Virtual Environment ──
    print()
    info("Setting up Python virtual environment...")
    venv_path = PROJECT_ROOT / "venv"

    if not venv_path.exists():
        result = run_cmd(f'python -m venv "{venv_path}"')
        if result:
            success(f"Virtual environment created: {venv_path}")
        else:
            warning("Could not create venv. Using system Python.")
    else:
        success("Virtual environment already exists.")

    # Determine pip path
    if (venv_path / "Scripts" / "pip.exe").exists():
        pip_cmd = str(venv_path / "Scripts" / "pip")
        python_cmd = str(venv_path / "Scripts" / "python")
    else:
        pip_cmd = "pip"
        python_cmd = "python"

    # ── Step 1.3: Install Dependencies ──
    print()
    info("Installing backend dependencies...")
    req_file = BACKEND_DIR / "requirements.txt"
    if req_file.exists():
        result = run_cmd(f'"{pip_cmd}" install -r "{req_file}"')
        if result:
            success("Backend dependencies installed.")
        else:
            warning("Some backend dependencies may have failed. Continuing...")
    else:
        warning(f"requirements.txt not found at {req_file}")

    # Install additional packages needed for setup
    extra_packages = [
        "boto3",          # AWS SDK
        "python-dotenv",  # .env loading
        "tqdm",           # Progress bars
        "dvc",            # Data Version Control
        "dvc-s3",         # DVC S3 remote
        "requests",       # HTTP downloads
        "fpdf2",          # PDF generation
    ]
    info("Installing additional setup dependencies...")
    for i, pkg in enumerate(extra_packages):
        progress_bar(i, len(extra_packages), prefix=f"Installing {pkg}")
        run_cmd(f'"{pip_cmd}" install {pkg}', capture=True)
    progress_bar(len(extra_packages), len(extra_packages), prefix="Done")
    success("Additional dependencies installed.")

    # ML Models requirements
    print()
    ml_req = ML_MODELS_DIR / "requirements.txt"
    if ml_req.exists():
        info("Installing ML model dependencies...")
        result = run_cmd(f'"{pip_cmd}" install -r "{ml_req}"')
        if result:
            success("ML dependencies installed.")
        else:
            warning("Some ML dependencies may have failed.")

    return pip_cmd, python_cmd


# ═══════════════════════════════════════════════
#  PHASE 2: AWS S3 SETUP
# ═══════════════════════════════════════════════
def phase2_aws_s3_setup():
    header(2, "AWS S3 SETUP")

    # Load .env
    env_path = PROJECT_ROOT / ".env"
    aws_key = ""
    aws_secret = ""
    aws_region = "us-east-1"

    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("AWS_ACCESS_KEY_ID="):
                    aws_key = line.split("=", 1)[1]
                elif line.startswith("AWS_SECRET_ACCESS_KEY="):
                    aws_secret = line.split("=", 1)[1]
                elif line.startswith("AWS_REGION="):
                    aws_region = line.split("=", 1)[1]

    if not aws_key or not aws_secret:
        warning("AWS credentials not provided. Skipping S3 setup.")
        warning("You can re-run setup later after adding credentials to .env")
        return False

    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
    except ImportError:
        run_cmd("pip install boto3")
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError

    # ── Step 2.1: Check/Create S3 Bucket ──
    info(f"Checking S3 bucket: {S3_BUCKET_NAME}...")
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_secret,
            region_name=aws_region,
        )

        # Check if bucket exists
        try:
            s3.head_bucket(Bucket=S3_BUCKET_NAME)
            success(f"Bucket '{S3_BUCKET_NAME}' exists!")
        except ClientError:
            info(f"Creating bucket '{S3_BUCKET_NAME}'...")
            if aws_region == "us-east-1":
                s3.create_bucket(Bucket=S3_BUCKET_NAME)
            else:
                s3.create_bucket(
                    Bucket=S3_BUCKET_NAME,
                    CreateBucketConfiguration={"LocationConstraint": aws_region},
                )
            success(f"Bucket '{S3_BUCKET_NAME}' created!")

        # ── Step 2.2: Create Folder Structure ──
        print()
        info("Creating S3 folder structure...")
        folders = ["raw-pdfs/", "raw-notes/", "processed/", "models/", "dvc-store/"]
        for i, folder in enumerate(folders):
            s3.put_object(Bucket=S3_BUCKET_NAME, Key=folder, Body="")
            progress_bar(i + 1, len(folders), prefix=f"Creating {folder}")
        success("S3 folder structure created!")

        # ── Step 2.3: Connection Test ──
        print()
        info("Testing S3 connection...")
        test_key = "connection-test.txt"
        s3.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=test_key,
            Body=f"Connection test - {time.strftime('%Y-%m-%d %H:%M:%S')}",
        )
        s3.delete_object(Bucket=S3_BUCKET_NAME, Key=test_key)
        success("S3 connection test passed! ✨")

        return True

    except NoCredentialsError:
        error("Invalid AWS credentials. Please check your .env file.")
        return False
    except Exception as e:
        error(f"AWS S3 error: {e}")
        return False


# ═══════════════════════════════════════════════
#  PHASE 3: SAMPLE DATA DOWNLOAD
# ═══════════════════════════════════════════════
def phase3_sample_data():
    header(3, "SAMPLE DATA DOWNLOAD & GENERATION")

    os.makedirs(SAMPLE_DATA_DIR, exist_ok=True)
    os.makedirs(DATA_DIR / "pdfs", exist_ok=True)
    os.makedirs(DATA_DIR / "notes", exist_ok=True)
    os.makedirs(DATA_DIR / "texts", exist_ok=True)

    # ── Step 3.1: Create Sample Notes ──
    info("Creating sample educational notes...")

    notes = {
        "machine_learning.txt": """\
Machine Learning Fundamentals
=============================
Supervised Learning: The model learns from labeled data.
  - Classification: Predicting categories (spam vs not spam)
  - Regression: Predicting continuous values (house prices)
  - Common algorithms: Linear Regression, Decision Trees, SVM, Random Forest

Unsupervised Learning: The model finds patterns in unlabeled data.
  - Clustering: Grouping similar items (K-Means, DBSCAN)
  - Dimensionality Reduction: PCA, t-SNE

Reinforcement Learning: Agent learns by interacting with environment.
  - Q-Learning, Deep Q-Networks (DQN)

Evaluation Metrics:
  - Accuracy, Precision, Recall, F1-Score
  - ROC-AUC curve, Confusion Matrix
  - Mean Squared Error (MSE) for regression
""",
        "deep_learning.txt": """\
Deep Learning Concepts
======================
Neural Networks: Inspired by the human brain.
  - Input layer: Receives the data
  - Hidden layers: Process the information
  - Output layer: Produces the result
  - Activation Functions: ReLU, Sigmoid, Tanh, Softmax

CNNs: Specialized for image processing.
  - Convolution layers extract features using filters
  - Pooling layers reduce dimensionality

RNNs: Designed for sequential data.
  - LSTM: Long Short-Term Memory (solves vanishing gradient)
  - GRU: Gated Recurrent Units

Transformers: Modern architecture for NLP.
  - Self-attention mechanism
  - Multi-head attention
  - Examples: BERT, GPT, T5
""",
        "nlp_concepts.txt": """\
Natural Language Processing (NLP)
=================================
Text Preprocessing:
  - Tokenization: Breaking text into words/sentences
  - Stop word removal, Stemming, Lemmatization
  - TF-IDF: Term Frequency-Inverse Document Frequency

Word Embeddings:
  - Word2Vec (CBOW, Skip-gram)
  - GloVe, FastText

NLP Tasks:
  - Sentiment Analysis: Determining opinion polarity
  - Named Entity Recognition (NER): Identifying entities
  - Machine Translation: Converting between languages
  - Text Summarization: Extractive vs Abstractive
  - Question Answering: Finding answers in text

Modern NLP Models:
  - BERT: Bidirectional Encoder Representations
  - GPT: Generative Pre-trained Transformer
  - T5: Text-to-Text Transfer Transformer
""",
        "python_basics.txt": """\
Python Programming Basics
=========================
Data Types: int, float, str, bool, list, tuple, dict, set

Control Flow:
  - if/elif/else for conditional logic
  - for loops for iteration
  - while loops for conditional iteration

Functions:
  - def keyword for definition
  - *args and **kwargs for variable arguments
  - Lambda functions: anonymous single-expression functions

Object-Oriented Programming:
  - Classes and Objects
  - Inheritance, Polymorphism, Encapsulation
  - Magic methods: __init__, __str__, __repr__

File Handling:
  - open(), read(), write(), close()
  - Context managers: with statement

Popular Libraries:
  - NumPy, Pandas, Matplotlib
  - Scikit-learn, TensorFlow, PyTorch
""",
        # ── Pakistan Education ──
        "islamiat_notes.txt": """\
Islamiat - Basic Teachings
==========================
Arkan-e-Islam (Five Pillars):
  1. Shahada: La ilaha illallah Muhammadur Rasulullah
  2. Salat: Five daily prayers (Fajr, Zuhr, Asr, Maghrib, Isha)
  3. Sawm: Fasting in Ramadan
  4. Zakat: 2.5% of savings for the poor
  5. Hajj: Pilgrimage to Makkah

Seerat-un-Nabi (PBUH):
  - Born: 571 CE in Makkah
  - First revelation: Cave Hira, 610 CE
  - Hijrah: Migration to Madinah, 622 CE
  - Conquest of Makkah: 630 CE

Khulafa-e-Rashideen:
  1. Hazrat Abu Bakr Siddiq (RA): 632-634 CE
  2. Hazrat Umar Farooq (RA): 634-644 CE
  3. Hazrat Usman Ghani (RA): 644-656 CE
  4. Hazrat Ali (RA): 656-661 CE
""",
        "pak_studies_notes.txt": """\
Pakistan Studies
================
Pakistan Movement:
  - 1906: All India Muslim League founded in Dhaka
  - 1930: Allama Iqbal's Allahabad Address
  - 1940: Lahore Resolution (23 March)
  - 1947: Pakistan created (14 August)

Quaid-e-Azam Muhammad Ali Jinnah:
  - Born: 25 December 1876, Karachi
  - First Governor General of Pakistan
  - Died: 11 September 1948

Geography:
  - Capital: Islamabad
  - Provinces: Punjab, Sindh, KPK, Balochistan
  - K2: Second highest peak (8,611m)
  - Indus River System: Lifeline of Pakistan
""",
        "math_notes.txt": """\
Mathematics - Key Formulas
===========================
Algebra:
  - Quadratic Formula: x = (-b +/- sqrt(b^2 - 4ac)) / 2a
  - Factoring: x^2 + 5x + 6 = (x+2)(x+3)
  - Laws of Exponents: a^m * a^n = a^(m+n)

Geometry:
  - Triangle Area: (1/2) * base * height
  - Circle Area: pi * r^2
  - Pythagoras: a^2 + b^2 = c^2

Trigonometry:
  - sin(theta) = opposite / hypotenuse
  - cos(theta) = adjacent / hypotenuse
  - tan(theta) = opposite / adjacent
  - sin^2(theta) + cos^2(theta) = 1
""",
        "english_notes.txt": """\
English Grammar Notes
=====================
Parts of Speech:
  - Noun: person, place, thing (Ali, Lahore, book)
  - Verb: action word (run, study, write)
  - Adjective: describes noun (beautiful, tall)
  - Adverb: describes verb (quickly, slowly)

Tenses:
  - Present Simple: I study every day
  - Past Simple: I studied yesterday
  - Future Simple: I will study tomorrow
  - Present Perfect: I have studied

Active/Passive Voice:
  - Active: The teacher teaches students
  - Passive: Students are taught by the teacher

Direct/Indirect Speech:
  - Direct: He said, "I am going."
  - Indirect: He said that he was going.
""",
    }

    for i, (fname, content) in enumerate(notes.items()):
        # Save to sample_data and data/raw/notes
        for folder in [SAMPLE_DATA_DIR, DATA_DIR / "notes"]:
            with open(folder / fname, "w", encoding="utf-8") as f:
                f.write(content)
        progress_bar(i + 1, len(notes), prefix=f"Creating {fname}")
    success(f"Created {len(notes)} sample notes!")

    # ── Step 3.2: Create Sample PDFs ──
    print()
    info("Generating sample PDF textbooks...")

    try:
        from fpdf import FPDF
    except ImportError:
        run_cmd("pip install fpdf2")
        from fpdf import FPDF

    pdf_data = {
        "ml_basics_textbook.pdf": {
            "title": "Machine Learning Basics",
            "chapters": [
                ("Ch1: Introduction to ML", [
                    "Machine Learning is a subset of AI that enables computers to learn from data without being explicitly programmed.",
                    "Types: Supervised Learning uses labeled data, Unsupervised Learning finds hidden patterns, Reinforcement Learning learns through rewards.",
                ]),
                ("Ch2: Algorithms", [
                    "Linear Regression predicts continuous values. Decision Trees split data based on feature thresholds.",
                    "Random Forest combines multiple decision trees. SVM finds optimal hyperplane for classification.",
                ]),
            ],
        },
        "python_tutorial.pdf": {
            "title": "Python Programming Tutorial",
            "chapters": [
                ("Ch1: Python Basics", [
                    "Python is a high-level interpreted language. Variables store data: x = 10, name = 'Ali'.",
                    "Data types: int, float, str, bool, list, tuple, dict. Use type() to check.",
                ]),
                ("Ch2: Control Flow", [
                    "If statements: if condition: action. For loops: for item in iterable: action.",
                    "Functions: def my_func(param): return result. Lambda: lambda x: x*2.",
                ]),
            ],
        },
        "islamiat_textbook.pdf": {
            "title": "Islamiat - Study Guide",
            "chapters": [
                ("Ch1: Arkan-e-Islam", [
                    "Shahada is the declaration of faith. Salat consists of five daily prayers. Sawm is fasting in Ramadan.",
                    "Zakat is giving 2.5 percent of savings. Hajj is the pilgrimage to Makkah.",
                ]),
                ("Ch2: Seerat-un-Nabi", [
                    "Prophet Muhammad (PBUH) was born in 571 CE. First revelation came in Cave Hira in 610 CE.",
                    "Hijrah to Madinah in 622 CE. Conquest of Makkah in 630 CE. Farewell Sermon in 632 CE.",
                ]),
            ],
        },
        "pakistan_studies_textbook.pdf": {
            "title": "Pakistan Studies Guide",
            "chapters": [
                ("Ch1: Pakistan Movement", [
                    "Allama Iqbal proposed separate Muslim state in 1930 Allahabad Address. Lahore Resolution passed on 23 March 1940.",
                    "Pakistan was created on 14 August 1947. Quaid-e-Azam became the first Governor General.",
                ]),
                ("Ch2: Geography", [
                    "Pakistan has four provinces: Punjab, Sindh, KPK, and Balochistan. Capital is Islamabad.",
                    "K2 at 8,611 meters is the second highest peak. Indus River is the lifeline of Pakistan.",
                ]),
            ],
        },
        "science_textbook.pdf": {
            "title": "General Science - Study Guide",
            "chapters": [
                ("Ch1: Physics", [
                    "Newton First Law: Objects at rest stay at rest. F = ma. Every action has equal and opposite reaction.",
                    "Work = Force times Distance. KE = half mv squared. Ohm Law: V = IR.",
                ]),
                ("Ch2: Chemistry and Biology", [
                    "Atoms consist of protons, neutrons, and electrons. Ionic bonds form by electron transfer.",
                    "Photosynthesis: CO2 + H2O + light gives glucose + O2. Respiration releases ATP energy.",
                ]),
            ],
        },
    }

    for i, (fname, data) in enumerate(pdf_data.items()):
        try:
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 22)
            pdf.ln(50)
            pdf.cell(0, 12, data["title"], ln=True, align="C")
            pdf.set_font("Helvetica", "", 11)
            pdf.ln(8)
            pdf.cell(0, 8, "Personalized E-Learning Assistant", ln=True, align="C")

            for ch_title, paras in data["chapters"]:
                pdf.add_page()
                pdf.set_font("Helvetica", "B", 15)
                pdf.cell(0, 10, ch_title, ln=True)
                pdf.ln(4)
                pdf.set_font("Helvetica", "", 11)
                for p in paras:
                    pdf.multi_cell(0, 7, p)
                    pdf.ln(3)

            out_path = DATA_DIR / "pdfs" / fname
            pdf.output(str(out_path))
            size_kb = os.path.getsize(out_path) / 1024
            progress_bar(i + 1, len(pdf_data), prefix=f"{fname} ({size_kb:.1f}KB)")
        except Exception as e:
            error(f"Failed to create {fname}: {e}")

    success(f"Created {len(pdf_data)} sample PDFs!")

    # ── Step 3.3: Download arXiv Papers ──
    print()
    info("Downloading sample research papers from arXiv...")
    import requests

    arxiv_papers = [
        ("arxiv_attention_is_all_you_need.pdf", "https://arxiv.org/pdf/1706.03762"),
        ("arxiv_bert_paper.pdf", "https://arxiv.org/pdf/1810.04805"),
        ("arxiv_gpt2_paper.pdf", "https://arxiv.org/pdf/2005.14165"),
        ("arxiv_resnet_paper.pdf", "https://arxiv.org/pdf/1512.03385"),
        ("arxiv_adam_optimizer.pdf", "https://arxiv.org/pdf/1412.6980"),
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
    }

    downloaded = 0
    for i, (fname, url) in enumerate(arxiv_papers):
        save_path = DATA_DIR / "pdfs" / fname
        try:
            resp = requests.get(url, headers=headers, timeout=30, stream=True)
            if resp.status_code == 200:
                with open(save_path, "wb") as f:
                    for chunk in resp.iter_content(8192):
                        f.write(chunk)
                size_kb = os.path.getsize(save_path) / 1024
                downloaded += 1
                progress_bar(i + 1, len(arxiv_papers), prefix=f"{fname} ({size_kb:.1f}KB)")
            else:
                progress_bar(i + 1, len(arxiv_papers), prefix=f"{fname} (SKIP)")
        except Exception:
            progress_bar(i + 1, len(arxiv_papers), prefix=f"{fname} (FAIL)")

    if downloaded > 0:
        success(f"Downloaded {downloaded}/{len(arxiv_papers)} arXiv papers!")
    else:
        warning("No arXiv papers downloaded (network issue). Sample PDFs are still available.")

    return True


# ═══════════════════════════════════════════════
#  PHASE 4: DATA UPLOAD & VERSION CONTROL
# ═══════════════════════════════════════════════
def phase4_data_versioning(s3_available):
    header(4, "DATA UPLOAD & VERSION CONTROL")

    # ── Step 4.1: Upload to S3 ──
    if s3_available:
        info("Uploading data to S3...")
        try:
            import boto3

            # Read credentials from .env
            env_path = PROJECT_ROOT / ".env"
            aws_key = aws_secret = aws_region = ""
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("AWS_ACCESS_KEY_ID="):
                        aws_key = line.split("=", 1)[1]
                    elif line.startswith("AWS_SECRET_ACCESS_KEY="):
                        aws_secret = line.split("=", 1)[1]
                    elif line.startswith("AWS_REGION="):
                        aws_region = line.split("=", 1)[1]

            s3 = boto3.client(
                "s3",
                aws_access_key_id=aws_key,
                aws_secret_access_key=aws_secret,
                region_name=aws_region,
            )

            # Upload notes
            notes_dir = DATA_DIR / "notes"
            if notes_dir.exists():
                files = list(notes_dir.glob("*"))
                for i, f in enumerate(files):
                    s3.upload_file(str(f), S3_BUCKET_NAME, f"raw-notes/{f.name}")
                    progress_bar(i + 1, len(files), prefix=f"Notes: {f.name}")
                success(f"Uploaded {len(files)} notes to S3!")

            # Upload PDFs
            pdfs_dir = DATA_DIR / "pdfs"
            if pdfs_dir.exists():
                files = list(pdfs_dir.glob("*.pdf"))
                for i, f in enumerate(files):
                    s3.upload_file(str(f), S3_BUCKET_NAME, f"raw-pdfs/{f.name}")
                    progress_bar(i + 1, len(files), prefix=f"PDFs: {f.name}")
                success(f"Uploaded {len(files)} PDFs to S3!")

        except Exception as e:
            warning(f"S3 upload failed: {e}")
    else:
        warning("S3 not configured. Skipping upload. Data saved locally.")

    # ── Step 4.2: DVC Init ──
    print()
    info("Initializing DVC (Data Version Control)...")

    # Git init first (DVC needs git)
    git_dir = PROJECT_ROOT / ".git"
    if not git_dir.exists():
        info("Initializing Git repository...")
        run_cmd("git init", cwd=str(PROJECT_ROOT))
        success("Git repository initialized!")

        # Create .gitignore
        gitignore_content = """\
# Python
venv/
__pycache__/
*.pyc
.env

# Data (tracked by DVC)
/data/

# Node
node_modules/
frontend/node_modules/

# ML Models (large files)
*.bin
*.pt
*.h5

# OS
.DS_Store
Thumbs.db
"""
        with open(PROJECT_ROOT / ".gitignore", "w", encoding="utf-8") as f:
            f.write(gitignore_content)
        success(".gitignore created!")
    else:
        success("Git repository already exists.")

    # DVC init
    dvc_dir = PROJECT_ROOT / ".dvc"
    if not dvc_dir.exists():
        result = run_cmd("dvc init", cwd=str(PROJECT_ROOT))
        if result:
            success("DVC initialized!")
        else:
            warning("DVC init failed. You can run 'dvc init' manually later.")
    else:
        success("DVC already initialized.")

    # ── Step 4.3: Add S3 remote ──
    if s3_available:
        print()
        info("Adding S3 as DVC remote storage...")
        run_cmd(
            f'dvc remote add -d s3remote s3://{S3_BUCKET_NAME}/dvc-store',
            cwd=str(PROJECT_ROOT),
        )
        success(f"DVC remote added: s3://{S3_BUCKET_NAME}/dvc-store")

    # ── Step 4.4: Track data with DVC ──
    print()
    info("Tracking data directory with DVC...")
    data_path = PROJECT_ROOT / "data"
    if data_path.exists():
        result = run_cmd(f'dvc add "{data_path}"', cwd=str(PROJECT_ROOT))
        if result:
            success("Data tracked with DVC!")
        else:
            warning("DVC tracking skipped. You can run 'dvc add data' manually.")

    # ── Step 4.5: Git commit ──
    print()
    info("Creating initial Git commit...")
    run_cmd("git add -A", cwd=str(PROJECT_ROOT))
    run_cmd(
        'git commit -m "Initial setup: project structure, sample data, DVC config"',
        cwd=str(PROJECT_ROOT),
    )
    success("Initial Git commit created!")


# ═══════════════════════════════════════════════
#  PHASE 5: VERIFICATION
# ═══════════════════════════════════════════════
def phase5_verification(s3_available):
    header(5, "VERIFICATION & FINAL REPORT")

    report = []

    # ── 5.1: Check local files ──
    info("Checking local files...")
    checks = {
        "Backend main.py": BACKEND_DIR / "app" / "main.py",
        "Upload route": BACKEND_DIR / "app" / "routes" / "upload.py",
        "Text extraction": BACKEND_DIR / "app" / "services" / "text_extraction.py",
        "Summarizer": BACKEND_DIR / "app" / "services" / "summarizer.py",
        "Keywords": BACKEND_DIR / "app" / "services" / "keywords.py",
        "Quiz generator": BACKEND_DIR / "app" / "services" / "quiz_generator.py",
        "Frontend App.jsx": FRONTEND_DIR / "src" / "App.jsx",
        "Docker Compose": PROJECT_ROOT / "docker-compose.yml",
        "Kubernetes": PROJECT_ROOT / "k8s" / "deployment.yaml",
        ".env config": PROJECT_ROOT / ".env",
    }

    all_ok = True
    for name, path in checks.items():
        if path.exists():
            success(f"{name}")
            report.append(f"✅ {name}: {path.name}")
        else:
            error(f"{name} — MISSING!")
            report.append(f"❌ {name}: MISSING")
            all_ok = False

    # ── 5.2: Check data files ──
    print()
    info("Checking data files...")
    notes_count = len(list((DATA_DIR / "notes").glob("*"))) if (DATA_DIR / "notes").exists() else 0
    pdfs_count = len(list((DATA_DIR / "pdfs").glob("*.pdf"))) if (DATA_DIR / "pdfs").exists() else 0
    texts_count = len(list((DATA_DIR / "texts").glob("*"))) if (DATA_DIR / "texts").exists() else 0

    success(f"Notes: {notes_count} files")
    success(f"PDFs: {pdfs_count} files")
    success(f"Texts: {texts_count} files")

    total_data = notes_count + pdfs_count + texts_count

    # ── 5.3: Check S3 ──
    if s3_available:
        print()
        info("Checking S3 bucket contents...")
        try:
            import boto3

            env_path = PROJECT_ROOT / ".env"
            aws_key = aws_secret = aws_region = ""
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("AWS_ACCESS_KEY_ID="):
                        aws_key = line.split("=", 1)[1]
                    elif line.startswith("AWS_SECRET_ACCESS_KEY="):
                        aws_secret = line.split("=", 1)[1]
                    elif line.startswith("AWS_REGION="):
                        aws_region = line.split("=", 1)[1]

            s3 = boto3.client(
                "s3",
                aws_access_key_id=aws_key,
                aws_secret_access_key=aws_secret,
                region_name=aws_region,
            )
            response = s3.list_objects_v2(Bucket=S3_BUCKET_NAME)
            s3_count = response.get("KeyCount", 0)
            success(f"S3 bucket has {s3_count} objects!")
            report.append(f"✅ S3: {s3_count} objects in bucket")
        except Exception as e:
            warning(f"S3 check failed: {e}")

    # ── 5.4: Check DVC ──
    print()
    info("Checking DVC status...")
    result = run_cmd("dvc status", cwd=str(PROJECT_ROOT))
    if result and result.returncode == 0:
        success("DVC is configured and tracking data!")
    else:
        warning("DVC status check skipped.")

    # ── 5.5: Check environment ──
    print()
    info("Checking environment...")
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        success(".env file exists")
    venv_path = PROJECT_ROOT / "venv"
    if venv_path.exists():
        success("Virtual environment exists")

    # ═══ FINAL REPORT ═══
    print()
    cprint("╔" + "═" * 58 + "╗", Colors.GREEN)
    cprint("║" + "  📊 FINAL SETUP REPORT".center(58) + "║", Colors.GREEN)
    cprint("╚" + "═" * 58 + "╝", Colors.GREEN)

    print()
    cprint(f"  📁 Project Root:   {PROJECT_ROOT}", Colors.CYAN)
    cprint(f"  📝 Total Notes:    {notes_count} files", Colors.CYAN)
    cprint(f"  📄 Total PDFs:     {pdfs_count} files", Colors.CYAN)
    cprint(f"  📊 Total Data:     {total_data} files", Colors.CYAN)
    cprint(f"  🗂️  S3 Bucket:     {S3_BUCKET_NAME}", Colors.CYAN)
    cprint(f"  📦 DVC:            {'Configured' if (PROJECT_ROOT / '.dvc').exists() else 'Not configured'}", Colors.CYAN)
    cprint(f"  🐍 Virtual Env:    {'Yes' if venv_path.exists() else 'No'}", Colors.CYAN)

    print()
    if all_ok and total_data > 0:
        cprint("  ✅ SETUP COMPLETE! Project ready for development. 🚀", Colors.GREEN + Colors.BOLD)
    else:
        cprint("  ⚠️  Setup completed with some warnings. Check above for details.", Colors.YELLOW)

    print()
    cprint("  Next Steps:", Colors.BOLD)
    cprint("  1. cd backend && uvicorn app.main:app --reload", Colors.CYAN)
    cprint("  2. cd frontend && npm install && npm start", Colors.CYAN)
    cprint("  3. Open http://localhost:3000 in browser", Colors.CYAN)
    cprint("  4. Upload any PDF/DOCX/TXT and get results!", Colors.CYAN)
    print()


# ═══════════════════════════════════════════════
#  MAIN ENTRY POINT
# ═══════════════════════════════════════════════
def main():
    os.system("cls" if os.name == "nt" else "clear")

    cprint("╔" + "═" * 58 + "╗", Colors.MAGENTA)
    cprint("║" + "  📚 Personalized E-Learning Assistant".center(58) + "║", Colors.MAGENTA)
    cprint("║" + "  Complete Setup Script v1.0".center(58) + "║", Colors.MAGENTA)
    cprint("║" + "  Windows Compatible | AWS S3 | DVC".center(58) + "║", Colors.MAGENTA)
    cprint("╚" + "═" * 58 + "╝", Colors.MAGENTA)

    print()
    cprint(f"  📁 Project: {PROJECT_ROOT}", Colors.CYAN)
    cprint(f"  🖥️  OS: {sys.platform}", Colors.CYAN)
    cprint(f"  🐍 Python: {sys.version.split()[0]}", Colors.CYAN)
    print()

    input("  Press ENTER to start setup... ")

    # Phase 1
    pip_cmd, python_cmd = phase1_environment_setup()

    # Phase 2
    s3_ok = phase2_aws_s3_setup()

    # Phase 3
    phase3_sample_data()

    # Phase 4
    phase4_data_versioning(s3_ok)

    # Phase 5
    phase5_verification(s3_ok)


if __name__ == "__main__":
    main()
