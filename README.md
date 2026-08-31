# AI Resume Screening & Ranking System

This project screens and ranks PDF resumes for Python + AI/agentic fit using a deterministic eligibility gate, a scoring model, optional GitHub enrichment, and an LLM adapter for judgment calls.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:
   `pip install -r requirements.txt`
3. Copy the example environment file:
   `copy .env.example .env`
4. Fill in your API keys if needed.

## Run the CLI

```bash
python src/main.py --input ./resumes --output ./output/results.json
```

## Design Decisions

The eligibility filter is deliberately rule-based and deterministic. A candidate only passes if there is clear evidence of Python usage and meaningful AI/agentic work. This avoids handing a soft, opaque LLM the authority to reject resumes before a human review.

The scoring model rewards actual system depth rather than keyword stuffing. AI project depth prioritizes retrieval, orchestration, tool use, memory, evaluation, and real business logic over simple API wrappers. Python and backend engineering rewards evidence in projects and work history rather than a stack list alone. GitHub activity is treated as a supporting signal and capped at 10 points, with failures gracefully ignored instead of blocking the batch.

LLM usage is intentionally narrow. It is used for semantic extraction and quality judgment, but every call is structured through Pydantic schemas and every failure is handled per candidate without crashing the run. This keeps the gate deterministic while still allowing useful judgment on project depth and nuance.

GitHub scoring is based on public activity and repo relevance. The system caches usernames within a run, tolerates private or rate-limited GitHub profiles, and falls back to zero points instead of failing the whole screening batch.

## If I Had More Time

1. Add DOCX and text file ingestion support for broader resume coverage.
2. Add richer project extraction and section normalization to better handle varied resume layouts.
3. Add a web UI or API layer for reviewing ranked candidates.
4. Add more robust LLM evaluation with confidence scoring and fallback heuristics.

## Notes

- The app reads all PDFs in the input folder.
- Malformed or unreadable resumes are logged and counted as failed without stopping the rest of the batch.
- The `output/results.json` file is overwritten on each run.
