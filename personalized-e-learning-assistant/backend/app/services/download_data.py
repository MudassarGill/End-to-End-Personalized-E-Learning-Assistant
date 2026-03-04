# personalized-e-learning-assistant/backend/services/download_data.py
# Locally generates all sample data — no internet required!

import os
from pathlib import Path


class DataDownloader:
    def __init__(self):
        # Project root
        self.base_dir = Path(__file__).parent.parent.parent.parent
        self.raw_pdfs_dir = self.base_dir / "data" / "raw" / "pdfs"
        self.raw_texts_dir = self.base_dir / "data" / "raw" / "texts"
        self.raw_notes_dir = self.base_dir / "data" / "raw" / "notes"

        # Folders create karo
        os.makedirs(self.raw_pdfs_dir, exist_ok=True)
        os.makedirs(self.raw_texts_dir, exist_ok=True)
        os.makedirs(self.raw_notes_dir, exist_ok=True)

        print(f"✅ Created folders in: {self.base_dir / 'data' / 'raw'}")

    # ──────────────────────────────────────────────
    #  1. Sample Notes (plain text)
    # ──────────────────────────────────────────────
    def create_sample_notes(self):
        """Testing ke liye sample notes create karo"""

        notes_data = {
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
  - Association: Finding relationships between variables

Semi-Supervised Learning: Combines small labeled data with large unlabeled data.

Reinforcement Learning: Agent learns by interacting with environment.
  - Reward and punishment mechanism
  - Q-Learning, Deep Q-Networks

Evaluation Metrics:
  - Accuracy, Precision, Recall, F1-Score
  - ROC-AUC curve
  - Mean Squared Error (MSE) for regression
""",
            "deep_learning.txt": """\
Deep Learning Concepts
======================

Neural Networks: Inspired by the human brain, consists of layers of interconnected neurons.
  - Input layer: Receives the data
  - Hidden layers: Process the information
  - Output layer: Produces the result
  - Activation Functions: ReLU, Sigmoid, Tanh, Softmax

Convolutional Neural Networks (CNNs): Specialized for processing grid-like data (images).
  - Convolution layers: Extract features using filters
  - Pooling layers: Reduce dimensionality (MaxPool, AvgPool)
  - Fully connected layers: Make predictions
  - Applications: Image classification, Object detection, Face recognition

Recurrent Neural Networks (RNNs): Designed for sequential data (text, time series).
  - LSTM: Long Short-Term Memory networks (solves vanishing gradient)
  - GRU: Gated Recurrent Units (lighter alternative to LSTM)
  - Bidirectional RNNs: Process sequence in both directions

Transformers: Modern architecture for NLP tasks.
  - Self-attention mechanism
  - Positional encoding
  - Multi-head attention
  - Examples: BERT, GPT, T5
""",
            "python_programming.txt": """\
Python Programming Notes
========================

Data Types:
  - int, float, str, bool
  - list, tuple, dict, set
  - None type

Control Flow:
  - if/elif/else statements
  - for loops and while loops
  - break, continue, pass

Functions:
  - def keyword for function definition
  - *args and **kwargs for variable arguments
  - Lambda functions for anonymous functions
  - Decorators for modifying function behavior

Object-Oriented Programming:
  - Classes and Objects
  - Inheritance (single, multiple)
  - Polymorphism and Encapsulation
  - Magic methods (__init__, __str__, __repr__)

File Handling:
  - open(), read(), write(), close()
  - Context managers (with statement)
  - CSV and JSON file processing

Popular Libraries:
  - NumPy: Numerical computing
  - Pandas: Data manipulation
  - Matplotlib: Data visualization
  - Scikit-learn: Machine learning
  - TensorFlow/PyTorch: Deep learning
""",
            "data_science.txt": """\
Data Science Pipeline
=====================

1. Problem Definition
   - Understand the business problem
   - Define success metrics
   - Identify stakeholders

2. Data Collection
   - APIs, web scraping, databases
   - Surveys, sensors, logs
   - Public datasets (Kaggle, UCI)

3. Data Cleaning & Preprocessing
   - Handle missing values (imputation, deletion)
   - Remove duplicates
   - Fix data types
   - Handle outliers (IQR, Z-score)

4. Exploratory Data Analysis (EDA)
   - Univariate analysis (histograms, box plots)
   - Bivariate analysis (scatter plots, correlation)
   - Feature engineering
   - Statistical tests

5. Model Building
   - Train/test split
   - Cross-validation
   - Hyperparameter tuning (Grid Search, Random Search)
   - Model selection

6. Evaluation
   - Classification: Accuracy, Precision, Recall, F1
   - Regression: MAE, MSE, RMSE, R-squared
   - Confusion matrix

7. Deployment
   - Flask/FastAPI for API
   - Docker for containerization
   - CI/CD pipelines
   - Monitoring and retraining
""",
            "natural_language_processing.txt": """\
Natural Language Processing (NLP)
=================================

Text Preprocessing:
  - Tokenization: Breaking text into words/sentences
  - Lowercasing and removing punctuation
  - Stop word removal
  - Stemming (Porter, Snowball)
  - Lemmatization (WordNet)

Feature Extraction:
  - Bag of Words (BoW)
  - TF-IDF (Term Frequency-Inverse Document Frequency)
  - Word2Vec (CBOW, Skip-gram)
  - GloVe embeddings
  - FastText

NLP Tasks:
  - Text Classification (sentiment analysis, spam detection)
  - Named Entity Recognition (NER)
  - Machine Translation
  - Question Answering
  - Text Summarization (extractive vs abstractive)
  - Chatbots and Dialogue Systems

Modern NLP:
  - BERT: Bidirectional Encoder Representations from Transformers
  - GPT: Generative Pre-trained Transformer
  - T5: Text-to-Text Transfer Transformer
  - Fine-tuning pre-trained models
  - Prompt engineering
""",
        }

        print("\n📝 Creating sample notes...")
        for filename, content in notes_data.items():
            file_path = self.raw_notes_dir / filename
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  ✅ Created: {filename}")

    # ──────────────────────────────────────────────
    #  2. Sample Text Files (longer educational content)
    # ──────────────────────────────────────────────
    def create_sample_texts(self):
        """Detailed educational text files create karo"""

        texts = {
            "introduction_to_ai.txt": """\
Introduction to Artificial Intelligence
========================================

Artificial Intelligence (AI) is the simulation of human intelligence processes by computer
systems. These processes include learning (the acquisition of information and rules for using
the information), reasoning (using rules to reach approximate or definite conclusions), and
self-correction.

History of AI:
The term Artificial Intelligence was coined by John McCarthy in 1956 at the Dartmouth
Conference. Early AI research focused on problem solving and symbolic methods. In the 1960s,
the US Department of Defense took interest in this type of work and began training computers
to mimic basic human reasoning.

Types of AI:
1. Narrow AI (Weak AI): Designed for a specific task (e.g., Siri, Alexa, chess engines).
   These systems can only perform the specific task they were designed for.

2. General AI (Strong AI): A system that possesses the ability to perform any intellectual
   task that a human can do. This type of AI does not yet exist.

3. Super AI: An AI that surpasses human intelligence in all aspects. This is a theoretical
   concept and does not exist yet.

Applications of AI:
- Healthcare: Disease diagnosis, drug discovery, medical imaging
- Finance: Fraud detection, algorithmic trading, credit scoring
- Transportation: Self-driving cars, route optimization
- Education: Personalized learning, automated grading
- Entertainment: Recommendation systems, game AI
- Manufacturing: Quality control, predictive maintenance

AI Ethics:
- Bias in AI systems
- Privacy concerns
- Job displacement
- Autonomous weapons
- Transparency and explainability
""",
            "calculus_basics.txt": """\
Calculus: Fundamental Concepts
===============================

1. Limits
A limit describes the value a function approaches as the input approaches some value.
  lim(x→a) f(x) = L
  
Properties of Limits:
  - Sum Rule: lim[f(x) + g(x)] = lim f(x) + lim g(x)
  - Product Rule: lim[f(x) * g(x)] = lim f(x) * lim g(x)
  - Quotient Rule: lim[f(x)/g(x)] = lim f(x) / lim g(x), provided lim g(x) ≠ 0

2. Derivatives
The derivative of a function represents the rate of change.
  f'(x) = lim(h→0) [f(x+h) - f(x)] / h

Common Derivatives:
  - d/dx(x^n) = n*x^(n-1)         (Power Rule)
  - d/dx(e^x) = e^x
  - d/dx(ln x) = 1/x
  - d/dx(sin x) = cos x
  - d/dx(cos x) = -sin x

Rules:
  - Chain Rule: d/dx[f(g(x))] = f'(g(x)) * g'(x)
  - Product Rule: d/dx[f*g] = f'*g + f*g'
  - Quotient Rule: d/dx[f/g] = (f'*g - f*g') / g^2

3. Integrals
Integration is the reverse process of differentiation.
  ∫ f(x) dx = F(x) + C

Fundamental Theorem of Calculus:
  ∫[a to b] f(x) dx = F(b) - F(a)

Applications:
  - Area under curves
  - Volume of solids of revolution
  - Work and energy calculations
  - Probability distributions
""",
            "physics_mechanics.txt": """\
Physics: Classical Mechanics
=============================

Newton's Laws of Motion:

1. First Law (Law of Inertia):
   An object at rest stays at rest, and an object in motion stays in motion with the same
   speed and direction, unless acted upon by an external force.

2. Second Law:
   F = ma (Force equals mass times acceleration)
   The acceleration of an object is directly proportional to the net force acting on it
   and inversely proportional to its mass.

3. Third Law:
   For every action, there is an equal and opposite reaction.

Work, Energy, and Power:
  - Work: W = F * d * cos(θ)
  - Kinetic Energy: KE = 1/2 * m * v^2
  - Potential Energy: PE = m * g * h
  - Conservation of Energy: Total energy in an isolated system remains constant
  - Power: P = W / t

Momentum:
  - Linear Momentum: p = m * v
  - Conservation of Momentum: Total momentum before = Total momentum after collision
  - Impulse: J = F * Δt = Δp

Circular Motion:
  - Centripetal acceleration: a = v^2 / r
  - Centripetal force: F = m * v^2 / r
  - Angular velocity: ω = 2π / T

Gravitation:
  - Newton's Law of Gravitation: F = G * m1 * m2 / r^2
  - Gravitational constant: G = 6.674 × 10^-11 N⋅m²/kg²
  - Orbital velocity: v = sqrt(G * M / r)
""",
        }

        print("\n📝 Creating educational text files...")
        for filename, content in texts.items():
            file_path = self.raw_texts_dir / filename
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  ✅ Created: {filename}")

    # ──────────────────────────────────────────────
    #  3. Sample PDFs (generated locally, no internet needed!)
    # ──────────────────────────────────────────────
    def create_sample_pdfs(self):
        """Sample PDF files locally generate karo using fpdf2"""

        try:
            from fpdf import FPDF
        except ImportError:
            print("\n⚠️  fpdf2 not installed. Installing now...")
            os.system("pip install fpdf2")
            from fpdf import FPDF

        pdf_contents = {
            "introduction_to_machine_learning.pdf": {
                "title": "Introduction to Machine Learning",
                "chapters": [
                    ("Chapter 1: What is Machine Learning?", [
                        "Machine Learning is a subset of Artificial Intelligence that provides systems the ability to automatically learn and improve from experience without being explicitly programmed.",
                        "Machine Learning focuses on the development of computer programs that can access data and use it to learn for themselves.",
                        "The process of learning begins with observations or data, such as examples, direct experience, or instruction, in order to look for patterns in data and make better decisions in the future.",
                    ]),
                    ("Chapter 2: Types of Machine Learning", [
                        "Supervised Learning: The algorithm learns from labeled training data, and makes predictions based on that data. Examples include classification and regression problems.",
                        "Unsupervised Learning: The algorithm learns from unlabeled data. It tries to find hidden patterns or intrinsic structures in the input data. Clustering and association are common tasks.",
                        "Reinforcement Learning: The algorithm learns by interacting with an environment. It receives rewards or penalties for actions and learns to maximize cumulative reward.",
                    ]),
                    ("Chapter 3: Applications", [
                        "Healthcare: Disease prediction, medical image analysis, drug discovery, and personalized treatment plans.",
                        "Finance: Stock price prediction, fraud detection, credit risk assessment, and algorithmic trading.",
                        "Natural Language Processing: Chatbots, translation, sentiment analysis, and text summarization.",
                        "Computer Vision: Face recognition, autonomous vehicles, quality inspection, and augmented reality.",
                    ]),
                ],
            },
            "python_data_structures.pdf": {
                "title": "Python Data Structures Guide",
                "chapters": [
                    ("Chapter 1: Lists and Tuples", [
                        "Lists are mutable sequences used to store collections of items. They support indexing, slicing, and various methods like append, extend, insert, and remove.",
                        "Tuples are immutable sequences. Once created, their elements cannot be changed. They are useful for representing fixed collections of items.",
                        "List comprehensions provide a concise way to create lists: [x**2 for x in range(10)]",
                        "Both lists and tuples support iteration, membership testing (in operator), and can contain mixed data types.",
                    ]),
                    ("Chapter 2: Dictionaries and Sets", [
                        "Dictionaries store key-value pairs. Keys must be immutable and unique. They provide O(1) average lookup time.",
                        "Dictionary methods include: get(), keys(), values(), items(), update(), pop(), and setdefault().",
                        "Sets are unordered collections of unique elements. They support mathematical operations like union, intersection, and difference.",
                        "Frozensets are immutable versions of sets and can be used as dictionary keys or elements of other sets.",
                    ]),
                    ("Chapter 3: Advanced Data Structures", [
                        "Collections module provides specialized data structures: Counter, defaultdict, OrderedDict, namedtuple, and deque.",
                        "Heapq module implements a min-heap priority queue algorithm, useful for finding the smallest or largest elements efficiently.",
                        "Queue module provides FIFO, LIFO, and priority queues for multi-threaded programming.",
                    ]),
                ],
            },
            "web_development_basics.pdf": {
                "title": "Web Development Fundamentals",
                "chapters": [
                    ("Chapter 1: HTML Basics", [
                        "HTML (HyperText Markup Language) is the standard markup language for creating web pages. It describes the structure of a web page using elements and tags.",
                        "Common HTML elements include: headings (h1-h6), paragraphs (p), links (a), images (img), lists (ul, ol, li), tables, and forms.",
                        "HTML5 introduced semantic elements like header, nav, main, article, section, aside, and footer for better document structure.",
                        "Forms are used to collect user input with elements like input, textarea, select, and button.",
                    ]),
                    ("Chapter 2: CSS Styling", [
                        "CSS (Cascading Style Sheets) controls the visual presentation of HTML elements. It handles layout, colors, fonts, and responsive design.",
                        "CSS selectors include: element, class, ID, attribute, pseudo-class, and pseudo-element selectors.",
                        "Flexbox provides a one-dimensional layout model for arranging items in rows or columns with flexible sizing.",
                        "CSS Grid provides a two-dimensional layout system for creating complex web layouts with rows and columns.",
                    ]),
                    ("Chapter 3: JavaScript Fundamentals", [
                        "JavaScript is a programming language that enables interactive web pages. It runs in the browser and can manipulate the DOM.",
                        "ES6+ features include: let/const, arrow functions, template literals, destructuring, spread operator, and promises.",
                        "The DOM (Document Object Model) is a programming interface for HTML documents. JavaScript can add, remove, and modify elements.",
                        "Fetch API and Async/Await provide modern ways to handle asynchronous operations like API calls.",
                    ]),
                ],
            },
            "statistics_for_data_science.pdf": {
                "title": "Statistics for Data Science",
                "chapters": [
                    ("Chapter 1: Descriptive Statistics", [
                        "Measures of Central Tendency: Mean (average), Median (middle value), and Mode (most frequent value).",
                        "Measures of Dispersion: Range, Variance, Standard Deviation, and Interquartile Range (IQR).",
                        "Data Visualization: Histograms show frequency distributions, box plots display quartiles and outliers, scatter plots reveal relationships between variables.",
                        "Skewness measures the asymmetry of a distribution. Kurtosis measures the tailedness of a distribution.",
                    ]),
                    ("Chapter 2: Probability", [
                        "Probability measures the likelihood of an event occurring, ranging from 0 (impossible) to 1 (certain).",
                        "Conditional Probability: P(A|B) = P(A and B) / P(B). Bayes Theorem: P(A|B) = P(B|A) * P(A) / P(B).",
                        "Probability Distributions: Normal (Gaussian), Binomial, Poisson, Uniform, and Exponential distributions.",
                        "The Central Limit Theorem states that the sampling distribution of the mean approaches a normal distribution as sample size increases.",
                    ]),
                    ("Chapter 3: Hypothesis Testing", [
                        "Null Hypothesis (H0): The default assumption that there is no effect or no difference.",
                        "Alternative Hypothesis (H1): The hypothesis that there is an effect or a difference.",
                        "P-value: The probability of observing results at least as extreme as the actual results, assuming the null hypothesis is true.",
                        "Common tests: t-test, chi-square test, ANOVA, Mann-Whitney U test, and Kolmogorov-Smirnov test.",
                    ]),
                ],
            },
        }

        print("\n📄 Creating sample PDF files...")
        for filename, data in pdf_contents.items():
            try:
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)

                # Title page
                pdf.add_page()
                pdf.set_font("Helvetica", "B", 24)
                pdf.ln(60)
                pdf.cell(0, 15, data["title"], ln=True, align="C")
                pdf.set_font("Helvetica", "", 12)
                pdf.ln(10)
                pdf.cell(0, 10, "Personalized E-Learning Assistant", ln=True, align="C")
                pdf.cell(0, 10, "Sample Educational Material", ln=True, align="C")

                # Chapters
                for chapter_title, paragraphs in data["chapters"]:
                    pdf.add_page()
                    pdf.set_font("Helvetica", "B", 16)
                    pdf.cell(0, 10, chapter_title, ln=True)
                    pdf.ln(5)
                    pdf.set_font("Helvetica", "", 11)
                    for para in paragraphs:
                        pdf.multi_cell(0, 7, para)
                        pdf.ln(4)

                file_path = self.raw_pdfs_dir / filename
                pdf.output(str(file_path))
                size_kb = os.path.getsize(file_path) / 1024
                print(f"  ✅ Created: {filename} ({size_kb:.1f} KB)")
            except Exception as e:
                print(f"  ❌ Failed to create {filename}: {e}")


    # ──────────────────────────────────────────────
    #  4. Pakistan Education Notes
    # ──────────────────────────────────────────────
    def create_pakistan_notes(self):
        """Pakistan curriculum ke notes create karo - English, Urdu, Math, Islamiat, etc."""
        from app.services.pakistan_data import NOTES_DATA

        print("\n📝 Creating Pakistan education notes...")
        for filename, content in NOTES_DATA.items():
            file_path = self.raw_notes_dir / filename
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  ✅ Created: {filename}")

    # ──────────────────────────────────────────────
    #  5. Pakistan Education PDFs
    # ──────────────────────────────────────────────
    def create_pakistan_pdfs(self):
        """Pakistan subjects ke PDF textbooks create karo"""
        try:
            from fpdf import FPDF
        except ImportError:
            print("\n⚠️  fpdf2 not installed. Installing now...")
            os.system("pip install fpdf2")
            from fpdf import FPDF

        from app.services.pakistan_pdf_data import PDF_CONTENTS

        print("\n📄 Creating Pakistan education PDF files...")
        for filename, data in PDF_CONTENTS.items():
            try:
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)

                # Title page
                pdf.add_page()
                pdf.set_font("Helvetica", "B", 24)
                pdf.ln(60)
                pdf.cell(0, 15, data["title"], ln=True, align="C")
                pdf.set_font("Helvetica", "", 12)
                pdf.ln(10)
                pdf.cell(0, 10, "Personalized E-Learning Assistant", ln=True, align="C")
                pdf.cell(0, 10, "Pakistan Education System", ln=True, align="C")

                # Chapters
                for chapter_title, paragraphs in data["chapters"]:
                    pdf.add_page()
                    pdf.set_font("Helvetica", "B", 16)
                    pdf.cell(0, 10, chapter_title, ln=True)
                    pdf.ln(5)
                    pdf.set_font("Helvetica", "", 11)
                    for para in paragraphs:
                        pdf.multi_cell(0, 7, para)
                        pdf.ln(4)

                file_path = self.raw_pdfs_dir / filename
                pdf.output(str(file_path))
                size_kb = os.path.getsize(file_path) / 1024
                print(f"  ✅ Created: {filename} ({size_kb:.1f} KB)")
            except Exception as e:
                print(f"  ❌ Failed to create {filename}: {e}")


if __name__ == "__main__":
    import sys
    # Add project paths for imports
    base = Path(__file__).parent.parent.parent
    if str(base) not in sys.path:
        sys.path.insert(0, str(base))

    downloader = DataDownloader()

    # Sab kuch generate karo — no internet needed!
    print("=" * 55)
    print("  Personalized E-Learning Data Generator")
    print("  Pakistan Education + ML/Tech Data")
    print("  No internet connection required!")
    print("=" * 55)

    # General ML/Tech data
    downloader.create_sample_notes()       # 5 ML/tech notes
    downloader.create_sample_texts()       # 3 educational texts
    downloader.create_sample_pdfs()        # 4 PDF textbooks

    # Pakistan Education data
    downloader.create_pakistan_notes()      # 13 Pakistan subject notes
    downloader.create_pakistan_pdfs()       # 6 Pakistan PDF textbooks

    print("\n" + "=" * 55)
    print("✅✅✅ All data generated successfully!")
    print("=" * 55)
    print(f"\n📁 Data location: {downloader.base_dir / 'data' / 'raw'}")
    print(f"   📝 Notes:  {len(list(downloader.raw_notes_dir.glob('*')))} files")
    print(f"   📃 Texts:  {len(list(downloader.raw_texts_dir.glob('*')))} files")
    print(f"   📄 PDFs:   {len(list(downloader.raw_pdfs_dir.glob('*')))} files")
