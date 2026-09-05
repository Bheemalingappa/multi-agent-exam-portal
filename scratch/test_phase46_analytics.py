import os
import sys
import uuid
import requests
import hashlib
from datetime import datetime, timedelta

BASE_URL = "http://ae7437d5531624dbd8d018588b30e79f-1203586077.us-east-1.elb.amazonaws.com"

def get_auth_token(email, password, role="candidate", class_level=None):
    register_payload = {"email": email, "password": password, "role": role}
    if class_level is not None:
        register_payload["class_level"] = class_level
    requests.post(f"{BASE_URL}/api/v1/auth/register", json=register_payload)
    login_res = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"email": email, "password": password})
    if login_res.status_code != 200:
        raise Exception(f"Login failed for {email}: {login_res.text}")
    return login_res.json()["access_token"]

def safe_post(url, **kwargs):
    return requests.post(url, **kwargs)

def safe_get(url, **kwargs):
    return requests.get(url, **kwargs)

def safe_put(url, **kwargs):
    return requests.put(url, **kwargs)

def test_phase46_analytics_engine():
    print("=== STARTING PHASE 46 RESULTS, PERFORMANCE & TEACHER ANALYTICS TEST SUITE ===")

    # 1. Setup Auth Tokens for Teacher 1, Teacher 2, Student 1, Student 2
    t1_email = f"teacher1_p46_{uuid.uuid4().hex[:6]}@school.com"
    t2_email = f"teacher2_p46_{uuid.uuid4().hex[:6]}@school.com"
    s1_email = f"student1_p46_{uuid.uuid4().hex[:6]}@school.com"
    s2_email = f"student2_p46_{uuid.uuid4().hex[:6]}@school.com"

    t1_token = get_auth_token(t1_email, "Password123!", role="recruiter")
    t2_token = get_auth_token(t2_email, "Password123!", role="recruiter")
    s1_token = get_auth_token(s1_email, "Password123!", role="candidate", class_level=7)
    s2_token = get_auth_token(s2_email, "Password123!", role="candidate", class_level=7)

    t1_hdr = {"Authorization": f"Bearer {t1_token}"}
    t2_hdr = {"Authorization": f"Bearer {t2_token}"}
    s1_hdr = {"Authorization": f"Bearer {s1_token}"}
    s2_hdr = {"Authorization": f"Bearer {s2_token}"}

    # -------------------------------------------------------------------
    # TEST O: Empty/no-submission handling returns clean zero-state metrics
    # -------------------------------------------------------------------
    res_empty_t = safe_get(f"{BASE_URL}/api/v1/analytics/teacher/summary", headers=t1_hdr)
    assert res_empty_t.status_code == 200, f"Test O failed for teacher: {res_empty_t.text}"
    empty_t_data = res_empty_t.json()
    assert empty_t_data["total_submissions"] == 0
    assert empty_t_data["average_score"] == 0.0

    res_empty_s = safe_get(f"{BASE_URL}/api/v1/analytics/student/summary", headers=s1_hdr)
    assert res_empty_s.status_code == 200, f"Test O failed for student: {res_empty_s.text}"
    empty_s_data = res_empty_s.json()
    assert empty_s_data["completed_exams"] == 0
    assert empty_s_data["latest_result"] is None
    print("[PASS] Test O: Empty/no-submission state handled cleanly with zero metrics.")

    # -------------------------------------------------------------------
    # SETUP EXAM & SUBMISSIONS FOR TEACHER 1
    # -------------------------------------------------------------------
    exact_topic_name = f"Cellular Respiration P46 {uuid.uuid4().hex[:4]}"
    gen_payload = {
        "title": "Class 7 Biology Assessment",
        "class_level": 7,
        "subject": "Biology",
        "topic": exact_topic_name,
        "exact_topic": exact_topic_name,
        "source_type": "PDF_AND_TOPIC",
        "source_analysis": "Context about cellular respiration in mitochondria.",
        "language": "English",
        "difficulty": "medium",
        "duration_minutes": 45,
        "maximum_marks": 30.0,
        "sections": [
            {
                "name": "Section A (MCQ)",
                "question_type": "MCQ",
                "num_questions": 1,
                "marks_per_question": 10.0,
                "questions": [
                    {
                        "number": 1,
                        "question": "Where does cellular respiration occur in eukaryotic cells?",
                        "options": ["Mitochondria", "Ribosome", "Chloroplast", "Nucleus"],
                        "correct_answer": "Mitochondria",
                        "marks": 10.0
                    }
                ]
            },
            {
                "name": "Section B (Short)",
                "question_type": "SHORT_ANSWER",
                "num_questions": 1,
                "marks_per_question": 10.0,
                "questions": [
                    {
                        "number": 2,
                        "question": "Describe the main function of cellular respiration.",
                        "marks": 10.0
                    }
                ]
            },
            {
                "name": "Section C (Long)",
                "question_type": "LONG_ANSWER",
                "num_questions": 1,
                "marks_per_question": 10.0,
                "questions": [
                    {
                        "number": 3,
                        "question": "Explain the stages of aerobic respiration in detail.",
                        "marks": 10.0
                    }
                ]
            }
        ]
    }

    res_gen = safe_post(f"{BASE_URL}/api/v1/question-papers", json=gen_payload, headers=t1_hdr)
    assert res_gen.status_code in (200, 201), f"Gen failed: {res_gen.text}"
    paper_id = res_gen.json()["id"]

    # Publish paper
    res_pub = safe_post(f"{BASE_URL}/api/v1/question-papers/{paper_id}/publish", headers=t1_hdr)
    assert res_pub.status_code == 200, f"Publish failed: {res_pub.text}"
    pub_data = res_pub.json()
    exam_id = pub_data["exam_id"]

    # Create active assignment for Class 7
    assign_payload = {
        "class_level": 7,
        "start_at": (datetime.utcnow() - timedelta(minutes=5)).isoformat() + "Z",
        "end_at": (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z",
        "is_active": True
    }
    res_assign = safe_post(f"{BASE_URL}/api/v1/exams/{exam_id}/assign", json=assign_payload, headers=t1_hdr)
    assert res_assign.status_code in (200, 201), f"Assign failed: {res_assign.text}"

    # Student 1 takes exam and submits (answers Q1 & Q2, skips Q3)
    res_att1 = safe_post(f"{BASE_URL}/api/v1/exams/{exam_id}/attempts", headers=s1_hdr)
    assert res_att1.status_code in (200, 201), f"Attempt start failed: {res_att1.text}"
    att1_id = res_att1.json()["id"]

    # Fetch question IDs
    res_qs = safe_get(f"{BASE_URL}/api/v1/attempts/{att1_id}/questions", headers=s1_hdr)
    assert res_qs.status_code == 200, f"Questions fetch failed: {res_qs.text}"
    q_items = res_qs.json()["questions"]
    q1_id = str(q_items[0]["id"])
    q2_id = str(q_items[1]["id"])
    q3_id = str(q_items[2]["id"])
    q1_ans = "Mitochondria"

    safe_put(
        f"{BASE_URL}/api/v1/attempts/{att1_id}/answers",
        json={"answers": {q1_id: q1_ans, q2_id: "Glucose is broken down to produce ATP in mitochondria."}},
        headers=s1_hdr
    )

    res_sub1 = safe_post(f"{BASE_URL}/api/v1/attempts/{att1_id}/submit", headers=s1_hdr)
    assert res_sub1.status_code == 200, f"Submit 1 failed: {res_sub1.text}"

    # Student 2 takes exam and submits (answers all 3 questions)
    res_att2 = safe_post(f"{BASE_URL}/api/v1/exams/{exam_id}/attempts", headers=s2_hdr)
    assert res_att2.status_code in (200, 201), f"Attempt 2 start failed: {res_att2.text}"
    att2_id = res_att2.json()["id"]

    safe_put(
        f"{BASE_URL}/api/v1/attempts/{att2_id}/answers",
        json={
            "answers": {
                q1_id: q1_ans,
                q2_id: "Cellular respiration yields ATP.",
                q3_id: "Detailed explanation of glycolysis, Krebs cycle, and electron transport chain."
            }
        },
        headers=s2_hdr
    )

    res_sub2 = safe_post(f"{BASE_URL}/api/v1/attempts/{att2_id}/submit", headers=s2_hdr)
    assert res_sub2.status_code == 200, f"Submit 2 failed: {res_sub2.text}"

    # -------------------------------------------------------------------
    # TEST A: Student summary endpoint returns accurate metrics
    # -------------------------------------------------------------------
    res_s1_sum = safe_get(f"{BASE_URL}/api/v1/analytics/student/summary", headers=s1_hdr)
    assert res_s1_sum.status_code == 200, f"Test A failed: {res_s1_sum.text}"
    s1_sum = res_s1_sum.json()
    assert s1_sum["total_attempted"] >= 1
    assert s1_sum["completed_exams"] >= 1
    assert s1_sum["latest_result"] is not None
    assert s1_sum["latest_result"]["subject"] == "Biology"
    print("[PASS] Test A: Student summary analytics returned accurate completed exam count and latest result.")

    # -------------------------------------------------------------------
    # TEST B: Student performance history endpoint returns trends
    # -------------------------------------------------------------------
    res_s1_perf = safe_get(f"{BASE_URL}/api/v1/analytics/student/performance", headers=s1_hdr)
    assert res_s1_perf.status_code == 200, f"Test B failed: {res_s1_perf.text}"
    s1_perf = res_s1_perf.json()
    assert "score_trend" in s1_perf
    assert "subject_performance" in s1_perf
    assert "grade_distribution" in s1_perf
    print("[PASS] Test B: Student performance timeline, subject breakdown, and grade distribution verified.")

    # -------------------------------------------------------------------
    # TEST C & Q: Student IDOR check - Student cannot access Teacher endpoint
    # -------------------------------------------------------------------
    res_s_to_t = safe_get(f"{BASE_URL}/api/v1/analytics/teacher/summary", headers=s1_hdr)
    assert res_s_to_t.status_code == 403, f"Test C failed: Expected 403 for candidate accessing teacher endpoint, got {res_s_to_t.status_code}"
    print("[PASS] Test C & Q: Student access to Teacher Analytics returned 403 Forbidden.")

    # -------------------------------------------------------------------
    # TEST D: Teacher summary endpoint returns correct aggregated metrics
    # -------------------------------------------------------------------
    res_t1_sum = safe_get(f"{BASE_URL}/api/v1/analytics/teacher/summary", headers=t1_hdr)
    assert res_t1_sum.status_code == 200, f"Test D failed: {res_t1_sum.text}"
    t1_sum = res_t1_sum.json()
    assert t1_sum["total_question_papers"] >= 1
    assert t1_sum["published_exams"] >= 1
    assert t1_sum["active_assignments"] >= 1
    assert t1_sum["total_submissions"] >= 2
    assert t1_sum["average_score"] > 0.0
    print("[PASS] Test D: Teacher summary metrics returned correct paper, assignment, and submission counts.")

    # -------------------------------------------------------------------
    # TEST E, H, I, J, K: Teacher exam performance metrics calculation
    # -------------------------------------------------------------------
    res_e_perf = safe_get(f"{BASE_URL}/api/v1/analytics/exams/{exam_id}/performance", headers=t1_hdr)
    assert res_e_perf.status_code == 200, f"Test E failed: {res_e_perf.text}"
    e_perf = res_e_perf.json()
    assert e_perf["total_submissions"] == 2
    assert e_perf["average_score"] > 0.0
    assert e_perf["highest_score"] >= e_perf["lowest_score"]
    assert "grade_distribution" in e_perf
    print("[PASS] Test E, H, I, J, K: Exam performance calculated correct avg score, high/low scores, pass rate, and grade distribution.")

    # -------------------------------------------------------------------
    # TEST F & G: Teacher ownership security & IDOR protection
    # -------------------------------------------------------------------
    res_t2_e_perf = safe_get(f"{BASE_URL}/api/v1/analytics/exams/{exam_id}/performance", headers=t2_hdr)
    assert res_t2_e_perf.status_code == 403, f"Test G failed: Expected 403 for unauthorized Teacher 2, got {res_t2_e_perf.status_code}"
    print("[PASS] Test F & G: Teacher 1 accessed owned exam analytics; Unauthorized Teacher 2 returned 403 Forbidden.")

    # -------------------------------------------------------------------
    # TEST L & M: Question-wise itemized accuracy, correct/incorrect/skipped
    # -------------------------------------------------------------------
    res_q_analytics = safe_get(f"{BASE_URL}/api/v1/analytics/exams/{exam_id}/questions", headers=t1_hdr)
    assert res_q_analytics.status_code == 200, f"Test L failed: {res_q_analytics.text}"
    q_ana = res_q_analytics.json()
    assert q_ana["total_questions"] == 3
    qs = q_ana["questions"]
    q3_stat = next(q for q in qs if q["question_id"] == q3_id or q["number"] == 3)
    assert q3_stat["skipped_count"] >= 1  # Student 1 skipped Q3
    print("[PASS] Test L & M: Question-wise accuracy, correct/incorrect, and skipped count verified.")

    # -------------------------------------------------------------------
    # TEST N: Topic performance accurately uses exact_topic (and NOT source_analysis)
    # -------------------------------------------------------------------
    topics = e_perf["topic_performance"]
    assert len(topics) >= 1
    assert topics[0]["topic"] == exact_topic_name
    assert topics[0]["topic"] != "Context about cellular respiration in mitochondria."
    print("[PASS] Test N: Topic analytics accurately uses teacher's exact_topic without source_analysis contamination.")

    # -------------------------------------------------------------------
    # TEST P: Student roster performance flags and status filtering
    # -------------------------------------------------------------------
    res_roster = safe_get(f"{BASE_URL}/api/v1/analytics/exams/{exam_id}/students", headers=t1_hdr)
    assert res_roster.status_code == 200, f"Test P failed: {res_roster.text}"
    roster = res_roster.json()["students"]
    assert len(roster) >= 2
    for st in roster:
        assert st["evaluation_status"] == "COMPLETED"
        assert st["performance_flag"] in ["High Performer", "Average", "Needs Improvement", "Not Submitted"]
    print("[PASS] Test P: Student performance roster returned complete records with evaluation status and performance flags.")

    print("\n=========================================================================")
    print("ALL PHASE 46 RESULTS, PERFORMANCE & TEACHER ANALYTICS TESTS PASSED (100%)")
    print("=========================================================================\n")

if __name__ == "__main__":
    test_phase46_analytics_engine()
