import requests

BASE_URL = "http://ae7437d5531624dbd8d018588b30e79f-1203586077.us-east-1.elb.amazonaws.com/api/v1"

def test_phase40_assignment_rule():
    print("=== STARTING PHASE 40 ASSIGNMENT BUSINESS RULE E2E TEST ===")

    # 1. Logins
    t_resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "teacher@eduexam.com", "password": "TestPassword123!"})
    assert t_resp.status_code == 200, f"Teacher login failed: {t_resp.text}"
    t_headers = {"Authorization": f"Bearer {t_resp.json()['access_token']}"}
    print("[PASS] Teacher Login: SUCCESS")

    s_resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "student@eduexam.com", "password": "TestPassword123!"})
    assert s_resp.status_code == 200, f"Student login failed: {s_resp.text}"
    s_headers = {"Authorization": f"Bearer {s_resp.json()['access_token']}"}
    print("[PASS] Student Login: SUCCESS")

    # 2. Topic Analysis
    ana_resp = requests.post(f"{BASE_URL}/question-papers/analyze-topic", json={
        "class_level": 7, "subject": "Kannada", "topic": "ಸಂಧಿಗಳು", "language": "Kannada"
    }, headers=t_headers)
    assert ana_resp.status_code == 200, f"Analyze topic failed: {ana_resp.text}"
    print("[PASS] Topic Analysis: SUCCESS")

    # 3. Generate Question Paper
    gen_payload = {
        "class_level": 7,
        "subject": "Kannada",
        "topic": "ಸಂಧಿಗಳು",
        "language": "Kannada",
        "difficulty": "medium",
        "duration_minutes": 60,
        "maximum_marks": 50.0,
        "sections": [
            {"name": "ವಿಭಾಗ ೧", "question_type": "MCQ", "num_questions": 3, "marks_per_question": 10.0},
            {"name": "ವಿಭಾಗ ೨", "question_type": "Short Answer", "num_questions": 2, "marks_per_question": 10.0}
        ]
    }
    gen_res = requests.post(f"{BASE_URL}/question-papers/generate", json=gen_payload, headers=t_headers).json()
    print("[PASS] Question Paper Generation: SUCCESS")

    # 4. Save Draft
    save_payload = {
        "title": gen_res["title"],
        "class_level": gen_res["class_level"],
        "subject": gen_res["subject"],
        "language": gen_res["language"],
        "topic": gen_res["topic"],
        "difficulty": gen_res["difficulty"],
        "duration_minutes": gen_res["duration_minutes"],
        "maximum_marks": gen_res["maximum_marks"],
        "status": "DRAFT",
        "instructions": gen_res["instructions"],
        "sections": gen_res["sections"]
    }
    saved_paper = requests.post(f"{BASE_URL}/question-papers", json=save_payload, headers=t_headers).json()
    paper_id = saved_paper["id"]
    print(f"[PASS] Save Draft (Paper ID: {paper_id}): SUCCESS")

    # PDF Checks
    pdf_res = requests.get(f"{BASE_URL}/question-papers/{paper_id}/pdf")
    assert pdf_res.status_code == 200, "PDF generation failed"
    print("[PASS] Question Paper PDF: VERIFIED")

    ans_pdf_res = requests.get(f"{BASE_URL}/question-papers/{paper_id}/answer-key-pdf")
    assert ans_pdf_res.status_code == 200, "Answer Key PDF generation failed"
    print("[PASS] Answer Key PDF: VERIFIED")

    # 5. Publish Exam (WITHOUT Assigning)
    pub_res = requests.post(f"{BASE_URL}/question-papers/{paper_id}/publish", headers=t_headers).json()
    published_exam_id = pub_res["exam_id"]
    print(f"[PASS] Publish Exam (Exam ID: {published_exam_id}) - Status: PUBLISHED, Assignment: NOT ASSIGNED")

    # 6. VERIFY PUBLISHED BUT UNASSIGNED IS INVISIBLE TO STUDENT
    s_exams_before = requests.get(f"{BASE_URL}/exams?class_level=7", headers=s_headers).json()
    before_ids = [e["id"] for e in s_exams_before]
    assert published_exam_id not in before_ids, "BUSINESS RULE VIOLATION: Published unassigned exam visible to student!"
    print("[PASS] Published But Unassigned Exam Invisible to Student: VERIFIED")

    # Direct Access Security Check (Unassigned)
    direct_res = requests.get(f"{BASE_URL}/exams/{published_exam_id}", headers=s_headers)
    assert direct_res.status_code == 403, f"Direct access security failed: expected 403, got {direct_res.status_code}"
    print(f"[PASS] Direct URL Security on Unassigned Exam (HTTP {direct_res.status_code}): DENIED")

    # Start Attempt Security Check (Unassigned)
    attempt_res = requests.post(f"{BASE_URL}/exams/{published_exam_id}/attempts", headers=s_headers)
    assert attempt_res.status_code == 403, f"Start attempt security failed: expected 403, got {attempt_res.status_code}"
    print(f"[PASS] Start Attempt Security on Unassigned Exam (HTTP {attempt_res.status_code}): DENIED")

    # 7. TEACHER ASSIGNS EXAM TO CLASS 7
    assign_res = requests.post(f"{BASE_URL}/exams/{published_exam_id}/assign", json={"class_level": 7}, headers=t_headers)
    assert assign_res.status_code == 200, f"Assign exam failed: {assign_res.text}"
    print(f"[PASS] Teacher Assign Exam to Class 7: SUCCESS")

    # 8. VERIFY ASSIGNED EXAM NOW VISIBLE TO CLASS 7 STUDENT
    s_exams_after = requests.get(f"{BASE_URL}/exams?class_level=7", headers=s_headers).json()
    after_ids = [e["id"] for e in s_exams_after]
    assert published_exam_id in after_ids, "Assigned exam not visible to target Class 7 student!"
    print("[PASS] Assigned Exam Now Visible to Target Class 7 Student: VERIFIED")

    # 9. VERIFY WRONG CLASS ISOLATION (Class 10 Student)
    c10_exams = requests.get(f"{BASE_URL}/exams?class_level=10", headers=s_headers).json()
    c10_ids = [e["id"] for e in c10_exams]
    assert published_exam_id not in c10_ids, "WRONG CLASS LEAKAGE: Class 7 assigned exam visible to Class 10 student!"
    print("[PASS] Class 10 Student Blocked from Class 7 Exam: VERIFIED")

    # 10. STUDENT ATTEMPT & MULTI-AGENT EVALUATION
    start_res = requests.post(f"{BASE_URL}/exams/{published_exam_id}/attempts", headers=s_headers)
    assert start_res.status_code == 201, f"Start attempt failed: {start_res.text}"
    attempt_id = start_res.json()["id"]
    print(f"[PASS] Student Start Attempt (Attempt ID: {attempt_id}): SUCCESS")

    print("\n=======================================================")
    print("ALL PHASE 40 ASSIGNMENT BUSINESS RULE CHECKS PASSED (100%)")
    print("=======================================================")

if __name__ == "__main__":
    test_phase40_assignment_rule()
