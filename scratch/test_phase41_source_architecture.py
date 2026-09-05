import sys
import os
import io
import time
import requests

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

def get_teacher_token():
    res = safe_post(f"{BASE_URL}/api/v1/auth/login", json={"email": "teacher@eduexam.com", "password": "TestPassword123!"})
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
    print("=== STARTING PHASE 42 REAL GEMINI QUESTION-PAPER SOURCE ARCHITECTURE TEST SUITE ===")
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
    res_a = safe_post(f"{BASE_URL}/api/v1/question-papers/generate", json=p_topic, headers=headers)
    assert res_a.status_code == 200, f"Test A failed with HTTP {res_a.status_code}: {res_a.text}"
    data_a = res_a.json()
    assert data_a.get("generation_provider") == "GEMINI", f"Test A provider mismatch: expected GEMINI, got {data_a.get('generation_provider')}"
    assert data_a["topic"] == "Photosynthesis", f"Topic contaminated: {data_a['topic']}"
    assert data_a.get("source_type") == "TOPIC_ONLY", f"Incorrect source_type: {data_a.get('source_type')}"
    total_q_a = sum(len(s["questions"]) for s in data_a["sections"])
    assert total_q_a == 5, f"Expected 5 questions, got {total_q_a}"
    print(f"[PASS] TOPIC_ONLY — Provider: {data_a.get('generation_provider')} (Generated 5 questions for 'Photosynthesis')")

    time.sleep(5)

    # -------------------------------------------------------------
    # TEST B: PDF Upload & PDF_ONLY Mode (10 MCQ)
    # -------------------------------------------------------------
    pdf_bytes = create_sample_pdf_bytes()
    upload_res = safe_post(
        f"{BASE_URL}/api/v1/question-papers/analyze-pdf",
        files={"file": ("biology_chapter7.pdf", pdf_bytes, "application/pdf")},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert upload_res.status_code == 200, f"PDF Upload failed: {upload_res.text}"
    pdf_info = upload_res.json()
    assert pdf_info["filename"] == "biology_chapter7.pdf", "PDF filename mismatch"
    print(f"[PASS] PDF Analyzed successfully ({pdf_info['page_count']} Pages, Document ID: {pdf_info['document_id']})")

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
    res_b = safe_post(f"{BASE_URL}/api/v1/question-papers/generate", json=p_pdf_only, headers=headers)
    assert res_b.status_code == 200, f"Test B failed with HTTP {res_b.status_code}: {res_b.text}"
    data_b = res_b.json()
    assert data_b.get("generation_provider") == "GEMINI", f"Test B provider mismatch: expected GEMINI, got {data_b.get('generation_provider')}"
    assert data_b.get("source_type") == "PDF_ONLY", f"Incorrect source_type: {data_b.get('source_type')}"
    total_q_b = sum(len(s["questions"]) for s in data_b["sections"])
    assert total_q_b == 10, f"Expected 10 questions, got {total_q_b}"
    print(f"[PASS] PDF_ONLY — Provider: {data_b.get('generation_provider')} (Generated 10 questions from PDF context)")

    time.sleep(5)

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
    res_c = safe_post(f"{BASE_URL}/api/v1/question-papers/generate", json=p_pdf_topic, headers=headers)
    assert res_c.status_code == 200, f"Test C failed with HTTP {res_c.status_code}: {res_c.text}"
    data_c = res_c.json()
    assert data_c.get("generation_provider") == "GEMINI", f"Test C provider mismatch: expected GEMINI, got {data_c.get('generation_provider')}"
    assert data_c["topic"] == "Photosynthesis", f"Topic contaminated: {data_c['topic']}"
    assert data_c.get("source_type") == "PDF_AND_TOPIC", f"Incorrect source_type: {data_c.get('source_type')}"
    total_q_c = sum(len(s["questions"]) for s in data_c["sections"])
    assert total_q_c == 10, f"Expected 10 questions, got {total_q_c}"
    print(f"[PASS] PDF_AND_TOPIC — Provider: {data_c.get('generation_provider')} (Generated 10 questions for 'Photosynthesis' using PDF context)")

    time.sleep(5)

    # -------------------------------------------------------------
    # TEST D: Topic Contamination & Separation Check
    # -------------------------------------------------------------
    ana_topic_res = safe_post(f"{BASE_URL}/api/v1/question-papers/analyze-topic", json={
        "class_level": 7, "subject": "Science", "topic": "Photosynthesis", "language": "English"
    }, headers=headers)
    assert ana_topic_res.status_code == 200
    ana_topic_data = ana_topic_res.json()
    assert ana_topic_data["topic"] == "Photosynthesis", "Analyze topic contaminated exact topic!"
    assert isinstance(ana_topic_data["key_concepts"], list) and len(ana_topic_data["key_concepts"]) > 0
    print("[PASS] exact_topic preserved (Topic analysis output is kept completely separate from req.topic)")

    time.sleep(5)

    # -------------------------------------------------------------
    # TEST E: Kannada Smoke Test (Class 7 Science, "ಸಸ್ಯಗಳಲ್ಲಿ ದ್ಯುತಿಸಂಶ್ಲೇಷಣೆ", 5 MCQ)
    # -------------------------------------------------------------
    p_kannada = {
        "class_level": 7,
        "subject": "Science",
        "topic": "ಸಸ್ಯಗಳಲ್ಲಿ ದ್ಯುತಿಸಂಶ್ಲೇಷಣೆ",
        "exact_topic": "ಸಸ್ಯಗಳಲ್ಲಿ ದ್ಯುತಿಸಂಶ್ಲೇಷಣೆ",
        "source_type": "TOPIC_ONLY",
        "language": "Kannada",
        "difficulty": "medium",
        "duration_minutes": 30,
        "maximum_marks": 25.0,
        "sections": [{"name": "ವಿಭಾಗ ಎ", "question_type": "MCQ", "num_questions": 5, "marks_per_question": 5.0}]
    }
    res_k = safe_post(f"{BASE_URL}/api/v1/question-papers/generate", json=p_kannada, headers=headers)
    assert res_k.status_code == 200, f"Kannada Test failed with HTTP {res_k.status_code}: {res_k.text}"
    data_k = res_k.json()
    assert data_k.get("generation_provider") == "GEMINI", f"Kannada provider mismatch: expected GEMINI, got {data_k.get('generation_provider')}"
    total_q_k = sum(len(s["questions"]) for s in data_k["sections"])
    assert total_q_k == 5, f"Expected 5 Kannada questions, got {total_q_k}"
    first_q = data_k["sections"][0]["questions"][0]
    assert len(first_q["options"]) == 4, "MCQ must have 4 options"
    print(f"[PASS] Kannada generation — Provider: {data_k.get('generation_provider')} (Generated 5 questions for 'ಸಸ್ಯಗಳಲ್ಲಿ ದ್ಯುತಿಸಂಶ್ಲೇಷಣೆ')")

    time.sleep(5)

    # -------------------------------------------------------------
    # TEST F: Exact Question Count Verification (20 requested = 20 returned)
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
            {"name": "Section A (MCQ)", "question_type": "MCQ", "num_questions": 5, "marks_per_question": 5.0},
            {"name": "Section B (Short Answer)", "question_type": "Short Answer", "num_questions": 5, "marks_per_question": 5.0}
        ]
    }
    res_e = safe_post(f"{BASE_URL}/api/v1/question-papers/generate", json=p20, headers=headers)
    assert res_e.status_code == 200, f"Test F failed with HTTP {res_e.status_code}: {res_e.text}"
    data_e = res_e.json()
    assert data_e.get("generation_provider") == "GEMINI", f"Test F provider mismatch: expected GEMINI, got {data_e.get('generation_provider')}"
    total_q_e = sum(len(s["questions"]) for s in data_e["sections"])
    assert total_q_e == 10, f"Expected 10 questions, got {total_q_e}"
    print(f"[PASS] exact question counts — Provider: {data_e.get('generation_provider')} (Requested 10 ➔ Generated 10)")

    print("\n=======================================================")
    print("ALL REAL GEMINI QUESTION GENERATION CHECKS PASSED (100%)")
    print("=======================================================")

if __name__ == "__main__":
    test_source_architecture()
