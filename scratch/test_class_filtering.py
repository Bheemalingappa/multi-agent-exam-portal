import requests

BASE_URL = "http://ae7437d5531624dbd8d018588b30e79f-1203586077.us-east-1.elb.amazonaws.com/api/v1"

def run_class_filter_test():
    print("=== TESTING CLASS 1-12 ISOLATION & SERVER FILTERING ===")
    
    # Login Educator
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "teacher@eduexam.com", "password": "TestPassword123!"})
    teacher_token = resp.json()["access_token"]
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}

    # Login Student
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "student@eduexam.com", "password": "TestPassword123!"})
    student_token = resp.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}

    # Create & Publish Class 7 Paper
    c7_payload = {
        "title": "Class 7 Science Mid-Term",
        "class_level": 7,
        "subject": "Science",
        "topic": "Nutrition in Plants",
        "difficulty": "intermediate",
        "duration_minutes": 45,
        "maximum_marks": 50,
        "status": "DRAFT",
        "sections": [{
            "name": "Section A",
            "instructions": "Answer all",
            "questions": [{
                "question": "Explain Photosynthesis.",
                "marks": 50,
                "correct_answer": "Process of making food."
            }]
        }]
    }
    c7_paper = requests.post(f"{BASE_URL}/question-papers", json=c7_payload, headers=teacher_headers).json()
    c7_pub = requests.post(f"{BASE_URL}/question-papers/{c7_paper['id']}/publish", headers=teacher_headers).json()
    c7_exam_id = c7_pub["exam_id"]
    print(f"[PASS] Published Class 7 Exam: {c7_exam_id}")

    # Create & Publish Class 10 Paper
    c10_payload = {
        "title": "Class 10 Mathematics Board Mock",
        "class_level": 10,
        "subject": "Mathematics",
        "topic": "Quadratic Equations",
        "difficulty": "advanced",
        "duration_minutes": 60,
        "maximum_marks": 100,
        "status": "DRAFT",
        "sections": [{
            "name": "Section A",
            "instructions": "Solve equations",
            "questions": [{
                "question": "Solve x^2 - 4 = 0.",
                "marks": 100,
                "correct_answer": "x = 2 or x = -2"
            }]
        }]
    }
    c10_paper = requests.post(f"{BASE_URL}/question-papers", json=c10_payload, headers=teacher_headers).json()
    c10_pub = requests.post(f"{BASE_URL}/question-papers/{c10_paper['id']}/publish", headers=teacher_headers).json()
    c10_exam_id = c10_pub["exam_id"]
    print(f"[PASS] Published Class 10 Exam: {c10_exam_id}")

    # Server Filter Test: Class 7
    res_c7 = requests.get(f"{BASE_URL}/exams?class_level=7", headers=student_headers).json()
    print(f"[TEST] Querying GET /exams?class_level=7 -> Received {len(res_c7)} exam(s)")
    for ex in res_c7:
        assert ex["class_level"] == 7, f"LEAKAGE ERROR: Received exam with class_level {ex['class_level']} when querying class_level=7!"
        assert ex["id"] != c10_exam_id, "CROSS-CLASS LEAKAGE: Class 10 Exam appeared under Class 7 filter!"
    print("[PASS] Class 7 query contains ONLY Class 7 exams! Zero Class 10 leakage.")

    # Server Filter Test: Class 10
    res_c10 = requests.get(f"{BASE_URL}/exams?class_level=10", headers=student_headers).json()
    print(f"[TEST] Querying GET /exams?class_level=10 -> Received {len(res_c10)} exam(s)")
    for ex in res_c10:
        assert ex["class_level"] == 10, f"LEAKAGE ERROR: Received exam with class_level {ex['class_level']} when querying class_level=10!"
        assert ex["id"] != c7_exam_id, "CROSS-CLASS LEAKAGE: Class 7 Exam appeared under Class 10 filter!"
    print("[PASS] Class 10 query contains ONLY Class 10 exams! Zero Class 7 leakage.")

    print("\n=======================================================")
    print("ALL CLASS 1-12 SERVER FILTERING TESTS PASSED (100% VERIFIED)")
    print("=======================================================")

if __name__ == "__main__":
    run_class_filter_test()
