import os
from typing import Any

from anthropic import Anthropic
from pydantic import BaseModel

from .config import SETTINGS
from .models import LLMExtractionResult, ProjectDepthJudgment


class LLMAdapter:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or SETTINGS.ANTHROPIC_API_KEY
        self.model = model or SETTINGS.ANTHROPIC_MODEL
        self.client = Anthropic(api_key=self.api_key) if self.api_key else None

    def _call(self, system_prompt: str, user_prompt: str, response_model: type[BaseModel]) -> BaseModel | None:
        if not self.client:
            return None
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=400,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            content = response.content[0].text if response.content else "{}"
            return response_model.model_validate_json(content)
        except Exception:
            return None

    def extract_resume_fields(self, raw_text: str) -> dict[str, Any]:
        if not raw_text.strip():
            return {"skills": [], "projects": [], "summary": "No content available."}
        prompt = (
            "Extract the candidate's important skills and project descriptions from the resume text. "
            "Return a JSON object with keys: skills (list of strings), projects (list of strings), summary (short narrative). "
            "Use short evidence-based phrases only."
        )
        result = self._call(
            system_prompt="You are a precise resume parser. Output valid JSON matching the requested schema.",
            user_prompt=raw_text[:12000],
            response_model=LLMExtractionResult,
        )
        if result is None:
            return {"skills": [], "projects": [], "summary": "LLM extraction unavailable."}
        return result.model_dump()

    def judge_project_depth(self, project_text: str) -> dict[str, Any]:
        prompt = (
            "Assess if this project is a thin LLM wrapper or a meaningful AI workflow. "
            "Return JSON with keys: score (0-40), reasoning (short evidence), is_thin_wrapper (bool). "
            "Reward retrieval, state, orchestration, business logic, evals, agents, tools, and data processing. "
            "Penalize tutorial/demo-only or simple OpenAI wrapper projects."
        )
        result = self._call(
            system_prompt="You are a strict evaluator of AI project quality. Use short evidence and return JSON only.",
            user_prompt=project_text[:12000],
            response_model=ProjectDepthJudgment,
        )
        if result is None:
            return {"score": 0, "reasoning": "LLM depth judgment unavailable.", "is_thin_wrapper": True}
        return result.model_dump()


llm_adapter = LLMAdapter()
