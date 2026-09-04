import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import redis

from app.core.config import settings
from app.database.session import engine, Base, check_database_connection
from app.api import auth, exams, questions, attempts, submissions, websockets, telemetry, live, organizations, reviews, plagiarism, audit, analytics, question_papers

from app.observability.metrics import metrics_collector

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("multi_agent_exam_portal")

from sqlalchemy import text

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler initializing database tables on gateway startup."""
    logger.info("Initializing PostgreSQL Database Schema via SQLAlchemy Metadata...")
    try:
        Base.metadata.create_all(bind=engine)
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE dim_users ADD COLUMN IF NOT EXISTS class_level INTEGER;"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_dim_users_class_level ON dim_users(class_level);"))
            conn.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_constraint
                        WHERE conname = 'ck_dim_users_class_level_range'
                    ) THEN
                        ALTER TABLE dim_users
                        ADD CONSTRAINT ck_dim_users_class_level_range
                        CHECK (class_level IS NULL OR class_level BETWEEN 1 AND 12);
                    END IF;
                END $$;
            """))
            conn.execute(text("ALTER TABLE dim_exams ADD COLUMN IF NOT EXISTS class_level INTEGER DEFAULT 10;"))
            conn.execute(text("ALTER TABLE dim_exams ADD COLUMN IF NOT EXISTS subject VARCHAR(100) DEFAULT 'Mathematics';"))
            conn.execute(text("ALTER TABLE dim_exams ADD COLUMN IF NOT EXISTS language VARCHAR(50) DEFAULT 'English';"))
            conn.execute(text("ALTER TABLE dim_question_papers ADD COLUMN IF NOT EXISTS language VARCHAR(50) DEFAULT 'English';"))
            conn.execute(text("ALTER TABLE dim_question_papers ADD COLUMN IF NOT EXISTS generation_provider VARCHAR(50) DEFAULT 'DETERMINISTIC_FALLBACK';"))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS fact_exam_assignments (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    exam_id UUID NOT NULL REFERENCES dim_exams(id) ON DELETE CASCADE,
                    class_level INTEGER NOT NULL,
                    assigned_by UUID REFERENCES dim_users(id) ON DELETE SET NULL,
                    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_fact_exam_assignments_exam_class ON fact_exam_assignments(exam_id, class_level, status);"))
            conn.execute(text("""
                UPDATE dim_exams 
                SET class_level = qp.class_level, subject = qp.subject, language = qp.language
                FROM dim_question_papers qp
                WHERE dim_exams.id = qp.published_exam_id;
            """))
        logger.info("Database Star Schema initialization and class_level columns verified.")
    except Exception as err:
        logger.warning(f"Database table initialization notice: {err}")
    yield
    logger.info("Shutting down Multi-Agent Exam Gateway service...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description=(
        "Production-grade Multi-Agent Exam & Evaluation Portal API Gateway (Phase 11). "
        "Integrates Real-Time WebSockets, Redis Event Bus, Advanced Analytics, Enterprise "
        "Identity, SCIM Provisioning, Signed Webhooks, Plagiarism Engine, and Developer APIs."
    ),
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Security Headers & Metrics Middleware
@app.middleware("http")
async def add_security_headers_and_metrics(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    metrics_collector.record_request(response.status_code)
    return response

# Configure Cross-Origin Resource Sharing (CORS)
cors_origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global Unhandled Exception at {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error": str(exc)}
    )

# Include API V1 Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(exams.router, prefix=settings.API_V1_STR)
app.include_router(questions.router, prefix=settings.API_V1_STR)
app.include_router(attempts.router, prefix=settings.API_V1_STR)
app.include_router(submissions.router, prefix=settings.API_V1_STR)
app.include_router(websockets.router, prefix=settings.API_V1_STR)
app.include_router(telemetry.router, prefix=settings.API_V1_STR)
app.include_router(live.router, prefix=settings.API_V1_STR)
app.include_router(organizations.router, prefix=settings.API_V1_STR)
app.include_router(reviews.router, prefix=settings.API_V1_STR)
app.include_router(plagiarism.router, prefix=settings.API_V1_STR)
app.include_router(audit.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)
app.include_router(question_papers.router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health & Readiness"])
def health_check():
    """Liveness probe returning simple health status."""
    return {"status": "healthy"}

@app.get("/ready", tags=["Health & Readiness"])
def readiness_check():
    """Readiness probe verifying PostgreSQL and Redis connections."""
    db_healthy = check_database_connection()
    redis_healthy = False
    
    try:
        r = redis.Redis.from_url(settings.REDIS_BROKER_URL, socket_timeout=2)
        redis_healthy = r.ping()
    except Exception as re:
        logger.warning(f"Redis readiness check failed: {re}")

    overall_ready = db_healthy and redis_healthy
    status_code = 200 if overall_ready else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if overall_ready else "degraded",
            "database": "connected" if db_healthy else "disconnected",
            "redis": "connected" if redis_healthy else "disconnected"
        }
    )

@app.get("/metrics", tags=["Health & Readiness"])
def get_operational_metrics():
    """Returns operational health metrics for monitoring dashboards."""
    return metrics_collector.get_summary()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
