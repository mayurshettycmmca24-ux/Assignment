import re
import sys
from pathlib import Path

import pdfplumber
from pypdf import PdfReader

from .config import SETTINGS
from .models import CandidateProfile


def normalize_whitespace(text: str) -> str:
    return " ".join((text or "").split())


def extract_email(text: str) -> str:
    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return match.group(0) if match else ""


def extract_github_url(text: str) -> str:
    match = re.search(r"https?://github\.com/[^\s]+|github\.com/[^\s]+", text, flags=re.IGNORECASE)
    if not match:
        return ""
    value = match.group(0)
    return value.strip("()[]{}<>\"'")


def extract_name(text: str) -> str:
    """
    Extract a candidate's name from resume text.
    Prioritizes lines that look like actual names:
    - Near the top of the document
    - 2-4 words, title-cased (each word starts capital, rest lowercase) OR all-caps
    - No colons or commas (to avoid section headers and skill lists)
    - Not common section keywords or job titles
    - Fallback to email local part as last resort (with warning)
    """
    section_keywords = {
        "resume", "cv", "profile", "summary", "experience", "education", "contact", "projects", 
        "skills", "certifications", "languages", "references", "objective", "core competencies",
        "engineer", "developer", "architect", "manager", "analyst", "lead", "senior", "junior",
        "focused", "expertise", "specializing", "technologies", "technical"
    }
    
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    
    # Pass 1: Look at first 5 lines for all-caps names (common resume format)
    for line in lines[:5]:
        lower_line = line.lower()
        
        # Skip lines with colons or commas
        if ":" in line or "," in line:
            continue
        
        words = line.split()
        word_count = len(words)
        
        # Check for all-caps name (2-4 words, all uppercase letters)
        if 2 <= word_count <= 4:
            all_caps_words = sum(1 for word in words if word and word.isupper() and word.isalpha())
            if all_caps_words >= 2:  # At least 2 all-caps words (allows middle names/initials)
                return line
    
    # Pass 2: Look at first 20 lines for title-cased names
    for line in lines[:20]:
        lower_line = line.lower()
        
        # Skip lines with colons or commas
        if ":" in line or "," in line:
            continue
        
        # Skip section header keywords
        if any(keyword in lower_line for keyword in section_keywords):
            continue
        
        words = line.split()
        word_count = len(words)
        
        # Valid name line: 2-4 words where most are title-cased
        if 2 <= word_count <= 4:
            # Each word should be title-cased: starts with capital, rest lowercase
            title_cased_words = sum(1 for word in words if word and word[0].isupper() and not word.isupper())
            
            # At least 2 words should be title-cased (allows middle names, suffixes like Jr.)
            if title_cased_words >= 2:
                return line
    
    # Fallback to email local part as last resort
    email = extract_email(text)
    if email:
        name_part = email.split("@")[0].replace(".", " ").replace("_", " ").replace("-", " ")
        if name_part and len(name_part.split()) >= 1:
            # Warn when falling back to email derivation
            derived_name = name_part.title()
            print(f"WARNING: Name extraction fell back to email local part. Derived name: {derived_name}", file=sys.stderr)
            return derived_name
    
    return "Unknown Candidate"


def extract_skills(text: str) -> list[str]:
    lowered = text.lower()
    skills = []
    for keyword in SETTINGS.PYTHON_KEYWORDS + SETTINGS.AI_KEYWORDS + SETTINGS.CLOUD_KEYWORDS + SETTINGS.FRONTEND_KEYWORDS + SETTINGS.ENGINEERING_DEPTH_KEYWORDS:
        term = keyword.lower()
        if term in lowered:
            skills.append(keyword)
    return sorted(set(skills), key=lambda s: s.lower())


def extract_project_phrases(text: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
    projects = []
    for sentence in sentences:
        s = sentence.strip()
        if not s:
            continue
        lower = s.lower()
        if any(trigger in lower for trigger in ["built", "developed", "implemented", "created", "designed", "launched", "engineered"]) and len(s.split()) >= 6:
            projects.append(s)
    if not projects:
        for section in re.split(r"\n\s*\n", text):
            if len(section.split()) >= 10:
                projects.append(section.strip())
    return projects[:5]


def extract_pdf_text(pdf_path: Path) -> str:
    text_parts: list[str] = []
    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                if page_text:
                    text_parts.append(page_text)
        if "".join(text_parts).strip():
            return "\n".join(text_parts)
    except Exception:
        pass

    try:
        reader = PdfReader(str(pdf_path))
        for page in reader.pages:
            text = page.extract_text() or ""
            if text:
                text_parts.append(text)
        return "\n".join(text_parts)
    except Exception:
        return ""


def parse_resume_file(file_path: Path) -> CandidateProfile:
    raw_text = extract_pdf_text(file_path)
    if not raw_text.strip():
        raise ValueError("No readable text extracted from PDF")

    name = extract_name(raw_text)
    email = extract_email(raw_text)
    github_url = extract_github_url(raw_text)
    skills = extract_skills(raw_text)
    projects = extract_project_phrases(raw_text)

    return CandidateProfile(
        name=name,
        email=email,
        skills=skills,
        projects=projects,
        github_url=github_url,
        raw_text=raw_text,
    )


def parse_resume_directory(input_dir: str | Path) -> tuple[list[CandidateProfile], dict[str, int]]:
    folder = Path(input_dir)
    profiles: list[CandidateProfile] = []
    summary = {"total": 0, "parsed": 0, "failed": 0}

    if not folder.exists():
        return profiles, summary

    files = sorted(folder.iterdir(), key=lambda p: p.name.lower())
    for pdf_file in files:
        if pdf_file.is_dir() or pdf_file.suffix.lower() not in {".pdf", ".PDF"}:
            continue
        summary["total"] += 1
        try:
            profile = parse_resume_file(pdf_file)
            profiles.append(profile)
            summary["parsed"] += 1
        except Exception as exc:
            summary["failed"] += 1
            print(f"Failed to parse {pdf_file.name}: {exc}")
    return profiles, summary
