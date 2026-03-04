"""
Quiz Generator Service
Extracts facts from text, creates MCQs with plausible wrong options.
Supports English and Urdu. Template-based with ML-ready architecture.
"""

import re
import uuid
import random
import logging
from typing import Dict, List, Optional

logger = logging.getLogger("elearning.quiz")


class QuizGenerator:
    """
    Generate MCQ quizzes from text content.

    Usage:
        qg = QuizGenerator()
        result = qg.generate_quiz("Some text...", keywords=["AI", "ML"])
        print(result['questions'])
    """

    def __init__(self, difficulty: str = "medium"):
        self.difficulty = difficulty
        logger.info(f"QuizGenerator initialized (difficulty: {difficulty})")

    def generate_quiz(
        self,
        text: str,
        keywords: List[str] = None,
        num_questions: int = 5,
    ) -> Dict:
        """
        Generate quiz from text and keywords.

        Returns:
            {
                'quiz_id': str,
                'questions': [...],
                'total_questions': int,
                'difficulty': str,
            }
        """
        keywords = keywords or []
        lang = self._detect_lang(text)
        facts = self._extract_facts(text)
        questions = []
        used = set()

        random.shuffle(facts)

        for fact in facts:
            if len(questions) >= num_questions:
                break
            q = self._create_mcq(fact, facts, lang, used)
            if q:
                q["id"] = len(questions) + 1
                questions.append(q)
                used.add(q.get("_answer_text", ""))

        # If not enough from facts, generate from keywords
        if len(questions) < num_questions and keywords:
            for kw in keywords:
                if len(questions) >= num_questions:
                    break
                q = self._create_keyword_question(kw, text, lang)
                if q:
                    q["id"] = len(questions) + 1
                    questions.append(q)

        quiz_id = uuid.uuid4().hex[:12]

        # Clean internal fields
        for q in questions:
            q.pop("_answer_text", None)

        return {
            "quiz_id": quiz_id,
            "questions": questions,
            "total_questions": len(questions),
            "difficulty": self.difficulty,
        }

    def generate_mcq(self, keyword: str, context: str) -> Optional[Dict]:
        """Generate a single MCQ for a keyword."""
        return self._create_keyword_question(keyword, context, "en")

    def generate_true_false(self, sentence: str) -> Dict:
        """Generate a True/False question from a sentence."""
        return {
            "type": "true_false",
            "question": f"True or False: {sentence}",
            "options": [
                {"label": "A", "text": "True"},
                {"label": "B", "text": "False"},
            ],
            "correct_answer": "A",
            "explanation": f"This statement is based on the text: {sentence[:100]}",
        }

    # ── Fact Extraction ──

    def _extract_facts(self, text: str) -> List[Dict]:
        """Extract question-worthy facts from text."""
        facts = []
        lines = re.split(r'[.\n]', text)

        for line in lines:
            line = line.strip()
            if len(line) < 15:
                continue

            # Pattern: "Key: Value"
            m = re.match(r'^(.+?)[:]\s*(.+)', line)
            if m:
                key = m.group(1).strip().strip('-* ')
                val = m.group(2).strip()
                if 3 < len(key) < 80 and len(val) > 10:
                    facts.append({"type": "definition", "key": key, "value": val, "full": line})
                    continue

            # Pattern: "X = Y"
            m = re.match(r'^(.+?)\s*=\s*(.+)', line)
            if m and len(m.group(1).strip()) > 2:
                facts.append({
                    "type": "formula",
                    "key": m.group(1).strip(),
                    "value": m.group(2).strip(),
                    "full": line,
                })
                continue

            # Pattern: "X is/are Y"
            for pat in [r'(.+?)\s+(?:is|are|was|were|means|refers to)\s+(.+)',
                        r'(.+?)\s+(?:ہے|ہیں|ہوتا|کہتے)\s+(.+)']:
                m = re.match(pat, line, re.IGNORECASE)
                if m and len(m.group(1).strip()) > 3:
                    facts.append({
                        "type": "statement",
                        "key": m.group(1).strip().strip('-* '),
                        "value": m.group(2).strip(),
                        "full": line,
                    })
                    break

            # Numbered items
            m = re.match(r'^\d+[.)]\s*(.+?)[\s:\-]+(.+)', line)
            if m and len(m.group(2).strip()) > 10:
                facts.append({
                    "type": "numbered",
                    "key": m.group(1).strip(),
                    "value": m.group(2).strip(),
                    "full": line,
                })

        return facts

    # ── MCQ Creation ──

    def _create_mcq(self, fact: Dict, all_facts: List[Dict], lang: str, used: set) -> Optional[Dict]:
        """Create MCQ from a fact."""
        key = fact["key"]
        value = fact["value"]

        if value in used:
            return None

        val_short = value[:80] + "..." if len(value) > 80 else value

        # Question templates
        if lang == "ur":
            templates = [f"{key} کیا ہے؟", f"{key} سے کیا مراد ہے؟"]
        elif fact["type"] == "formula":
            templates = [f"What is the formula for {key}?", f"Which expression equals {key}?"]
        elif fact["type"] == "definition":
            templates = [f"What is {key}?", f"Which best describes {key}?"]
        else:
            templates = [f"Which is true about {key}?", f"What does {key} refer to?"]

        question = random.choice(templates)

        # Wrong options
        wrongs = []
        for f in all_facts:
            if f is not fact:
                v = f["value"][:80] + "..." if len(f["value"]) > 80 else f["value"]
                if v != val_short and v not in wrongs:
                    wrongs.append(v)
            if len(wrongs) >= 5:
                break

        # Generic fillers
        fillers = (
            ["مذکورہ میں سے کوئی نہیں", "یہ سب درست ہیں", "اس کا تعلق نہیں"]
            if lang == "ur"
            else ["None of the above", "All of the above", "Not related to this topic"]
        )
        while len(wrongs) < 3:
            for f in fillers:
                if f not in wrongs:
                    wrongs.append(f)
                    break
            else:
                break

        if len(wrongs) < 3:
            return None

        options = [val_short] + wrongs[:3]
        random.shuffle(options)

        labels = ["A", "B", "C", "D"]
        correct_idx = options.index(val_short)

        return {
            "type": "mcq",
            "question": question,
            "options": [{"label": labels[i], "text": opt} for i, opt in enumerate(options)],
            "correct_answer": labels[correct_idx],
            "explanation": f"The answer is: {val_short}",
            "_answer_text": val_short,
        }

    def _create_keyword_question(self, keyword: str, text: str, lang: str) -> Optional[Dict]:
        """Generate question about a keyword using context from text."""
        # Find sentence containing keyword
        sentences = re.split(r'[.\n]', text)
        context = None
        for s in sentences:
            if keyword.lower() in s.lower() and len(s.strip()) > 20:
                context = s.strip()
                break

        if not context:
            return None

        if lang == "ur":
            question = f"{keyword} کے بارے میں درست بیان کون سا ہے؟"
        else:
            question = f"According to the text, which statement about '{keyword}' is correct?"

        correct = context[:80] + "..." if len(context) > 80 else context

        wrongs = [
            f"{keyword} is not mentioned in the text",
            f"{keyword} refers to a completely different concept",
            f"None of the statements about {keyword} are accurate",
        ]

        options = [correct] + wrongs
        random.shuffle(options)
        labels = ["A", "B", "C", "D"]
        correct_idx = options.index(correct)

        return {
            "type": "mcq",
            "question": question,
            "options": [{"label": labels[i], "text": opt} for i, opt in enumerate(options)],
            "correct_answer": labels[correct_idx],
            "explanation": f"From the text: {correct}",
        }

    def _detect_lang(self, text: str) -> str:
        urdu = len(re.findall(r'[\u0600-\u06FF]', text))
        alpha = sum(1 for c in text if c.isalpha())
        return "ur" if alpha > 0 and urdu / alpha > 0.3 else "en"
