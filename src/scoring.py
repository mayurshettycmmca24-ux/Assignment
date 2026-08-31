import re

from .config import SETTINGS
from .models import CandidateProfile


def _normalize_text(value: str) -> str:
    return " ".join((value or "").lower().split())


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    lowered = _normalize_text(text)
    return any(term.lower() in lowered for term in terms)


def _contains_any_unnegated(text: str, terms: tuple[str, ...]) -> bool:
    lowered = _normalize_text(text)
    for term in terms:
        pattern = re.compile(rf"\b(?:no|not|without|never|none|did not|didn't|there was no|there were no|lacked|lacking)\b(?:\s+\w+){{0,6}}\s+{re.escape(term.lower())}\b")
        if pattern.search(lowered):
            continue
        if term.lower() in lowered:
            return True
    return False


def _score_category(name: str, points: int, max_points: int, reasoning: str) -> dict:
    return {"points": max(0, min(points, max_points)), "max_points": max_points, "reasoning": reasoning}


def score_candidate(candidate: CandidateProfile, eligibility: dict, github_signal: dict | None = None) -> dict:
    text = _normalize_text(" ".join([candidate.raw_text, " ".join(candidate.skills), " ".join(candidate.projects)]))
    skills = [s.lower() for s in candidate.skills]
    project_text = " ".join(candidate.projects).lower()

    score_breakdown: dict[str, dict] = {}

    ai_project_depth = 0
    ai_reasoning = []
    if _contains_any_unnegated(text, SETTINGS.AI_KEYWORDS):
        ai_project_depth += 10
        ai_reasoning.append("AI/LLM or agentic keywords found in resume text.")
    if _contains_any_unnegated(text, SETTINGS.AI_STRONG_SIGNALS):
        ai_project_depth += 18
        ai_reasoning.append("Strong AI system signals such as RAG, retrieval, orchestration, embeddings, or agent workflows were found.")
    if _contains_any_unnegated(text, ("agentic workflow", "langgraph", "workflow", "pipeline", "retrieval", "orchestration", "memory", "tool", "evaluation", "state", "multi-agent")):
        ai_project_depth += 8
        ai_reasoning.append("Project descriptions suggest workflow logic and product-level orchestration beyond a prompt wrapper.")
    if _contains_any_unnegated(text, ("stateful memory", "eval pipelines", "tool calling", "retrieval over embeddings", "business workflow state management")):
        ai_project_depth += 5
        ai_reasoning.append("The project demonstrates memory, state, evaluation, or retrieval patterns that indicate deeper AI system design.")
    if _contains_any(project_text, ("tutorial", "toy", "basic demo", "hello world")):
        ai_project_depth -= 10
        ai_reasoning.append("Project appears tutorial-style or demo-only, reducing AI depth score.")
    llm_api_call = _contains_any_unnegated(text, ("openai api", "anthropic api", "llm api", "chatgpt", "gpt api", "claude api"))
    real_system_signals = _contains_any_unnegated(text, ("retrieval", "embeddings", "vector search", "tool calling", "tool-calling", "multi-agent", "state management", "stateful memory", "workflow", "orchestration", "evaluation", "evals", "agentic", "rag", "vector database", "pipeline", "memory"))
    if llm_api_call and not real_system_signals:
        ai_project_depth -= 15
        ai_reasoning.append("Project appears to be a thin wrapper around an LLM API call with no meaningful workflow, retrieval, or evaluation logic, reducing AI depth score.")
    ai_project_depth = max(0, min(ai_project_depth, 40))
    score_breakdown["ai_project_depth"] = _score_category("ai_project_depth", ai_project_depth, 40, " | ".join(ai_reasoning) if ai_reasoning else "No strong AI project evidence found.")

    backend_points = 0
    backend_reasoning = []
    if "python" in text:
        backend_points += 12
        backend_reasoning.append("Python is present across skills or projects.")
    if any(term in text for term in ("fastapi", "django", "flask")):
        backend_points += 10
        backend_reasoning.append("Backend framework evidence supports Python engineering depth.")
    if any(term in text for term in ("postgresql", "redis", "sqlalchemy", "celery", "asyncio")):
        backend_points += 8
        backend_reasoning.append("Data or asynchronous backend infrastructure is mentioned.")
    if any(term in text for term in ("stateful memory", "tool calling", "eval pipeline", "workflow orchestration", "retrieval", "orchestration", "memory", "multi-agent", "state management")):
        backend_points += 5
        backend_reasoning.append("Workflow/state/evaluation-heavy backend logic indicates deeper software engineering beyond simple API usage.")
    backend_points = max(0, min(backend_points, 30))
    score_breakdown["python_backend_engineering"] = _score_category("python_backend_engineering", backend_points, 30, " | ".join(backend_reasoning) if backend_reasoning else "No meaningful backend evidence found.")

    cloud_points = 0
    cloud_reasoning = []
    if any(term in text for term in ("gcp", "google cloud", "aws", "azure", "docker", "kubernetes", "deployment")):
        cloud_points += 10
        cloud_reasoning.append("Cloud or deployment signals are present.")
    if any(term in text for term in ("react", "next.js", "nextjs", "javascript", "typescript")):
        cloud_points += 5
        cloud_reasoning.append("Frontend stack signals support the cloud/full-stack profile.")
    cloud_points = max(0, min(cloud_points, 15))
    score_breakdown["cloud_fullstack"] = _score_category("cloud_fullstack", cloud_points, 15, " | ".join(cloud_reasoning) if cloud_reasoning else "No strong cloud/full-stack deployment evidence found.")

    github_score = 0
    github_summary = "No GitHub enrichment available."
    if github_signal:
        github_score = int(github_signal.get("score", 0))
        github_summary = github_signal.get("summary", "GitHub analysis unavailable.")
    score_breakdown["github_activity"] = _score_category("github_activity", github_score, 10, github_summary)

    engineering_points = 0
    engineering_reasoning = []
    strong_software_signals = any(term in text for term in ("architecture", "system design", "scalable", "distributed", "state management", "workflow orchestration", "business workflow", "automation", "stateful memory", "eval pipeline", "tool calling", "multi-agent", "retrieval", "orchestration"))
    if any(term in text for term in ("testing", "pytest", "unit tests", "integration tests")):
        engineering_points += 2
        engineering_reasoning.append("Testing evidence is present.")
    if strong_software_signals:
        engineering_points += 2
        engineering_reasoning.append("Architecture or workflow orchestration signals are present.")
    if any(term in text for term in ("cache", "caching", "queue", "redis", "observability", "monitoring", "retry", "failure handling", "asyncio", "concurrency", "eval pipeline", "stateful memory", "tool calling", "multi-agent")):
        engineering_points += 1
        engineering_reasoning.append("Operational and reliability signals appear in the resume.")
    if strong_software_signals and any(term in text for term in ("redis", "postgresql", "fastapi", "langgraph", "rag", "retrieval")):
        engineering_points += 1
        engineering_reasoning.append("The project combines agentic workflow signals with backend infrastructure and production-grade components.")
    engineering_points = max(0, min(engineering_points, 5))
    score_breakdown["engineering_depth"] = _score_category("engineering_depth", engineering_points, 5, " | ".join(engineering_reasoning) if engineering_reasoning else "No explicit engineering depth signals found.")

    total_score = (
        score_breakdown["ai_project_depth"]["points"]
        + score_breakdown["python_backend_engineering"]["points"]
        + score_breakdown["cloud_fullstack"]["points"]
        + score_breakdown["github_activity"]["points"]
        + score_breakdown["engineering_depth"]["points"]
    )

    strengths = []
    concerns = []
    if ai_project_depth >= 25:
        strengths.append("Strong AI/project depth with meaningful workflow or retrieval signals.")
    else:
        concerns.append("AI project depth is limited or mostly a thin API wrapper.")
    if backend_points >= 20:
        strengths.append("Solid Python and backend engineering evidence.")
    else:
        concerns.append("Python/backend engineering evidence is light.")
    if github_score > 0:
        strengths.append("Public GitHub activity adds positive evidence.")
    else:
        concerns.append("GitHub signal is weak or unavailable.")

    return {
        "candidate_name": candidate.name,
        "eligible": bool(eligibility.get("eligible", False)),
        "total_score": int(total_score),
        "score_breakdown": score_breakdown,
        "matched_skills": eligibility.get("matched_skills", []),
        "project_summary": " ".join(candidate.projects)[:500] if candidate.projects else "No project details found.",
        "github_summary": github_summary,
        "strengths": strengths,
        "concerns": concerns,
        "rank": None,
        "rejection_reasons": eligibility.get("rejection_reasons", []),
    }
