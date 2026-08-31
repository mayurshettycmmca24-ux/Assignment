from src.parser import extract_name, extract_email, extract_skills, extract_github_url


def test_extract_name_skips_section_headers_with_colons():
    """
    Regression test: section headers with colons (e.g., "Databases: MongoDB, MySQL")
    should not be picked as the candidate's name.
    """
    resume_text = """Databases: MongoDB, MySQL
Python, FastAPI, PostgreSQL

Mayur Shetty
mayur.shetty@example.com
github.com/mayurshetty

Experience:
Built RAG systems with LangChain and retrieval over embeddings."""
    
    name = extract_name(resume_text)
    assert name == "Mayur Shetty"
    assert name != "Databases: MongoDB, MySQL"


def test_extract_name_prefers_capitalized_name_over_section_headers():
    """
    Name extraction should prefer lines with proper names (2-4 words with capitalization)
    over section headers that might appear first.
    """
    resume_text = """Skills: Python, FastAPI, Docker, Kubernetes
Projects: RAG systems, multi-agent workflows

John Smith
john.smith@example.com"""
    
    name = extract_name(resume_text)
    assert name == "John Smith"


def test_extract_name_fallback_to_email_when_no_clear_name():
    """
    If no clear name pattern is found, fall back to deriving from email local part.
    """
    resume_text = """Contact Information
Email: alice_chen@example.com
GitHub: github.com/alicechen

Experience: Built AI systems"""
    
    name = extract_name(resume_text)
    assert name == "Alice Chen"


def test_extract_name_handles_resume_with_titles():
    """
    Resume should extract name correctly even if job titles appear early.
    """
    resume_text = """Senior Software Engineer
AI/ML focus

Sarah Johnson
sarah.johnson@example.com

Built multi-agent systems with LangGraph."""
    
    name = extract_name(resume_text)
    assert name == "Sarah Johnson"


def test_extract_email_finds_valid_email():
    resume_text = "Contact: mayur.shetty@example.com or mayur@company.org"
    email = extract_email(resume_text)
    assert email == "mayur.shetty@example.com"


def test_extract_github_url():
    resume_text = "GitHub: https://github.com/mayurshetty | Portfolio: example.com"
    url = extract_github_url(resume_text)
    assert url == "https://github.com/mayurshetty"
