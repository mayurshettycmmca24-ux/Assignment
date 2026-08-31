import re

from .config import SETTINGS
from .models import CandidateEligibilityResult, CandidateProfile


def _normalize_text(value: str) -> str:
    return " ".join((value or "").lower().split())


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    lowered = _normalize_text(text)
    return any(term.lower() in lowered for term in terms)


def _collect_matched_skills(candidate: CandidateProfile) -> list[str]:
    text = _normalize_text(candidate.raw_text + " " + " ".join(candidate.skills) + " " + " ".join(candidate.projects))
    matched: list[str] = []
    for skill in sorted(set(candidate.skills + [s.strip() for s in candidate.skills]), key=lambda x: x.lower()):
        if not skill:
            continue
        normalized_skill = skill.lower()
        if normalized_skill in text:
            matched.append(skill)
    if not matched:
        for term in SETTINGS.PYTHON_KEYWORDS + SETTINGS.AI_KEYWORDS + SETTINGS.CLOUD_KEYWORDS + SETTINGS.FRONTEND_KEYWORDS:
            if term.lower() in text:
                matched.append(term)
    return sorted(set(matched), key=lambda x: x.lower())


def evaluate_eligibility(candidate: CandidateProfile) -> dict:
    raw_text = _normalize_text(candidate.raw_text)
    skills_text = _normalize_text(" ".join(candidate.skills))
    project_text = _normalize_text(" ".join(candidate.projects))
    full_text = raw_text + " " + skills_text + " " + project_text

    python_evidence = _contains_any(full_text, SETTINGS.PYTHON_KEYWORDS)
    ai_evidence = _contains_any(full_text, SETTINGS.AI_KEYWORDS)

    if not python_evidence:
        python_reason = "Python evidence missing"
    else:
        python_reason = ""
    if not ai_evidence:
        ai_reason = "AI/agentic evidence missing"
    else:
        ai_reason = ""

    reason_list = [reason for reason in [python_reason, ai_reason] if reason]
    eligible = python_evidence and ai_evidence

    matched_skills = _collect_matched_skills(candidate)
    return CandidateEligibilityResult(
        eligible=eligible,
        rejection_reasons=reason_list,
        matched_skills=matched_skills,
        python_evidence=python_evidence,
        ai_evidence=ai_evidence,
    ).model_dump()
