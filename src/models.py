from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CandidateProfile(BaseModel):
    name: str = "Unknown Candidate"
    email: str = ""
    skills: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    github_url: str = ""
    raw_text: str = ""


class CandidateEligibilityResult(BaseModel):
    eligible: bool = False
    rejection_reasons: list[str] = Field(default_factory=list)
    matched_skills: list[str] = Field(default_factory=list)
    python_evidence: bool = False
    ai_evidence: bool = False


class ScoreBreakdownCategory(BaseModel):
    points: int = 0
    max_points: int = 0
    reasoning: str = ""


class CandidateScoreResult(BaseModel):
    candidate_name: str
    eligible: bool
    total_score: int = 0
    score_breakdown: dict[str, dict[str, Any]] = Field(default_factory=dict)
    matched_skills: list[str] = Field(default_factory=list)
    project_summary: str = ""
    github_summary: str = ""
    strengths: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    rank: int | None = None
    rejection_reasons: list[str] = Field(default_factory=list)


class GitHubSignal(BaseModel):
    username: str = ""
    status: str = "missing"
    score: int = 0
    summary: str = ""
    repo_count: int = 0
    relevant_repo_count: int = 0
    recent_activity: list[str] = Field(default_factory=list)
    repos: list[str] = Field(default_factory=list)


class LLMExtractionResult(BaseModel):
    skills: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    summary: str = ""


class ProjectDepthJudgment(BaseModel):
    score: int = 0
    reasoning: str = ""
    is_thin_wrapper: bool = False
