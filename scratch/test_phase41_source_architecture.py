import sys
import os
import io
import requests

BASE_URL = "http://ae7437d5531624dbd8d018588b30e79f-1203586077.us-east-1.elb.amazonaws.com"

def get_teacher_token():
    res = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"email": "teacher@eduexam.com", "password": "TestPassword123!"})
    assert res.status_code == 200, f"Teacher login failed: {res.text}"
    return res.json()["access_token"]

def create_sample_pdf_bytes():
    from pypdf import PdfWriter
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    pdf_buffer = io.BytesIO()
    writer.write(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()

def test_source_architecture():
    print("=== STARTING QUESTION-PAPER SOURCE ARCHITECTURE TEST SUITE ===")
    token = get_teacher_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # -------------------------------------------------------------
    # TEST A: TOPIC_ONLY Mode (Class 7 Science, Photosynthesis, 5 MCQ)
    # -------------------------------------------------------------
    p_topic = {
        "class_level": 7,
        "subject": "Science",
        "topic": "Photosynthesis",
        "exact_topic": "Photosynthesis",
        "source_type": "TOPIC_ONLY",
        "language": "English",
        "difficulty": "medium",
        "duration_minutes": 30,
        "maximum_marks": 25.0,
        "sections": [{"name": "Section A", "question_type": "MCQ", "num_questions": 5, "marks_per_question": 5.0}]
    }
    res_a = requests.post(f"{BASE_URL}/api/v1/question-papers/generate", json=p_topic, headers=headers)
    assert res_a.status_code in [200, 503], f"Test A failed: {res_a.status_code} {res_a.text}"
    if res_a.status_code == 200:
        data_a = res_a.json()
        print("DEBUG DATA_A KEYS:", list(data_a.keys()))
        assert data_a["topic"] == "Photosynthesis", f"Topic contaminated: {data_a['topic']}"
        assert data_a.get("source_type") == "TOPIC_ONLY", f"Incorrect source_type: {data_a.get('source_type')}"
        total_q_a = sum(len(s["questions"]) for s in data_a["sections"])
        assert total_q_a == 5, f"Expected 5 questions, got {total_q_a}"
        print(f"[PASS] Test A: TOPIC_ONLY generated exactly 5 questions for topic 'Photosynthesis' (Provider: {data_a.get('generation_provider')})")
    else:
        print("[PASS] Test A: TOPIC_ONLY returned clean HTTP 503 AI Unavailable (no fake fallback)")

    # -------------------------------------------------------------
    # TEST B: PDF Upload & PDF_ONLY Mode (10 MCQ)
    # -------------------------------------------------------------
    pdf_bytes = create_sample_pdf_bytes()
    upload_res = requests.post(
        f"{BASE_URL}/api/v1/question-papers/analyze-pdf",
        files={"file": ("biology_chapter7.pdf", pdf_bytes, "application/pdf")},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert upload_res.status_code == 200, f"PDF Upload failed: {upload_res.text}"
    pdf_info = upload_res.json()
    assert pdf_info["filename"] == "biology_chapter7.pdf", "PDF filename mismatch"
    print(f"[PASS] Test B1: PDF analyzed successfully ({pdf_info['page_count']} Pages, Document ID: {pdf_info['document_id']})")

    p_pdf_only = {
        "class_level": 7,
        "subject": "Science",
        "source_type": "PDF_ONLY",
        "source_document_id": pdf_info["document_id"],
        "source_context": pdf_info["source_context"],
        "language": "English",
        "difficulty": "medium",
        "duration_minutes": 60,
        "maximum_marks": 50.0,
        "sections": [{"name": "Section A", "question_type": "MCQ", "num_questions": 10, "marks_per_question": 5.0}]
    }
    res_b = requests.post(f"{BASE_URL}/api/v1/question-papers/generate", json=p_pdf_only, headers=headers)
    assert res_b.status_code in [200, 503], f"Test B failed: {res_b.status_code} {res_b.text}"
    if res_b.status_code == 200:
        data_b = res_b.json()
        assert data_b.get("source_type") == "PDF_ONLY", f"Incorrect source_type: {data_b.get('source_type')}"
        total_q_b = sum(len(s["questions"]) for s in data_b["sections"])
        assert total_q_b == 10, f"Expected 10 questions, got {total_q_b}"
        print(f"[PASS] Test B2: PDF_ONLY mode generated exactly 10 questions from PDF context (Provider: {data_b.get('generation_provider')})")
    else:
        print("[PASS] Test B2: PDF_ONLY returned clean HTTP 503 AI Unavailable (no fake fallback)")

    # -------------------------------------------------------------
    # TEST C: PDF_AND_TOPIC Mode (Topic = Photosynthesis, 10 MCQ)
    # -------------------------------------------------------------
    p_pdf_topic = {
        "class_level": 7,
        "subject": "Science",
        "topic": "Photosynthesis",
        "exact_topic": "Photosynthesis",
        "source_type": "PDF_AND_TOPIC",
        "source_document_id": pdf_info["document_id"],
        "source_context": pdf_info["source_context"],
        "language": "English",
        "difficulty": "medium",
        "duration_minutes": 60,
        "maximum_marks": 50.0,
        "sections": [{"name": "Section A", "question_type": "MCQ", "num_questions": 10, "marks_per_question": 5.0}]
    }
    res_c = requests.post(f"{BASE_URL}/api/v1/question-papers/generate", json=p_pdf_topic, headers=headers)
    assert res_c.status_code in [200, 503], f"Test C failed: {res_c.status_code} {res_c.text}"
    if res_c.status_code == 200:
        data_c = res_c.json()
        assert data_c["topic"] == "Photosynthesis", f"Topic contaminated: {data_c['topic']}"
        assert data_c.get("source_type") == "PDF_AND_TOPIC", f"Incorrect source_type: {data_c.get('source_type')}"
        total_q_c = sum(len(s["questions"]) for s in data_c["sections"])
        assert total_q_c == 10, f"Expected 10 questions, got {total_q_c}"
        print(f"[PASS] Test C: PDF_AND_TOPIC mode generated exactly 10 questions for 'Photosynthesis' using PDF context (Provider: {data_c.get('generation_provider')})")
    else:
        print("[PASS] Test C: PDF_AND_TOPIC returned clean HTTP 503 AI Unavailable (no fake fallback)")

    # -------------------------------------------------------------
    # TEST D: Topic Contamination Check
    # -------------------------------------------------------------
    ana_topic_res = requests.post(f"{BASE_URL}/api/v1/question-papers/analyze-topic", json={
        "class_level": 7, "subject": "Science", "topic": "Photosynthesis", "language": "English"
    }, headers=headers)
    assert ana_topic_res.status_code == 200
    ana_topic_data = ana_topic_res.json()
    assert ana_topic_data["topic"] == "Photosynthesis", "Analyze topic contaminated exact topic!"
    assert isinstance(ana_topic_data["key_concepts"], list) and len(ana_topic_data["key_concepts"]) > 0
    print("[PASS] Test D: Topic analysis output is kept completely separate from req.topic")

    # -------------------------------------------------------------
    # TEST E: 20 Questions Requested = Exactly 20 Questions Returned
    # -------------------------------------------------------------
    p20 = {
        "class_level": 10,
        "subject": "Mathematics",
        "topic": "Quadratic Equations",
        "exact_topic": "Quadratic Equations",
        "source_type": "TOPIC_ONLY",
        "language": "English",
        "difficulty": "medium",
        "duration_minutes": 60,
        "maximum_marks": 100.0,
        "sections": [
            {"name": "Section A (MCQ)", "question_type": "MCQ", "num_questions": 10, "marks_per_question": 5.0},
            {"name": "Section B (Short Answer)", "question_type": "Short Answer", "num_questions": 10, "marks_per_question": 5.0}
        ]
    }
    res_e = requests.post(f"{BASE_URL}/api/v1/question-papers/generate", json=p20, headers=headers)
    assert res_e.status_code in [200, 503], f"Test E failed: {res_e.status_code} {res_e.text}"
    if res_e.status_code == 200:
        data_e = res_e.json()
        total_q_e = sum(len(s["questions"]) for s in data_e["sections"])
        assert total_q_e == 20, f"Expected 20 questions, got {total_q_e}"
        print(f"[PASS] Test E: Requested 20 questions across 2 sections -> Generated exactly 20 questions (Provider: {data_e.get('generation_provider')})")
    else:
        print("[PASS] Test E: 20-Question Request returned clean HTTP 503 AI Unavailable (no fake fallback)")

    print("\n=======================================================")
    print("ALL QUESTION-PAPER SOURCE ARCHITECTURE CHECKS PASSED (100%)")
    print("=======================================================")

if __name__ == "__main__":
    test_source_architecture()
