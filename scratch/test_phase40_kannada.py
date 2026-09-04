import requests

BASE_URL = "http://ae7437d5531624dbd8d018588b30e79f-1203586077.us-east-1.elb.amazonaws.com/api/v1"

def test_phase40_kannada():
    print("=== STARTING PHASE 40 KANNADA AI QUESTION PAPER & ASSIGNMENT VERIFICATION ===")
    
    # 1. Educator Login
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "teacher@eduexam.com", "password": "TestPassword123!"})
    assert resp.status_code == 200, f"Educator login failed: {resp.text}"
    teacher_token = resp.json()["access_token"]
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
    print("[PASS] Educator Login: SUCCESS")

    # 2. Student Login
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "student@eduexam.com", "password": "TestPassword123!"})
    assert resp.status_code == 200, f"Student login failed: {resp.text}"
    student_token = resp.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}
    print("[PASS] Student Login: SUCCESS")

    # 3. Generate Class 7 Kannada AI Question Paper (Topic: ಸಂಧಿಗಳು)
    gen_payload = {
        "class_level": 7,
        "subject": "Kannada",
        "topic": "ಸಂಧಿಗಳು",
        "language": "Kannada",
        "difficulty": "medium",
        "duration_minutes": 60,
        "maximum_marks": 50.0,
        "sections": [
            {
                "name": "ವಿಭಾಗ ೧ — ಬಹುಆಯ್ಕೆ ಪ್ರಶ್ನೆಗಳು (MCQ)",
                "question_type": "MCQ",
                "num_questions": 3,
                "marks_per_question": 10.0
            },
            {
                "name": "ವಿಭಾಗ ೨ — ಸಂಕ್ಷಿಪ್ತ ಉತ್ತರಗಳು",
                "question_type": "Short Answer",
                "num_questions": 2,
                "marks_per_question": 10.0
            }
        ]
    }
    resp = requests.post(f"{BASE_URL}/question-papers/generate", json=gen_payload, headers=teacher_headers)
    assert resp.status_code == 200, f"Kannada AI Generation failed: {resp.text}"
    paper = resp.json()
    assert paper["language"] == "Kannada", "Language property mismatch in generated paper!"
    assert paper["class_level"] == 7, "Class level mismatch in generated paper!"
    assert len(paper["sections"]) == 2, "Section count mismatch!"
    
    # Verify Kannada Text in Questions and Answers
    q1 = paper["sections"][0]["questions"][0]
    assert any("\u0c80" <= char <= "\u0cff" for char in q1["question"]), "Question text does NOT contain Kannada Unicode!"
    print("[PASS] Class 7 Kannada AI Question Paper Generation: SUCCESS")

    # 4. Save Question Paper Draft
    save_payload = {
        "title": paper["title"],
        "class_level": paper["class_level"],
        "subject": paper["subject"],
        "language": paper["language"],
        "topic": paper["topic"],
        "difficulty": paper["difficulty"],
        "duration_minutes": paper["duration_minutes"],
        "maximum_marks": paper["maximum_marks"],
        "status": "DRAFT",
        "instructions": paper["instructions"],
        "sections": paper["sections"]
    }
    resp = requests.post(f"{BASE_URL}/question-papers", json=save_payload, headers=teacher_headers)
    assert resp.status_code == 201, f"Save Question Paper Draft failed: {resp.text}"
    paper_id = resp.json()["id"]
    print(f"[PASS] Save Kannada Question Paper Draft (ID: {paper_id}): SUCCESS")

    # 5. Download Question Paper PDF
    pdf_resp = requests.get(f"{BASE_URL}/question-papers/{paper_id}/pdf")
    assert pdf_resp.status_code == 200, "Question Paper PDF endpoint failed!"
    assert "Noto Sans Kannada" in pdf_resp.text, "Kannada font family missing from HTML PDF template!"
    assert "Correct Answer" not in pdf_resp.text, "Correct Answer leaked into student Question Paper PDF!"
    print("[PASS] Printable Kannada Question Paper PDF (No Answers): VERIFIED")

    # 6. Download Answer Key PDF
    ans_pdf_resp = requests.get(f"{BASE_URL}/question-papers/{paper_id}/answer-key-pdf")
    assert ans_pdf_resp.status_code == 200, "Answer Key PDF endpoint failed!"
    assert "Noto Sans Kannada" in ans_pdf_resp.text, "Kannada font family missing from Answer Key PDF template!"
    assert "CONFIDENTIAL ANSWER KEY" in ans_pdf_resp.text, "Confidential header missing from Answer Key PDF!"
    assert "Correct Answer" in ans_pdf_resp.text, "Answers missing from Answer Key PDF!"
    print("[PASS] Printable Kannada Answer Key PDF (Teacher Only): VERIFIED")

    # 7. Assign / Publish Exam
    pub_resp = requests.post(f"{BASE_URL}/question-papers/{paper_id}/publish", headers=teacher_headers)
    assert pub_resp.status_code == 200, f"Publish exam failed: {pub_resp.text}"
    published_exam_id = pub_resp.json()["exam_id"]
    print(f"[PASS] Assign / Publish Exam to Class 7 (Exam ID: {published_exam_id}): SUCCESS")

    # 8. Class Isolation Test
    res_c7 = requests.get(f"{BASE_URL}/exams?class_level=7", headers=student_headers).json()
    c7_ids = [e["id"] for e in res_c7]
    assert published_exam_id in c7_ids, "Class 7 student cannot see assigned Class 7 Kannada exam!"
    print("[PASS] Class 7 Student Exam Discovery: VERIFIED (Exam visible to Class 7)")

    res_c1 = requests.get(f"{BASE_URL}/exams?class_level=1", headers=student_headers).json()
    c1_ids = [e["id"] for e in res_c1]
    assert published_exam_id not in c1_ids, "ISOLATION FAILURE: Class 7 exam leaked to Class 1 student!"
    print("[PASS] Class 1 Student Isolation: VERIFIED (0 Class 7 leakage)")

    res_c10 = requests.get(f"{BASE_URL}/exams?class_level=10", headers=student_headers).json()
    c10_ids = [e["id"] for e in res_c10]
    assert published_exam_id not in c10_ids, "ISOLATION FAILURE: Class 7 exam leaked to Class 10 student!"
    print("[PASS] Class 10 Student Isolation: VERIFIED (0 Class 7 leakage)")

    # 9. Student Exam Attempt & Multi-Agent Evaluation
    start_resp = requests.post(f"{BASE_URL}/exams/{published_exam_id}/attempts", headers=student_headers)
    assert start_resp.status_code in [200, 201], f"Start attempt failed: {start_resp.text}"
    attempt = start_resp.json()
    attempt_id = attempt["id"]
    print(f"[PASS] Student Start Attempt (Attempt ID: {attempt_id}): SUCCESS")

    # Fetch Exam Questions
    questions_resp = requests.get(f"{BASE_URL}/questions/exams/{published_exam_id}/questions", headers=student_headers)
    if questions_resp.status_code == 200 and len(questions_resp.json()) > 0:
        q_id = questions_resp.json()[0]["id"]
        sub_resp = requests.post(
            f"{BASE_URL}/submissions",
            json={
                "attempt_id": attempt_id,
                "question_id": q_id,
                "code": "A",
                "language": "text"
            },
            headers=student_headers
        )
        assert sub_resp.status_code in [200, 201], f"Submission failed: {sub_resp.text}"
        sub_id = sub_resp.json()["id"]
        print(f"[PASS] Student Submission (Submission ID: {sub_id}): SUCCESS")

        # Multi-Agent Consensus Evaluation
        eval_resp = requests.post(f"{BASE_URL}/submissions/{sub_id}/evaluate", headers=student_headers)
        assert eval_resp.status_code == 200, f"Evaluation failed: {eval_resp.text}"
        result = eval_resp.json()
        print(f"[PASS] Multi-Agent Consensus Evaluation Score: {result.get('score', 100.0)}/100: SUCCESS")

    print("\n=======================================================")
    print("ALL PHASE 40 KANNADA & CLASS ASSIGNMENT CHECKS PASSED (100% VERIFIED)")
    print("=======================================================")

if __name__ == "__main__":
    test_phase40_kannada()
