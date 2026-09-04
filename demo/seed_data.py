import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

import uuid
from datetime import datetime

try:
    from app.database.session import SessionLocal, engine, Base
    from app.database.models import User, Exam, Question, TestCase, SandboxProfile, Organization
    from app.core.security import get_password_hash
    HAS_DEPS = True
except (ImportError, ModuleNotFoundError):
    HAS_DEPS = False

def seed_demo_environment():
    print("--- Seeding Multi-Agent Exam Portal Demo Environment ---")
    if not HAS_DEPS:
        print("[NOTICE] Full JWT/passlib dependencies active inside backend container environment.")
        return

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        profile = db.query(SandboxProfile).filter(SandboxProfile.name == "Python Standard").first()
        if not profile:
            profile = SandboxProfile(
                name="Python Standard",
                memory_limit_mb=128,
                cpu_limit=0.5,
                timeout_seconds=2
            )
            db.add(profile)

        org = db.query(Organization).filter(Organization.slug == "acme-corp").first()
        if not org:
            org = Organization(name="Acme Corp", slug="acme-corp", max_candidates=500)
            db.add(org)

        recruiter = db.query(User).filter(User.email == "recruiter@acme.com").first()
        if not recruiter:
            recruiter = User(
                email="recruiter@acme.com",
                password_hash=get_password_hash("Recruiter123!"),
                role="recruiter"
            )
            db.add(recruiter)

        candidate = db.query(User).filter(User.email == "candidate@example.com").first()
        if not candidate:
            candidate = User(
                email="candidate@example.com",
                password_hash=get_password_hash("Candidate123!"),
                role="candidate"
            )
            db.add(candidate)

        db.commit()
        print("[PASS] Demo environment seeded cleanly!")
    except Exception as err:
        print(f"Notice during seeding: {err}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_demo_environment()
