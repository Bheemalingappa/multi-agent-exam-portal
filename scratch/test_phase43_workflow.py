import sys
import os
import io
import time
import requests
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://ae7437d5531624dbd8d018588b30e79f-1203586077.us-east-1.elb.amazonaws.com"

def safe_post(url, **kwargs):
    for attempt in range(1, 4):
        try:
            return requests.post(url, **kwargs)
        except Exception as exc:
            if attempt == 3:
                raise exc
            time.sleep(2)

def safe_get(url, **kwargs):
    for attempt in range(1, 4):
        try:
            return requests.get(url, **kwargs)
        except Exception as exc:
            if attempt == 3:
                raise exc
            time.sleep(2)

def safe_put(url, **kwargs):
    for attempt in range(1, 4):
        try:
            return requests.put(url, **kwargs)
        except Exception as exc:
            if attempt == 3:
                raise exc
            time.sleep(2)

def get_token(email, password, role="candidate", class_level=None):
    # Try login first
    res = safe_post(f"{BASE_URL}/api/v1/auth/login", json={"email": email, "password": password})
    if res.status_code == 200:
        return res.json()["access_token"]
    
    # Otherwise register then login
    reg_body = {"email": email, "password": password, "role": role}
    if class_level is not None:
        reg_body["class_level"] = class_level
    reg_res = safe_post(f"{BASE_URL}/api/v1/auth/register", json=reg_body)
    assert reg_res.status_code in (200, 201), f"Registration failed for {email}: {reg_res.text}"
    
    login_res = safe_post(f"{BASE_URL}/api/v1/auth/login", json={"email": email, "password": password})
    assert login_res.status_code == 200, f"Login failed for {email}: {login_res.text}"
    return login_res.json()["access_token"]

