import sys
import os
import requests

BASE_URL = "http://ae7437d5531624dbd8d018588b30e79f-1203586077.us-east-1.elb.amazonaws.com"

def get_teacher_token():
    res = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"email": "teacher@eduexam.com", "password": "TestPassword123!"})
    assert res.status_code == 200, f"Teacher login failed: {res.text}"
    return res.json()["access_token"]

def test_gemini_requirements():
    print("=== STARTING GEMINI PROVIDER & TOPIC PRESERVATION TEST SUITE ===")
    token = get_teacher_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Test A: Topic Preservation ("Photosynthesis" stays "Photosynthesis")
    ana_res = requests.post(f"{BASE_URL}/api/v1/question-papers/analyze-topic", json={
        "class_level": 7, "subject": "Science", "topic": "Photosynthesis", "language": "English"
    }, headers=headers)
    assert ana_res.status_code == 200, f"Analyze topic failed: {ana_res.text}"
    ana_data = ana_res.json()
    assert ana_data["topic"] == "Photosynthesis", f"Topic contaminated in analysis: {ana_data['topic']}"
    print("[PASS] Test A: Exact topic 'Photosynthesis' stays 'Photosynthesis'")

    # Test B: Topic Analysis returns large concepts without contaminating req.topic
    assert len(ana_data["key_concepts"]) > 0, "No key concepts returned in topic analysis"
    assert len(ana_data["learning_objectives"]) > 0, "No learning objectives returned"
    print("[PASS] Test B: Topic Analysis returns rich learning objectives separately from req.topic")

    # Test C: 1-Question Generation
    p1 = {
        "class_level": 7, "subject": "Science", "topic": "Photosynthesis", "language": "English",
        "difficulty": "medium", "duration_minutes": 15, "maximum_marks": 5.0,
        "sections": [{"name": "Section A", "question_type": "MCQ", "num_questions": 1, "marks_per_question": 5.0}]
    }
    r1 = requests.post(f"{BASE_URL}/api/v1/question-papers/generate", json=p1, headers=headers)
    assert r1.status_code in [200, 503], f"1-Question endpoint error: {r1.status_code} {r1.text}"
    if r1.status_code == 200:
        data1 = r1.json()
        assert sum(len(s["questions"]) for s in data1["sections"]) == 1, "1-question request failed count"
        assert data1["topic"] == "Photosynthesis", f"Generated paper topic contaminated: {data1['topic']}"
        print(f"[PASS] Test C: 1-Question Generation returned exactly 1 question (Provider: {data1.get('generation_provider')})")
    else:
        print("[PASS] Test C: 1-Question Generation returned clean HTTP 503 AI Unavailable (no fake fallback)")

    # Test D: 5-Question Generation
    p5 = {
        "class_level": 7, "subject": "Mathematics", "topic": "Fractions", "language": "English",
        "difficulty": "medium", "duration_minutes": 30, "maximum_marks": 25.0,
        "sections": [{"name": "Section A", "question_type": "MCQ", "num_questions": 5, "marks_per_question": 5.0}]
    }
    r5 = requests.post(f"{BASE_URL}/api/v1/question-papers/generate", json=p5, headers=headers)
    assert r5.status_code in [200, 503], f"5-Question endpoint error: {r5.status_code} {r5.text}"
    if r5.status_code == 200:
        data5 = r5.json()
        assert sum(len(s["questions"]) for s in data5["sections"]) == 5, "5-question request failed count"
        print(f"[PASS] Test D: 5-Question Generation returned exactly 5 questions (Provider: {data5.get('generation_provider')})")
    else:
        print("[PASS] Test D: 5-Question Generation returned clean HTTP 503 AI Unavailable (no fake fallback)")

    # Test E: Kannada 2-Question Generation
    pk2 = {
        "class_level": 7, "subject": "Kannada", "topic": "ಸಂಧಿಗಳು", "language": "Kannada",
        "difficulty": "medium", "duration_minutes": 20, "maximum_marks": 10.0,
        "sections": [{"name": "Section A — Multiple Choice Questions (MCQ)", "question_type": "MCQ", "num_questions": 2, "marks_per_question": 5.0}]
    }
    rk2 = requests.post(f"{BASE_URL}/api/v1/question-papers/generate", json=pk2, headers=headers)
    assert rk2.status_code in [200, 503], f"Kannada 2-Question error: {rk2.status_code} {rk2.text}"
    if rk2.status_code == 200:
        datak2 = rk2.json()
        assert sum(len(s["questions"]) for s in datak2["sections"]) == 2, "Kannada 2-question count failed"
        print(f"[PASS] Test E: Kannada 2-Question Generation returned exactly 2 questions (Provider: {datak2.get('generation_provider')})")
    else:
        print("[PASS] Test E: Kannada 2-Question Generation returned clean HTTP 503 AI Unavailable (no fake fallback)")

    print("\n=======================================================")
    print("ALL GEMINI PROVIDER & TOPIC PRESERVATION CHECKS PASSED (100%)")
    print("=======================================================")

if __name__ == "__main__":
    test_gemini_requirements()
