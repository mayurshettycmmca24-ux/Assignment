import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()


class Settings:
    INPUT_DIR: str = os.getenv("RESUME_INPUT_DIR", "./resumes")
    OUTPUT_PATH: str = os.getenv("RESUME_OUTPUT_PATH", "./output/results.json")
    ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY")
    GITHUB_TOKEN: str | None = os.getenv("GITHUB_TOKEN")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    AI_KEYWORDS: tuple[str, ...] = (
        "langchain",
        "langgraph",
        "llamaindex",
        "rag",
        "retrieval",
        "retriever",
        "embeddings",
        "vector search",
        "agent",
        "agents",
        "multi-agent",
        "tool calling",
        "tool-calling",
        "orchestration",
        "state machine",
        "memory",
        "evaluation",
        "evals",
        "google adk",
        "adk",
        "openai",
        "anthropic",
        "llm",
        "large language model",
        "prompt engineering",
    )
    PYTHON_KEYWORDS: tuple[str, ...] = (
        "python",
        "fastapi",
        "django",
        "flask",
        "asyncio",
        "postgresql",
        "redis",
        "sqlalchemy",
        "celery",
        "pandas",
        "numpy",
        "pytorch",
        "tensorflow",
        "pytest",
        "gunicorn",
    )
    CLOUD_KEYWORDS: tuple[str, ...] = (
        "gcp",
        "google cloud",
        "docker",
        "kubernetes",
        "aws",
        "azure",
        "deployment",
        "cloudrun",
        "terraform",
        "helm",
    )
    FRONTEND_KEYWORDS: tuple[str, ...] = ("react", "next.js", "nextjs", "javascript", "typescript")
    ENGINEERING_DEPTH_KEYWORDS: tuple[str, ...] = (
        "testing",
        "pytest",
        "ci/cd",
        "cache",
        "caching",
        "queue",
        "redis",
        "observability",
        "monitoring",
        "concurrency",
        "asyncio",
        "retry",
        "failure handling",
        "logging",
        "architecture",
    )
    AI_STRONG_SIGNALS: tuple[str, ...] = (
        "langgraph",
        "rag",
        "retrieval",
        "embeddings",
        "vector search",
        "agentic",
        "tool calling",
        "multi-agent",
        "workflow orchestration",
        "eval pipeline",
        "memory",
        "state management",
        "search pipeline",
    )
    tutorial_signals: tuple[str, ...] = (
        "tutorial",
        "hello world",
        "basic demo",
        "course project",
        "toy project",
        "sample app",
    )


SETTINGS = Settings()


def env_or_default(name: str, default: Any = None) -> Any:
    return os.getenv(name, default)
