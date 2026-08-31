from src.models import CandidateProfile
from src.scoring import score_candidate


def make_candidate(skills=None, projects=None, raw_text=None):
    return CandidateProfile(
        name="Test Candidate",
        email="test@example.com",
        skills=skills or [],
        projects=projects or [],
        github_url="",
        raw_text=raw_text or " ",
    )


def test_thin_llm_wrapper_project_gets_penalty():
    candidate = make_candidate(
        skills=["Python", "OpenAI", "FastAPI"],
        projects=[
            "Built a simple Flask app calling OpenAI API to generate text for users."
        ],
        raw_text="Created a thin wrapper around GPT API with basic endpoints and prompt templates.",
    )

    result = score_candidate(candidate, eligibility={"eligible": True}, github_signal=None)
    assert result["total_score"] < 60
    assert result["score_breakdown"]["ai_project_depth"]["points"] <= 20
    assert "Project appears to be a thin wrapper around an LLM API call with no meaningful workflow, retrieval, or evaluation logic, reducing AI depth score." in result["score_breakdown"]["ai_project_depth"]["reasoning"]


def test_negated_retrieval_phrases_do_not_count_as_real_system_signal():
    candidate = make_candidate(
        skills=["Python", "OpenAI", "FastAPI", "Flask", "PostgreSQL"],
        projects=[
            "Built a chatbot using the OpenAI API to answer user questions about company policies and product FAQs. The app exposed a REST API and used prompt templates.",
            "Created a small admin interface to track conversation logs and prompt usage, with basic session bookkeeping in PostgreSQL. There was no retrieval system or workflow orchestration beyond passing the request to the model.",
        ],
        raw_text="Built a chatbot using the OpenAI API to answer user questions about company policies and product FAQs. The app exposed a REST API and used prompt templates. There was no retrieval system or workflow orchestration beyond passing the request to the model.",
    )

    result = score_candidate(candidate, eligibility={"eligible": True}, github_signal=None)
    assert result["score_breakdown"]["ai_project_depth"]["points"] <= 20
    assert "Project appears to be a thin wrapper around an LLM API call with no meaningful workflow, retrieval, or evaluation logic, reducing AI depth score." in result["score_breakdown"]["ai_project_depth"]["reasoning"]


def test_strong_agentic_project_scores_high_in_ai_category():
    candidate = make_candidate(
        skills=["Python", "LangGraph", "RAG", "FastAPI", "PostgreSQL", "Redis"],
        projects=[
            "Designed an agentic workflow using LangGraph, retrieval over embeddings, tool calling, stateful memory, and eval pipelines for customer support automation."
        ],
        raw_text="Built a multi-step AI assistant with retrieval, orchestration, tool calling, and business workflow state management.",
    )

    result = score_candidate(candidate, eligibility={"eligible": True}, github_signal=None)
    assert result["score_breakdown"]["ai_project_depth"]["points"] >= 25
    assert result["total_score"] >= 70


def test_github_enrichment_failure_does_not_crash_scoring():
    candidate = make_candidate(
        skills=["Python", "LangChain", "FastAPI"],
        projects=["Built a Python RAG workflow with retrieval and orchestration."],
        raw_text="Worked on an AI retrieval and orchestration system for enterprise use cases.",
    )

    result = score_candidate(candidate, eligibility={"eligible": True}, github_signal={"score": 0, "status": "failed", "summary": "GitHub unavailable"})
    assert result["total_score"] >= 0
    assert result["score_breakdown"]["github_activity"]["points"] == 0
