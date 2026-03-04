# Generate MCQ quizzes from text
from transformers import pipeline
from typing import List, Dict


quiz_pipeline = None


def get_quiz_pipeline():
    global quiz_pipeline
    if quiz_pipeline is None:
        quiz_pipeline = pipeline("text2text-generation", model="t5-small")
    return quiz_pipeline


def generate_quiz(text: str, num_questions: int = 5) -> List[Dict]:
    """Generate multiple-choice questions from the input text."""
    generator = get_quiz_pipeline()

    questions = []
    # Split text into chunks for question generation
    sentences = text.split(".")
    selected = sentences[: min(num_questions, len(sentences))]

    for i, sentence in enumerate(selected):
        sentence = sentence.strip()
        if len(sentence) < 20:
            continue

        prompt = f"generate question: {sentence}"
        result = generator(prompt, max_length=100)

        question_text = result[0]["generated_text"] if result else f"Question about: {sentence[:50]}..."

        questions.append(
            {
                "id": i + 1,
                "question": question_text,
                "options": [
                    {"label": "A", "text": "Option A (to be refined)"},
                    {"label": "B", "text": "Option B (to be refined)"},
                    {"label": "C", "text": "Option C (to be refined)"},
                    {"label": "D", "text": "Option D (to be refined)"},
                ],
                "correct_answer": "A",
            }
        )

    return questions
