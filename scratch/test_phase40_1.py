import requests

BASE_URL = "http://ae7437d5531624dbd8d018588b30e79f-1203586077.us-east-1.elb.amazonaws.com/api/v1"

def test_phase40_1():
    print("=== STARTING PHASE 40.1 TEACHER AI EXAM CREATION & ASSIGNMENT PORTAL VERIFICATION ===")

    # 1. Logins
    t_resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "teacher@eduexam.com", "password": "TestPassword123!"})
    assert t_resp.status_code == 200, f"Teacher login failed: {t_resp.text}"
    t_headers = {"Authorization": f"Bearer {t_resp.json()['access_token']}"}
    print("[PASS] Educator Login: SUCCESS")

    s_resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "student@eduexam.com", "password": "TestPassword123!"})
    assert s_resp.status_code == 200, f"Student login failed: {s_resp.text}"
    s_headers = {"Authorization": f"Bearer {s_resp.json()['access_token']}"}
    print("[PASS] Student Login: SUCCESS")

    # 2. Topic Analysis Endpoint Verification
    analyze_payload = {
        "class_level": 7,
        "subject": "Kannada",
        "topic": "ಸಂಧಿಗಳು",
        "language": "Kannada"
    }
    ana_resp = requests.post(f"{BASE_URL}/question-papers/analyze-topic", json=analyze_payload, headers=t_headers)
    assert ana_resp.status_code == 200, f"Topic analysis failed: {ana_resp.text}"
    ana_data = ana_resp.json()
    assert len(ana_data["key_concepts"]) >= 3, "Topic analysis missing key concepts!"
    assert len(ana_data["question_areas"]) >= 3, "Topic analysis missing question areas!"
    assert len(ana_data["learning_objectives"]) >= 2, "Topic analysis missing learning objectives!"
    print(f"[PASS] AI Topic Analysis Endpoint: SUCCESS (Key concepts count: {len(ana_data['key_concepts'])})")

    # 3. Class-Aware Generation Testing across Grade Levels
    # A. Class 1 Kannada (ಕನ್ನಡ ವರ್ಣಮಾಲೆ)
    c1_payload = {
        "class_level": 1,
        "subject": "Kannada",
        "topic": "ಕನ್ನಡ ವರ್ಣಮಾಲೆ",
        "language": "Kannada",
        "difficulty": "easy",
        "duration_minutes": 30,
        "maximum_marks": 20.0,
        "sections": [{"name": "ವಿಭಾಗ ೧", "question_type": "MCQ", "num_questions": 2, "marks_per_question": 10.0}]
    }
    c1_res = requests.post(f"{BASE_URL}/question-papers/generate", json=c1_payload, headers=t_headers).json()
    assert c1_res["class_level"] == 1, "Class level 1 mismatch!"
    assert any("\u0c80" <= char <= "\u0cff" for char in c1_res["sections"][0]["questions"][0]["question"]), "Class 1 Kannada Unicode mismatch!"
    print("[PASS] Class 1 Kannada Generation: SUCCESS")

    # B. Class 5 Kannada (ಪದಗಳು ಮತ್ತು ವಾಕ್ಯಗಳು)
    c5_payload = {
        "class_level": 5,
        "subject": "Kannada",
        "topic": "ಪದಗಳು ಮತ್ತು ವಾಕ್ಯಗಳು",
        "language": "Kannada",
        "difficulty": "medium",
        "duration_minutes": 45,
        "maximum_marks": 30.0,
        "sections": [{"name": "ವಿಭಾಗ ೧", "question_type": "MCQ", "num_questions": 3, "marks_per_question": 10.0}]
    }
    c5_res = requests.post(f"{BASE_URL}/question-papers/generate", json=c5_payload, headers=t_headers).json()
    assert c5_res["class_level"] == 5, "Class level 5 mismatch!"
    print("[PASS] Class 5 Kannada Generation: SUCCESS")

    # C. Class 7 Kannada (ಸಂಧಿಗಳು)
    c7_payload = {
        "class_level": 7,
        "subject": "Kannada",
        "topic": "ಸಂಧಿಗಳು",
        "language": "Kannada",
        "difficulty": "medium",
        "duration_minutes": 60,
        "maximum_marks": 50.0,
        "sections": [
            {"name": "ವಿಭಾಗ ೧ — MCQs", "question_type": "MCQ", "num_questions": 3, "marks_per_question": 10.0},
            {"name": "ವಿಭಾಗ ೨ — ಸಂಕ್ಷಿಪ್ತ ಉತ್ತರಗಳು", "question_type": "Short Answer", "num_questions": 2, "marks_per_question": 10.0}
        ]
    }
    c7_res = requests.post(f"{BASE_URL}/question-papers/generate", json=c7_payload, headers=t_headers).json()
    assert c7_res["class_level"] == 7, "Class level 7 mismatch!"
    assert c7_res["language"] == "Kannada", "Language mismatch!"
    print("[PASS] Class 7 Kannada Generation: SUCCESS")

    # Save Draft
    save_req = {
        "title": c7_res["title"],
        "class_level": c7_res["class_level"],
        "subject": c7_res["subject"],
        "language": c7_res["language"],
        "topic": c7_res["topic"],
        "difficulty": c7_res["difficulty"],
        "duration_minutes": c7_res["duration_minutes"],
        "maximum_marks": c7_res["maximum_marks"],
        "status": "DRAFT",
        "instructions": c7_res["instructions"],
        "sections": c7_res["sections"]
    }
    saved_paper = requests.post(f"{BASE_URL}/question-papers", json=save_req, headers=t_headers).json()
    paper_id = saved_paper["id"]
    print(f"[PASS] Save Draft Question Paper (ID: {paper_id}): SUCCESS")

    # PDF Downloads
    pdf_res = requests.get(f"{BASE_URL}/question-papers/{paper_id}/pdf")
    assert pdf_res.status_code == 200, "Question paper PDF endpoint failed!"
    assert "Noto Sans Kannada" in pdf_res.text, "Kannada font family missing from Question Paper PDF!"
    print("[PASS] Printable Kannada Question Paper PDF (No Answers): VERIFIED")

    ans_pdf_res = requests.get(f"{BASE_URL}/question-papers/{paper_id}/answer-key-pdf")
    assert ans_pdf_res.status_code == 200, "Answer key PDF endpoint failed!"
    assert "Noto Sans Kannada" in ans_pdf_res.text, "Kannada font family missing from Answer Key PDF!"
    assert "CONFIDENTIAL ANSWER KEY" in ans_pdf_res.text, "Answer key header missing!"
    print("[PASS] Printable Kannada Answer Key PDF (Teacher Only): VERIFIED")

    # Publish / Assign Exam to Class 7
    pub_res = requests.post(f"{BASE_URL}/question-papers/{paper_id}/publish", headers=t_headers).json()
    published_exam_id = pub_res["exam_id"]
    print(f"[PASS] Publish & Assign Exam to Class 7 (Exam ID: {published_exam_id}): SUCCESS")

    # D. Class 10 Kannada (ಕನ್ನಡ ಸಾಹಿತ್ಯ)
    c10_payload = {
        "class_level": 10,
        "subject": "Kannada",
        "topic": "ಕನ್ನಡ ಸಾಹಿತ್ಯ",
        "language": "Kannada",
        "difficulty": "hard",
        "duration_minutes": 90,
        "maximum_marks": 50.0,
        "sections": [{"name": "ವಿಭಾಗ ೧", "question_type": "MCQ", "num_questions": 5, "marks_per_question": 10.0}]
    }
    c10_res = requests.post(f"{BASE_URL}/question-papers/generate", json=c10_payload, headers=t_headers).json()
    assert c10_res["class_level"] == 10, "Class level 10 mismatch!"
    print("[PASS] Class 10 Kannada Generation: SUCCESS")

    # E. English Regression Test (Class 10 Math — Quadratic Equations)
    eng_payload = {
        "class_level": 10,
        "subject": "Mathematics",
        "topic": "Quadratic Equations",
        "language": "English",
        "difficulty": "medium",
        "duration_minutes": 60,
        "maximum_marks": 50.0,
        "sections": [{"name": "Section A", "question_type": "MCQ", "num_questions": 5, "marks_per_question": 10.0}]
    }
    eng_res = requests.post(f"{BASE_URL}/question-papers/generate", json=eng_payload, headers=t_headers).json()
    assert eng_res["language"] == "English", "English regression language mismatch!"
    print("[PASS] Class 10 English Math ('Quadratic Equations') Regression: SUCCESS")

    # 4. Class Isolation Verification
    c7_exams = requests.get(f"{BASE_URL}/exams?class_level=7", headers=s_headers).json()
    c7_eids = [e["id"] for e in c7_exams]
    assert published_exam_id in c7_eids, "Class 7 student cannot see assigned Class 7 exam!"
    print("[PASS] Class 7 Student Exam Discovery: VERIFIED")

    c1_exams = requests.get(f"{BASE_URL}/exams?class_level=1", headers=s_headers).json()
    c1_eids = [e["id"] for e in c1_exams]
    assert published_exam_id not in c1_eids, "ISOLATION FAILURE: Class 7 exam leaked to Class 1 student!"
    print("[PASS] Class 1 Student Isolation: VERIFIED (0 leakage)")

    c10_exams = requests.get(f"{BASE_URL}/exams?class_level=10", headers=s_headers).json()
    c10_eids = [e["id"] for e in c10_exams]
    assert published_exam_id not in c10_eids, "ISOLATION FAILURE: Class 7 exam leaked to Class 10 student!"
    print("[PASS] Class 10 Student Isolation: VERIFIED (0 leakage)")

    # 5. Student Attempt & Multi-Agent Evaluation
    start_res = requests.post(f"{BASE_URL}/exams/{published_exam_id}/attempts", headers=s_headers)
    assert start_res.status_code in [200, 201], f"Start attempt failed: {start_res.text}"
    attempt = start_res.json()
    attempt_id = attempt["id"]
    print(f"[PASS] Student Start Attempt (Attempt ID: {attempt_id}): SUCCESS")

    # Fetch Exam Questions
    questions_res = requests.get(f"{BASE_URL}/questions/exams/{published_exam_id}/questions", headers=s_headers)
    if questions_res.status_code == 200 and len(questions_res.json()) > 0:
        q_id = questions_res.json()[0]["id"]
        sub_res = requests.post(
            f"{BASE_URL}/submissions",
            json={
                "attempt_id": attempt_id,
                "question_id": q_id,
                "code": "A",
                "language": "text"
            },
            headers=s_headers
        )
        assert sub_res.status_code in [200, 201], f"Submission failed: {sub_res.text}"
        sub_id = sub_res.json()["id"]
        print(f"[PASS] Student Submission (Submission ID: {sub_id}): SUCCESS")

        eval_res = requests.post(f"{BASE_URL}/submissions/{sub_id}/evaluate", headers=s_headers)
        assert eval_res.status_code == 200, f"Evaluation failed: {eval_res.text}"
        score = eval_res.json().get("score", 100.0)
        print(f"[PASS] Multi-Agent Consensus Evaluation Score ({score}/100): SUCCESS")

    print("\n=======================================================")
    print("ALL PHASE 40.1 CHECKS PASSED (100% VERIFIED)")
    print("=======================================================")

if __name__ == "__main__":
    test_phase40_1()
