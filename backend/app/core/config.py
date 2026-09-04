import os
from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Multi-Agent Exam & Evaluation Portal"
    API_V1_STR: str = "/api/v1"

    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # ============================================================
    # Database
    # ============================================================

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgrespassword@localhost:5432/exam_portal_db",
    )

    # ============================================================
    # Redis / Celery
    # ============================================================

    REDIS_BROKER_URL: str = os.getenv(
        "REDIS_BROKER_URL",
        os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    )

    REDIS_RESULT_BACKEND: str = os.getenv(
        "REDIS_RESULT_BACKEND",
        "redis://localhost:6379/1",
    )

    REDIS_URL: str = os.getenv(
        "REDIS_URL",
        os.getenv("REDIS_BROKER_URL", "redis://localhost:6379/0"),
    )

    # ============================================================
    # Authentication
    # ============================================================

    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        os.getenv(
            "JWT_SECRET",
            "dev_secret_key_change_in_production_2026",
        ),
    )

    JWT_SECRET: str = os.getenv(
        "JWT_SECRET",
        os.getenv(
            "JWT_SECRET_KEY",
            "dev_secret_key_change_in_production_2026",
        ),
    )

    JWT_ALGORITHM: str = os.getenv(
        "JWT_ALGORITHM",
        "HS256",
    )

    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv(
            "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
            "1440",
        )
    )

    # ============================================================
    # Docker Sandbox
    # ============================================================

    SANDBOX_IMAGE: str = os.getenv(
        "SANDBOX_IMAGE",
        "multi-agent-exam-portal-sandbox:latest",
    )

    SANDBOX_MEM_LIMIT: str = os.getenv(
        "SANDBOX_MEM_LIMIT",
        "128m",
    )

    SANDBOX_MAX_MEMORY_MB: int = 128

    SANDBOX_CPU_NANOS: int = int(
        os.getenv(
            "SANDBOX_CPU_NANOS",
            "500000000",
        )
    )

    SANDBOX_CPU_QUOTA: float = float(
        os.getenv(
            "SANDBOX_CPU_QUOTA",
            "0.5",
        )
    )

    SANDBOX_TIMEOUT_SECONDS: int = int(
        os.getenv(
            "SANDBOX_TIMEOUT_SECONDS",
            "2",
        )
    )

    # ============================================================
    # CORS / WebSocket
    # ============================================================

    CORS_ORIGINS: Union[List[str], str] = os.getenv(
        "CORS_ORIGINS",
        "*",
    )

    WEBSOCKET_MAX_CONNECTIONS: int = int(
        os.getenv(
            "WEBSOCKET_MAX_CONNECTIONS",
            "1000",
        )
    )

    WEBSOCKET_IDLE_TIMEOUT_SECONDS: int = int(
        os.getenv(
            "WEBSOCKET_IDLE_TIMEOUT_SECONDS",
            "300",
        )
    )

    MAX_WEBSOCKET_MESSAGE_BYTES: int = int(
        os.getenv(
            "MAX_WEBSOCKET_MESSAGE_BYTES",
            "65536",
        )
    )

    # ============================================================
    # AI Provider
    # ============================================================

    # Supported values:
    # deterministic
    # gemini
    # bedrock
    # llm

    AI_PROVIDER: str = os.getenv(
        "AI_PROVIDER",
        "gemini",
    )

    # ============================================================
    # Google Gemini
    # ============================================================

    GEMINI_API_KEY: str = os.getenv(
        "GEMINI_API_KEY",
        "",
    )

    GEMINI_MODEL: str = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.6-flash",
    )

    MAX_GENERATED_QUESTIONS: int = int(
        os.getenv(
            "MAX_GENERATED_QUESTIONS",
            "100",
        )
    )

    # ============================================================
    # Existing LLM Compatibility
    # ============================================================

    LLM_API_KEY: str = os.getenv(
        "LLM_API_KEY",
        "",
    )

    LLM_MODEL: str = os.getenv(
        "LLM_MODEL",
        "gemini-1.5-pro",
    )

    # ============================================================
    # AWS / Amazon Bedrock
    # ============================================================

    AWS_REGION: str = os.getenv(
        "AWS_REGION",
        "us-east-1",
    )

    BEDROCK_MODEL_ID: str = os.getenv(
        "BEDROCK_MODEL_ID",
        "us.amazon.nova-2-lite-v1:0",
    )

    # ============================================================
    # A2A Consensus
    # ============================================================

    MAX_A2A_ROUNDS: int = int(
        os.getenv(
            "MAX_A2A_ROUNDS",
            "3",
        )
    )

    # ============================================================
    # Telemetry / Payload Limits
    # ============================================================

    MAX_SOURCE_CODE_BYTES: int = int(
        os.getenv(
            "MAX_SOURCE_CODE_BYTES",
            "100000",
        )
    )

    MAX_OUTPUT_BYTES: int = int(
        os.getenv(
            "MAX_OUTPUT_BYTES",
            "65536",
        )
    )

    MAX_TELEMETRY_EVENTS: int = int(
        os.getenv(
            "MAX_TELEMETRY_EVENTS",
            "1000",
        )
    )

    ANOMALY_UPDATE_INTERVAL_SECONDS: int = int(
        os.getenv(
            "ANOMALY_UPDATE_INTERVAL_SECONDS",
            "5",
        )
    )

    # ============================================================
    # Validators
    # ============================================================

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(
        cls,
        v: Union[str, List[str]],
    ) -> List[str]:
        if isinstance(v, str):
            if v.strip() == "*":
                return ["*"]

            return [
                origin.strip()
                for origin in v.split(",")
                if origin.strip()
            ]

        return v

    class Config:
        case_sensitive = True


settings = Settings()