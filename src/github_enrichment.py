import re
from typing import Any

import requests

from .config import SETTINGS

_GITHUB_CACHE: dict[str, dict[str, Any]] = {}


def parse_github_username(url: str | None) -> str:
    if not url:
        return ""
    match = re.search(r"github\.com[:/]+([^/\s]+)", url, flags=re.IGNORECASE)
    if not match:
        return ""
    return match.group(1).strip("/")


def _headers() -> dict[str, str]:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "resume-screening-system"}
    if SETTINGS.GITHUB_TOKEN:
        headers["Authorization"] = f"token {SETTINGS.GITHUB_TOKEN}"
    return headers


def _score_github_signal(data: dict[str, Any], username: str) -> dict[str, Any]:
    recent_events = []
    repo_names = []
    relevant_repo_count = 0
    created_recent = 0

    events = data.get("events", [])
    for event in events[:10]:
        if event.get("type") == "PushEvent":
            repo_name = event.get("repo", {}).get("name", "")
            recent_events.append(repo_name)
        elif event.get("type") in {"CreateEvent", "WatchEvent", "ForkEvent"}:
            repo_name = event.get("repo", {}).get("name", "")
            recent_events.append(repo_name)

    for repo in data.get("repos", [])[:10]:
        name = repo.get("name", "")
        if name:
            repo_names.append(name)
        if repo.get("updated_at"):
            created_recent += 1
        if any(token in (repo.get("description") or "").lower() for token in ["python", "langchain", "rag", "agent", "llm", "ai", "vector", "fastapi"]):
            relevant_repo_count += 1

    recent_activity_score = min(5, max(0, len(recent_events) // 2))
    repo_score = min(5, max(0, relevant_repo_count + max(0, len(repo_names) // 3)))
    total = min(10, recent_activity_score + repo_score)

    return {
        "username": username,
        "status": "ok",
        "score": total,
        "summary": f"GitHub activity near {username} indicates {total}/10 signal strength.",
        "repo_count": len(repo_names),
        "relevant_repo_count": relevant_repo_count,
        "recent_activity": recent_events,
        "repos": repo_names,
    }


def fetch_github_signal(username: str, url: str | None = None) -> dict[str, Any]:
    if not username:
        return {"username": "", "status": "missing", "score": 0, "summary": "No GitHub username found in resume.", "recent_activity": [], "repos": []}
    if username in _GITHUB_CACHE:
        return _GITHUB_CACHE[username]

    try:
        user_response = requests.get(f"https://api.github.com/users/{username}", headers=_headers(), timeout=10)
        if user_response.status_code in {404, 403}:
            result = {"username": username, "status": "missing", "score": 0, "summary": "GitHub profile missing or private.", "repo_count": 0, "relevant_repo_count": 0, "recent_activity": [], "repos": []}
            _GITHUB_CACHE[username] = result
            return result
        user_response.raise_for_status()
        user_data = user_response.json()
        public_repos = user_data.get("public_repos", 0)

        repos_response = requests.get(f"https://api.github.com/users/{username}/repos?per_page=5&type=owner", headers=_headers(), timeout=10)
        repos_response.raise_for_status()
        repos = repos_response.json() if isinstance(repos_response.json(), list) else []
        events_response = requests.get(f"https://api.github.com/users/{username}/events/public?per_page=10", headers=_headers(), timeout=10)
        events_response.raise_for_status()
        events = events_response.json() if isinstance(events_response.json(), list) else []

        payload = {"events": events, "repos": repos, "public_repos": public_repos}
        result = _score_github_signal(payload, username)
        if not result["repos"] and public_repos == 0:
            result["summary"] = "GitHub profile exists but has no public repo activity available."
        _GITHUB_CACHE[username] = result
        return result
    except Exception:
        result = {"username": username, "status": "failed", "score": 0, "summary": "GitHub API unavailable or rate-limited; continuing without enrichment.", "repo_count": 0, "relevant_repo_count": 0, "recent_activity": [], "repos": []}
        _GITHUB_CACHE[username] = result
        return result


def enrich_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    username = parse_github_username(candidate.get("github_url", ""))
    signal = fetch_github_signal(username, candidate.get("github_url"))
    signal["status"] = signal.get("status", "missing")
    return signal
