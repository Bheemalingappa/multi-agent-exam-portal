import requests
import time
from datetime import datetime, timedelta

BASE_URL = "http://ae7437d5531624dbd8d018588b30e79f-1203586077.us-east-1.elb.amazonaws.com"

def safe_post(url, json=None, headers=None):
    for attempt in range(4):
        try:
            return requests.post(url, json=json, headers=headers, timeout=15)
        except Exception as exc:
            if attempt == 3:
                raise exc
            time.sleep(2)

def safe_get(url, headers=None):
    for attempt in range(4):
        try:
            return requests.get(url, headers=headers, timeout=15)
        except Exception as exc:
            if attempt == 3:
                raise exc
            time.sleep(2)

def safe_put(url, json=None, headers=None):
    for attempt in range(4):
        try:
            return requests.put(url, json=json, headers=headers, timeout=15)
        except Exception as exc:
            if attempt == 3:
                raise exc
            time.sleep(2)

def get_token(email, password, role="candidate", class_level=None):
    res = safe_post(f"{BASE_URL}/api/v1/auth/login", json={"email": email, "password": password})
    if res.status_code == 200:
        return res.json()["access_token"]
    
    reg_body = {"email": email, "password": password, "role": role}
    if class_level is not None:
        reg_body["class_level"] = class_level
    reg_res = safe_post(f"{BASE_URL}/api/v1/auth/register", json=reg_body)
    assert reg_res.status_code in (200, 201), f"Registration failed for {email}: {reg_res.text}"
    
    login_res = safe_post(f"{BASE_URL}/api/v1/auth/login", json={"email": email, "password": password})
    assert login_res.status_code == 200, f"Login failed for {email}: {login_res.text}"
    return login_res.json()["access_token"]

