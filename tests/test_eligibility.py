from src.models import CandidateProfile
from src.eligibility import evaluate_eligibility


def make_candidate(skills=None, projects=None, raw_text=None):
    return CandidateProfile(
        name="Test Candidate",
        email="test@example.com",
        skills=skills or [],
        projects=projects or [],
        github_url="",
        raw_text=raw_text or " ",
    )


def test_python_only_no_ai_rejected():
    candidate = make_candidate(
        skills=["Python", "FastAPI", "PostgreSQL"],
        projects=["Built a Python API with FastAPI and SQLAlchemy"],
        raw_text="I worked on Python backend services and APIs.",
    )

    result = evaluate_eligibility(candidate)
    assert result["eligible"] is False
    assert "Python evidence missing" not in result["rejection_reasons"]
    assert "AI/agentic evidence missing" in result["rejection_reasons"]


def test_ai_only_no_python_rejected():
    candidate = make_candidate(
        skills=["LangChain", "RAG", "OpenAI", "vector search"],
        projects=["Built a RAG assistant using embeddings and retrieval"],
        raw_text="Designed a LangChain agent with retrieval, prompt engineering, and embeddings.",
    )

    result = evaluate_eligibility(candidate)
    assert result["eligible"] is False
    assert "Python evidence missing" in result["rejection_reasons"]
    assert "AI/agentic evidence missing" not in result["rejection_reasons"]


def test_python_and_ai_present_is_eligible():
    candidate = make_candidate(
        skills=["Python", "LangChain", "RAG", "FastAPI"],
        projects=["Built a Python RAG pipeline with retrieval, embeddings, and agent orchestration"],
        raw_text="Python engineer building LangChain-based retrieval systems and agents.",
    )

    result = evaluate_eligibility(candidate)
    assert result["eligible"] is True
    assert result["matched_skills"]


def test_js_plus_python_ai_is_eligible_not_penalized_for_js():
    candidate = make_candidate(
        skills=["JavaScript", "React", "Python", "LangGraph", "FastAPI"],
        projects=["Implemented a Python agentic workflow with LangGraph and a React dashboard"],
        raw_text="Built Python backend and LangGraph orchestration; React frontend used for admin dashboard.",
    )

    result = evaluate_eligibility(candidate)
    assert result["eligible"] is True
    assert "JavaScript" not in result["rejection_reasons"]