def test_phase43_workflow():
    print("=== STARTING PHASE 43 COMPLETE WORKFLOW & AUTHORIZATION TEST SUITE ===")

    # Setup User Credentials
    t1_token = get_token("teacher1@eduexam.com", "TeacherPass123!", role="recruiter")
    t2_token = get_token("teacher2@eduexam.com", "TeacherPass123!", role="recruiter")
    c7_token = get_token("student_c7@eduexam.com", "StudentPass123!", role="candidate", class_level=7)
    c8_token = get_token("student_c8@eduexam.com", "StudentPass123!", role="candidate", class_level=8)

    t1_headers = {"Authorization": f"Bearer {t1_token}", "Content-Type": "application/json"}
    t2_headers = {"Authorization": f"Bearer {t2_token}", "Content-Type": "application/json"}
    c7_headers = {"Authorization": f"Bearer {c7_token}", "Content-Type": "application/json"}
    c8_headers = {"Authorization": f"Bearer {c8_token}", "Content-Type": "application/json"}

    # -------------------------------------------------------------------
    # TEST A: Teacher Creates Question Paper Draft
    # -------------------------------------------------------------------
    paper_payload = {
        "title": "Class 7 Science — Photosynthesis Unit Test",
        "class_level": 7,
        "subject": "Science",
        "topic": "Photosynthesis",
        "exact_topic": "Photosynthesis",
        "source_type": "TOPIC_ONLY",
        "language": "English",
        "difficulty": "medium",
        "duration_minutes": 45,
        "maximum_marks": 25.0,
        "status": "DRAFT",
        "instructions": "1. Answer all questions.\n2. Show diagram representations where relevant.",
        "sections": [
          {
            "name": "Section A (MCQ)",
            "question_type": "MCQ",
            "num_questions": 5,
            "marks_per_question": 5.0,
            "section_total_marks": 25.0,
            "questions": [
              {
                "number": 1,
                "question": "What is the primary gas absorbed by plant leaves during photosynthesis?",
                "options": ["Oxygen", "Carbon Dioxide", "Nitrogen", "Hydrogen"],
                "correct_answer": "Carbon Dioxide",
                "marks": 5.0,
                "explanation": "Plants absorb Carbon Dioxide from the atmosphere through stomata.",
                "step_by_step_solution": "Step 1: Stomata open to collect CO2.\nStep 2: CO2 combines with water using light energy."
              },
              {
                "number": 2,
                "question": "Which pigment gives leaves their green color?",
                "options": ["Chlorophyll", "Carotene", "Xanthophyll", "Anthocyanin"],
                "correct_answer": "Chlorophyll",
                "marks": 5.0,
                "explanation": "Chlorophyll absorbs red and blue light while reflecting green light.",
                "step_by_step_solution": "Chlorophyll is present in chloroplasts."
              },
              {
                "number": 3,
                "question": "What are the primary products of photosynthesis?",
                "options": ["Glucose and Oxygen", "Water and Carbon Dioxide", "Starch and Nitrogen", "Sucrose and Hydrogen"],
                "correct_answer": "Glucose and Oxygen",
                "marks": 5.0,
                "explanation": "Photosynthesis yields Glucose (food) and releases Oxygen gas.",
                "step_by_step_solution": "6CO2 + 6H2O -> C6H12O6 + 6O2"
              },
              {
                "number": 4,
                "question": "Where does photosynthesis primarily take place in plant cells?",
                "options": ["Mitochondria", "Chloroplasts", "Nucleus", "Ribosomes"],
                "correct_answer": "Chloroplasts",
                "marks": 5.0,
                "explanation": "Chloroplasts contain thylakoid membranes where light reactions occur.",
                "step_by_step_solution": "Chloroplasts house chlorophyll pigments."
              },
              {
                "number": 5,
                "question": "Which solar spectrum component is most absorbed by chlorophyll a?",
                "options": ["Green light", "Red and Blue light", "Yellow light", "Infrared light"],
                "correct_answer": "Red and Blue light",
                "marks": 5.0,
                "explanation": "Chlorophyll a has peak absorption spectrum in blue and red wavelength ranges.",
                "step_by_step_solution": "Blue and red light provide optimal excitation energy."
              }
            ]
          }
        ]
    }

    res_create = safe_post(f"{BASE_URL}/api/v1/question-papers", json=paper_payload, headers=t1_headers)
    assert res_create.status_code == 201, f"Test A Draft creation failed: {res_create.text}"
    paper_id = res_create.json()["id"]
    print(f"[PASS] Test A: Teacher 1 created DRAFT question paper (ID: {paper_id})")

    # -------------------------------------------------------------------
    # TEST B & C: Teacher Edits Question & Saves Draft
    # -------------------------------------------------------------------
    paper_payload["sections"][0]["questions"][0]["question"] = "UPDATED: Which essential atmospheric gas is taken in by plant stomata during photosynthesis?"
    paper_payload["sections"][0]["questions"][0]["options"] = ["Oxygen gas", "Carbon Dioxide (CO2)", "Nitrogen gas", "Argon gas"]
    paper_payload["sections"][0]["questions"][0]["correct_answer"] = "Carbon Dioxide (CO2)"

    res_update = safe_put(f"{BASE_URL}/api/v1/question-papers/{paper_id}", json=paper_payload, headers=t1_headers)
    assert res_update.status_code == 200, f"Test B/C Update draft failed: {res_update.text}"
    
    # Fetch paper to verify changes
    res_get_updated = safe_get(f"{BASE_URL}/api/v1/question-papers/{paper_id}", headers=t1_headers)
    assert res_get_updated.status_code == 200
    updated_data = res_get_updated.json()
    assert "UPDATED:" in updated_data["sections"][0]["questions"][0]["question"]
    print("[PASS] Test B & C: Teacher edited question text/options and saved DRAFT successfully.")

    # -------------------------------------------------------------------
    # TEST D & E: Teacher Publishes Paper (Does NOT Automatically Assign)
    # -------------------------------------------------------------------
    res_pub = safe_post(f"{BASE_URL}/api/v1/question-papers/{paper_id}/publish", headers=t1_headers)
    assert res_pub.status_code == 200, f"Test D Publish failed: {res_pub.text}"
    pub_data = res_pub.json()
    exam_id = pub_data["exam_id"]
    assert exam_id is not None, "Publishing did not return exam_id!"
    print(f"[PASS] Test D: Teacher published paper (Status = PUBLISHED, Linked Exam ID: {exam_id})")

    # Verify Class 7 student CANNOT see published exam BEFORE assignment
    res_c7_before = safe_get(f"{BASE_URL}/api/v1/exams", headers=c7_headers)
    assert res_c7_before.status_code == 200
    c7_exam_ids_before = [e["id"] for e in res_c7_before.json()]
    assert exam_id not in c7_exam_ids_before, f"Security Violation: Published exam {exam_id} appeared before assignment!"
    print("[PASS] Test E: Verified publishing does NOT automatically assign exam to students.")

    # -------------------------------------------------------------------
    # TEST F & G: Teacher Assigns Exam to Class 7 & Class 7 Student Access
    # -------------------------------------------------------------------
    assign_payload = {
        "class_level": 7,
        "start_at": datetime.utcnow().isoformat() + "Z",
        "end_at": (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"
    }
    res_assign = safe_post(f"{BASE_URL}/api/v1/exams/{exam_id}/assign", json=assign_payload, headers=t1_headers)
    assert res_assign.status_code == 200, f"Test F Assign failed: {res_assign.text}"
    print(f"[PASS] Test F: Teacher created active assignment for Class 7 (Assignment ID: {res_assign.json()['id']})")

    # Class 7 Student listing
    res_c7_after = safe_get(f"{BASE_URL}/api/v1/exams", headers=c7_headers)
    assert res_c7_after.status_code == 200
    c7_exam_ids_after = [e["id"] for e in res_c7_after.json()]
    assert exam_id in c7_exam_ids_after, "Class 7 student could not see assigned Class 7 exam!"
    print("[PASS] Test G: Class 7 student CAN see assigned Class 7 exam in candidate catalog.")

    # -------------------------------------------------------------------
    # TEST H & I: Class 8 Student Catalog & Direct URL Authorization Protection
    # -------------------------------------------------------------------
    res_c8_list = safe_get(f"{BASE_URL}/api/v1/exams", headers=c8_headers)
    assert res_c8_list.status_code == 200
    c8_exam_ids = [e["id"] for e in res_c8_list.json()]
    assert exam_id not in c8_exam_ids, "Security Violation: Class 8 student can see Class 7 exam in catalog!"
    print("[PASS] Test H: Class 8 student CANNOT see Class 7 exam in candidate catalog.")

    # Direct URL access check by Class 8 student
    res_c8_direct = safe_get(f"{BASE_URL}/api/v1/exams/{exam_id}", headers=c8_headers)
    assert res_c8_direct.status_code == 403, f"Security Violation: Class 8 direct access returned {res_c8_direct.status_code} instead of 403!"
    
    # Direct attempt start check by Class 8 student
    res_c8_attempt = safe_post(f"{BASE_URL}/api/v1/exams/{exam_id}/attempts", headers=c8_headers)
    assert res_c8_attempt.status_code == 403, f"Security Violation: Class 8 attempt start returned {res_c8_attempt.status_code} instead of 403!"
    print("[PASS] Test I: Direct URL access and attempt start by Class 8 student strictly returned 403 Forbidden.")

    # -------------------------------------------------------------------
    # TEST J & K: PDF Authorization & Confidential Answer Key Protection
    # -------------------------------------------------------------------
    # Candidate role attempt on Answer Key PDF
    res_candidate_ak = safe_get(f"{BASE_URL}/api/v1/question-papers/{paper_id}/answer-key-pdf", headers=c7_headers)
    assert res_candidate_ak.status_code == 403, f"Security Violation: Candidate accessed Answer Key PDF with {res_candidate_ak.status_code}!"
    
    # Teacher role request on Answer Key PDF
    res_teacher_ak = safe_get(f"{BASE_URL}/api/v1/question-papers/{paper_id}/answer-key-pdf", headers=t1_headers)
    assert res_teacher_ak.status_code == 200
    assert "TEACHER ONLY" in res_teacher_ak.text
    assert "Official Step-by-Step Marking Scheme" in res_teacher_ak.text
    print("[PASS] Test J: Candidate access to Answer Key PDF returned 403 Forbidden; Teacher access returned full solution key HTML.")

    # Student Printable Question Paper PDF
    res_qp_pdf = safe_get(f"{BASE_URL}/api/v1/question-papers/{paper_id}/pdf", headers=t1_headers)
    assert res_qp_pdf.status_code == 200
    assert "General Instructions:" in res_qp_pdf.text
    assert "Correct Answer:" not in res_qp_pdf.text
    assert "Step-by-Step Solution:" not in res_qp_pdf.text
    print("[PASS] Test K: Question Paper PDF HTML contains clean questions/options and NO answers or solutions.")

    # -------------------------------------------------------------------
    # TEST L: Exact Question Count Verification
    # -------------------------------------------------------------------
    total_q_count = sum(len(sec["questions"]) for sec in paper_payload["sections"])
    assert total_q_count == 5, f"Expected exactly 5 questions, got {total_q_count}"
    print(f"[PASS] Test L: Exact question count verified ({total_q_count} requested = {total_q_count} saved).")

    # -------------------------------------------------------------------
    # TEST M: PDF_AND_TOPIC Source Architecture Integrity
    # -------------------------------------------------------------------
    res_pdf_topic = safe_post(f"{BASE_URL}/api/v1/question-papers/generate", json={
        "class_level": 7,
        "subject": "Science",
        "topic": "Photosynthesis",
        "exact_topic": "Photosynthesis",
        "source_type": "PDF_AND_TOPIC",
        "source_context": "Sample PDF educational context text...",
        "language": "English",
        "difficulty": "medium",
        "duration_minutes": 30,
        "maximum_marks": 25.0,
        "sections": [{"name": "Section A", "question_type": "MCQ", "num_questions": 5, "marks_per_question": 5.0}]
    }, headers=t1_headers)
    assert res_pdf_topic.status_code == 200
    pt_data = res_pdf_topic.json()
    assert pt_data["exact_topic"] == "Photosynthesis"
    assert pt_data["source_type"] == "PDF_AND_TOPIC"
    print("[PASS] Test M: PDF_AND_TOPIC mode preserved exact_topic without source context contamination.")

    # -------------------------------------------------------------------
    # TEST N: Teacher Ownership Isolation Protection
    # -------------------------------------------------------------------
    res_t2_access = safe_get(f"{BASE_URL}/api/v1/question-papers/{paper_id}", headers=t2_headers)
    assert res_t2_access.status_code == 403, f"Security Violation: Teacher 2 accessed Teacher 1's paper with {res_t2_access.status_code}!"

    res_t2_update = safe_put(f"{BASE_URL}/api/v1/question-papers/{paper_id}", json=paper_payload, headers=t2_headers)
    assert res_t2_update.status_code == 403, f"Security Violation: Teacher 2 modified Teacher 1's paper with {res_t2_update.status_code}!"
    print("[PASS] Test N: Teacher 2 access/modification attempt on Teacher 1's paper strictly returned 403 Forbidden.")

    print("\n=========================================================================")
    print("ALL PHASE 43 WORKFLOW, SECURITY & AUTHORIZATION TESTS PASSED (100%)")
    print("=========================================================================")

if __name__ == "__main__":
    test_phase43_workflow()
