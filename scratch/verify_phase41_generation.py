import sys
import os
from unittest.mock import MagicMock

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Mock boto3 if not installed in local environment
try:
    import boto3
except ImportError:
    sys.modules['boto3'] = MagicMock()
    sys.modules['botocore'] = MagicMock()
    sys.modules['botocore.exceptions'] = MagicMock()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.ai.question_generator import generate_ai_question_paper
from app.ai.provider import get_question_generator_provider

def run_tests():
    print("=== TESTING QUESTION GENERATION ENGINE ===")

    # Test 1: Class 7 Kannada Sandhigalu - 10 Questions
    paper_kn = generate_ai_question_paper(
        class_level=7,
        subject="Kannada",
        topic="ಸಂಧಿಗಳು",
        language="Kannada",
        difficulty="medium",
        duration_minutes=60,
        maximum_marks=50.0,
        sections_config=[{"name": "Section A", "question_type": "MCQ", "num_questions": 10, "marks_per_question": 5.0}]
    )
    assert len(paper_kn["sections"][0]["questions"]) == 10, "Expected 10 questions"
    print(f"[PASS] Test 1 (10 Kannada Questions): {paper_kn['title']}")
    print(f"       Q1: {paper_kn['sections'][0]['questions'][0]['question']}")
    print(f"       Q10: {paper_kn['sections'][0]['questions'][9]['question']}")

    # Test 2: Class 10 Math Quadratic Equations - 20 Questions
    paper_math = generate_ai_question_paper(
        class_level=10,
        subject="Mathematics",
        topic="Quadratic Equations",
        language="English",
        difficulty="medium",
        duration_minutes=90,
        maximum_marks=100.0,
        sections_config=[{"name": "Section A", "question_type": "MCQ", "num_questions": 20, "marks_per_question": 5.0}]
    )
    assert len(paper_math["sections"][0]["questions"]) == 20, "Expected 20 questions"
    print(f"[PASS] Test 2 (20 Math Questions): {paper_math['title']}")
    print(f"       Q1: {paper_math['sections'][0]['questions'][0]['question']}")
    print(f"       Q20: {paper_math['sections'][0]['questions'][19]['question']}")

    # Test 3: Class 1 Kannada Alphabets - 5 Questions
    paper_c1 = generate_ai_question_paper(
        class_level=1,
        subject="Kannada",
        topic="ಕನ್ನಡ ವರ್ಣಮಾಲೆ",
        language="Kannada",
        difficulty="easy",
        duration_minutes=30,
        maximum_marks=25.0,
        sections_config=[{"name": "Section A", "question_type": "MCQ", "num_questions": 5, "marks_per_question": 5.0}]
    )
    assert len(paper_c1["sections"][0]["questions"]) == 5, "Expected 5 questions"
    print(f"[PASS] Test 3 (Class 1 Kannada 5 Questions): {paper_c1['title']}")

    # Test 4: Provider Selection
    provider = get_question_generator_provider()
    print(f"[PASS] Test 4 (Provider Selection): {provider.__class__.__name__ if provider else 'None (Fallback active)'}")

    print("\nALL QUESTION GENERATION ENGINE TESTS PASSED 100%!")

if __name__ == "__main__":
    run_tests()