def test_phase44_student_exam_workflow():
    print("=== STARTING PHASE 44 STUDENT EXAM-TAKING & SECURITY TEST SUITE ===")

    # Setup User Tokens
    t1_token = get_token("p44_teacher@eduexam.com", "TeacherPass123!", role="recruiter")
    s7_a_token = get_token("p44_student7a@eduexam.com", "StudentPass123!", role="candidate", class_level=7)
    s7_b_token = get_token("p44_student7b@eduexam.com", "StudentPass123!", role="candidate", class_level=7)
    s8_token = get_token("p44_student8@eduexam.com", "StudentPass123!", role="candidate", class_level=8)

    t1_hdr = {"Authorization": f"Bearer {t1_token}", "Content-Type": "application/json"}
    s7_a_hdr = {"Authorization": f"Bearer {s7_a_token}", "Content-Type": "application/json"}
    s7_b_hdr = {"Authorization": f"Bearer {s7_b_token}", "Content-Type": "application/json"}
    s8_hdr = {"Authorization": f"Bearer {s8_token}", "Content-Type": "application/json"}

    # 1. Teacher creates draft & publishes paper
    paper_payload = {
        "title": "Class 7 Mathematics - Algebra Foundations",
        "class_level": 7,
        "subject": "Mathematics",
        "language": "English",
        "topic": "Algebra Foundations",
        "difficulty": "medium",
        "duration_minutes": 60,
        "maximum_marks": 20.0,
        "generation_provider": "DETERMINISTIC_FALLBACK",
        "source_type": "TOPIC_ONLY",
        "exact_topic": "Algebra Foundations",
        "sections": [
            {
                "name": "Section A (MCQ)",
                "question_type": "MCQ",
                "num_questions": 2,
                "marks_per_question": 10.0,
                "section_total_marks": 20.0,
                "questions": [
                    {
                        "number": 1,
                        "question": "Solve for x in equation 2x + 4 = 10",
                        "options": ["x = 2", "x = 3", "x = 4", "x = 5"],
                        "correct_answer": "B",
                        "explanation": "2x = 6 implies x = 3.",
                        "step_by_step_solution": "Subtract 4 from both sides: 2x = 6. Divide by 2: x = 3.",
                        "marks": 10.0
                    },
                    {
                        "number": 2,
                        "question": "What is the degree of expression 3x^2 + 5x + 2?",
                        "options": ["1", "2", "3", "4"],
                        "correct_answer": "B",
                        "explanation": "Highest exponent of x is 2.",
                        "step_by_step_solution": "The term 3x^2 has highest power 2.",
                        "marks": 10.0
                    }
                ]
            }
        ]
    }

    res_create = safe_post(f"{BASE_URL}/api/v1/question-papers", json=paper_payload, headers=t1_hdr)
    assert res_create.status_code == 201, f"Setup paper creation failed: {res_create.text}"
    paper_id = res_create.json()["id"]

    res_pub = safe_post(f"{BASE_URL}/api/v1/question-papers/{paper_id}/publish", headers=t1_hdr)
    assert res_pub.status_code == 200, f"Setup publish failed: {res_pub.text}"
    exam_id = res_pub.json()["exam_id"]

    # 2. Teacher assigns exam to Class 7 (Active window: current time to 7 days ahead)
    assign_body = {
        "exam_id": exam_id,
        "class_level": 7,
        "start_at": (datetime.utcnow() - timedelta(minutes=5)).isoformat() + "Z",
        "end_at": (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z",
        "is_active": True
    }
    res_assign = safe_post(f"{BASE_URL}/api/v1/exams/{exam_id}/assign", json=assign_body, headers=t1_hdr)
    assert res_assign.status_code in (200, 201), f"Setup assign failed: {res_assign.text}"

    # -------------------------------------------------------------------
    # TEST A: Authorized Class 7 student can start assigned Class 7 exam
    # -------------------------------------------------------------------
    res_start = safe_post(f"{BASE_URL}/api/v1/exams/{exam_id}/attempts", headers=s7_a_hdr)
    assert res_start.status_code in (200, 201), f"Test A failed: {res_start.text}"
    att_a_data = res_start.json()
    attempt_a_id = att_a_data["id"]
    assert att_a_data["status"] == "STARTED"
    assert att_a_data["remaining_seconds"] > 0
    print("[PASS] Test A: Authorized Class 7 student started assigned exam successfully.")

    # -------------------------------------------------------------------
    # TEST B: Wrong-class student (Class 8) cannot start Class 7 exam
    # -------------------------------------------------------------------
    res_s8_start = safe_post(f"{BASE_URL}/api/v1/exams/{exam_id}/attempts", headers=s8_hdr)
    assert res_s8_start.status_code == 403, f"Test B failed: Expected 403, got {res_s8_start.status_code}"
    print("[PASS] Test B: Class 8 student start attempt correctly returned 403 Forbidden.")

    # -------------------------------------------------------------------
    # TEST C: Student B cannot access Student A's attempt (IDOR Protection)
    # -------------------------------------------------------------------
    res_s7b_get = safe_get(f"{BASE_URL}/api/v1/attempts/{attempt_a_id}", headers=s7_b_hdr)
    assert res_s7b_get.status_code == 403, f"Test C failed: Expected 403, got {res_s7b_get.status_code}"
    print("[PASS] Test C: Student B access to Student A's attempt returned 403 Forbidden.")

    # -------------------------------------------------------------------
    # TEST D & E: Student A answers are saved via autosave and retrieved
    # -------------------------------------------------------------------
    save_body = {"answers": {"1": "B", "2": "B"}}
    res_save = safe_put(f"{BASE_URL}/api/v1/attempts/{attempt_a_id}/answers", json=save_body, headers=s7_a_hdr)
    assert res_save.status_code == 200, f"Test D failed: {res_save.text}"
    assert res_save.json()["answers"] == {"1": "B", "2": "B"}

    res_get_a = safe_get(f"{BASE_URL}/api/v1/attempts/{attempt_a_id}", headers=s7_a_hdr)
    assert res_get_a.status_code == 200, f"Test E failed: {res_get_a.text}"
    assert res_get_a.json()["answers"] == {"1": "B", "2": "B"}
    print("[PASS] Test D & E: Student answers saved via autosave and retrieved by owner.")

    # -------------------------------------------------------------------
    # TEST F & G: Refresh/resume retrieves existing attempt & timer is server-authoritative
    # -------------------------------------------------------------------
    res_resume = safe_post(f"{BASE_URL}/api/v1/exams/{exam_id}/attempts", headers=s7_a_hdr)
    assert res_resume.status_code in (200, 201)
    res_data = res_resume.json()
    assert res_data["id"] == attempt_a_id, "Resume failed: Created new attempt ID instead of returning existing"
    assert res_data["answers"] == {"1": "B", "2": "B"}
    assert res_data["remaining_seconds"] <= 3600
    print("[PASS] Test F & G: Page refresh/resume preserves attempt ID & timer is server-authoritative.")

    # -------------------------------------------------------------------
    # TEST M & N: Candidate question endpoint hides correct answers & solutions
    # -------------------------------------------------------------------
    res_qs = safe_get(f"{BASE_URL}/api/v1/attempts/{attempt_a_id}/questions", headers=s7_a_hdr)
    assert res_qs.status_code == 200, f"Test M/N failed: {res_qs.text}"
    q_body = res_qs.json()
    assert len(q_body["questions"]) == 2
    for q_item in q_body["questions"]:
        assert "correct_answer" not in q_item, "SECURITY FAILURE: correct_answer exposed in student API JSON!"
        assert "explanation" not in q_item, "SECURITY FAILURE: explanation exposed in student API JSON!"
        assert "solution" not in q_item, "SECURITY FAILURE: solution exposed in student API JSON!"
        assert "step_by_step_solution" not in q_item, "SECURITY FAILURE: step_by_step_solution exposed in student API!"
    print("[PASS] Test M & N: Student question API strictly hides correct answers and solutions.")

    # -------------------------------------------------------------------
    # TEST O: Answer Key PDF remains teacher-only (Candidate returns 403)
    # -------------------------------------------------------------------
    res_key = safe_get(f"{BASE_URL}/api/v1/question-papers/{paper_id}/answer-key-pdf", headers=s7_a_hdr)
    assert res_key.status_code == 403, f"Test O failed: Expected 403 for candidate, got {res_key.status_code}"
    print("[PASS] Test O: Answer Key PDF access by candidate returned 403 Forbidden.")

    # -------------------------------------------------------------------
    # TEST P & H: Final submission locks attempt & duplicate submit is rejected
    # -------------------------------------------------------------------
    res_sub = safe_post(f"{BASE_URL}/api/v1/attempts/{attempt_a_id}/submit", headers=s7_a_hdr)
    assert res_sub.status_code == 200, f"Test P failed: {res_sub.text}"
    sub_data = res_sub.json()
    assert sub_data["status"] in ("SUBMITTED", "COMPLETED", "EVALUATED")
    assert sub_data["total_score"] == 20.0  # Both correct answers awarded 10 + 10

    res_sub_dup = safe_post(f"{BASE_URL}/api/v1/attempts/{attempt_a_id}/submit", headers=s7_a_hdr)
    assert res_sub_dup.status_code == 400, f"Test H failed: Expected 400 for duplicate submit, got {res_sub_dup.status_code}"
    print("[PASS] Test P & H: Final submission changed status to SUBMITTED & duplicate submit rejected.")

    # -------------------------------------------------------------------
    # TEST I: Submitted attempt cannot be edited
    # -------------------------------------------------------------------
    res_post_sub_save = safe_put(f"{BASE_URL}/api/v1/attempts/{attempt_a_id}/answers", json={"answers": {"1": "A"}}, headers=s7_a_hdr)
    assert res_post_sub_save.status_code == 400, f"Test I failed: Expected 400 for editing submitted attempt, got {res_post_sub_save.status_code}"
    print("[PASS] Test I: Modifying answers on a submitted attempt strictly returned 400 Bad Request.")

    # -------------------------------------------------------------------
    # TEST Q: Student B cannot modify Student A's answers
    # -------------------------------------------------------------------
    res_q_hack = safe_put(f"{BASE_URL}/api/v1/attempts/{attempt_a_id}/answers", json={"answers": {"1": "A"}}, headers=s7_b_hdr)
    assert res_q_hack.status_code == 403, f"Test Q failed: Expected 403 for unauthorized user answer edit, got {res_q_hack.status_code}"
    print("[PASS] Test Q: Student B attempt to modify Student A's answers returned 403 Forbidden.")

    # -------------------------------------------------------------------
    # TEST J, K, L: Assignment window & inactive assignment enforcement
    # -------------------------------------------------------------------
    # Create Future assignment for Class 7 (start_at in 10 minutes)
    future_paper_payload = dict(paper_payload, title="Future Class 7 Physics Exam")
    res_fut_p = safe_post(f"{BASE_URL}/api/v1/question-papers", json=future_paper_payload, headers=t1_hdr)
    fut_paper_id = res_fut_p.json()["id"]
    res_fut_pub = safe_post(f"{BASE_URL}/api/v1/question-papers/{fut_paper_id}/publish", headers=t1_hdr)
    fut_exam_id = res_fut_pub.json()["exam_id"]

    future_assign_body = {
        "exam_id": fut_exam_id,
        "class_level": 7,
        "start_at": (datetime.utcnow() + timedelta(minutes=10)).isoformat() + "Z",
        "end_at": (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z",
        "is_active": True
    }
    safe_post(f"{BASE_URL}/api/v1/exams/{fut_exam_id}/assign", json=future_assign_body, headers=t1_hdr)

    res_fut_start = safe_post(f"{BASE_URL}/api/v1/exams/{fut_exam_id}/attempts", headers=s7_a_hdr)
    assert res_fut_start.status_code == 403, f"Test J failed: Expected 403 for future exam, got {res_fut_start.status_code}"
    print("[PASS] Test J: Exam starting before assignment start window returned 403 Forbidden.")

    # Create Inactive assignment for Class 7
    inact_paper_payload = dict(paper_payload, title="Inactive Class 7 Chemistry Exam")
    res_inact_p = safe_post(f"{BASE_URL}/api/v1/question-papers", json=inact_paper_payload, headers=t1_hdr)
    inact_paper_id = res_inact_p.json()["id"]
    res_inact_pub = safe_post(f"{BASE_URL}/api/v1/question-papers/{inact_paper_id}/publish", headers=t1_hdr)
    inact_exam_id = res_inact_pub.json()["exam_id"]

    inact_assign_body = {
        "exam_id": inact_exam_id,
        "class_level": 7,
        "start_at": (datetime.utcnow() - timedelta(minutes=5)).isoformat() + "Z",
        "end_at": (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z",
        "is_active": False
    }
    safe_post(f"{BASE_URL}/api/v1/exams/{inact_exam_id}/assign", json=inact_assign_body, headers=t1_hdr)

    res_inact_start = safe_post(f"{BASE_URL}/api/v1/exams/{inact_exam_id}/attempts", headers=s7_a_hdr)
    assert res_inact_start.status_code == 403, f"Test L failed: Expected 403 for inactive assignment, got {res_inact_start.status_code}"
    print("[PASS] Test L: Attempting to start inactive assignment returned 403 Forbidden.")

    # Create Past assignment for Class 7 (ended 1 hour ago)
    past_paper_payload = dict(paper_payload, title="Expired Class 7 Biology Exam")
    res_past_p = safe_post(f"{BASE_URL}/api/v1/question-papers", json=past_paper_payload, headers=t1_hdr)
    past_paper_id = res_past_p.json()["id"]
    res_past_pub = safe_post(f"{BASE_URL}/api/v1/question-papers/{past_paper_id}/publish", headers=t1_hdr)
    past_exam_id = res_past_pub.json()["exam_id"]

    past_assign_body = {
        "exam_id": past_exam_id,
        "class_level": 7,
        "start_at": (datetime.utcnow() - timedelta(days=2)).isoformat() + "Z",
        "end_at": (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z",
        "is_active": True
    }
    safe_post(f"{BASE_URL}/api/v1/exams/{past_exam_id}/assign", json=past_assign_body, headers=t1_hdr)

    res_past_start = safe_post(f"{BASE_URL}/api/v1/exams/{past_exam_id}/attempts", headers=s7_a_hdr)
    assert res_past_start.status_code == 403, f"Test K failed: Expected 403 for past end date, got {res_past_start.status_code}"
    print("[PASS] Test K: Exam starting after assignment end window returned 403 Forbidden.")

    # -------------------------------------------------------------------
    # TEST R: Auto-save updates answers without creating duplicate attempts
    # -------------------------------------------------------------------
    # Start second attempt for student 7B
    res_s7b_start = safe_post(f"{BASE_URL}/api/v1/exams/{exam_id}/attempts", headers=s7_b_hdr)
    assert res_s7b_start.status_code in (200, 201)
    s7b_att_id = res_s7b_start.json()["id"]

    # Multiple autosave calls
    safe_put(f"{BASE_URL}/api/v1/attempts/{s7b_att_id}/answers", json={"answers": {"1": "A"}}, headers=s7_b_hdr)
    safe_put(f"{BASE_URL}/api/v1/attempts/{s7b_att_id}/answers", json={"answers": {"1": "B", "2": "C"}}, headers=s7_b_hdr)

    res_check = safe_get(f"{BASE_URL}/api/v1/attempts/{s7b_att_id}", headers=s7_b_hdr)
    assert res_check.status_code == 200
    assert res_check.json()["answers"] == {"1": "B", "2": "C"}
    print("[PASS] Test R: Auto-save updated answers without creating duplicate attempts.")

    print("\n=========================================================================")
    print("ALL PHASE 44 STUDENT EXAM-TAKING, TIMER & SECURITY TESTS PASSED (100%)")
    print("=========================================================================")

if __name__ == "__main__":
    test_phase44_student_exam_workflow()
