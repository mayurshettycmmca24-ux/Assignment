from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, ListFlowable

ROOT = Path(__file__).resolve().parents[1]
RESUMES_DIR = ROOT / "resumes"
RESUMES_DIR.mkdir(exist_ok=True)


def build_resume(name, email, skills, projects, github_url=None, extra_experience=None):
    skills_text = ", ".join(skills)
    project_paragraphs = []
    for project in projects:
        project_paragraphs.append(Paragraph(project, styles["ResumeBodyText"]))
        project_paragraphs.append(Spacer(1, 6))

    experience = []
    if extra_experience:
        experience.append(Paragraph("<b>Experience</b>", styles["ResumeHeading2"]))
        for item in extra_experience:
            experience.append(Paragraph(item, styles["ResumeBodyText"]))
            experience.append(Spacer(1, 5))

    story = [
        Paragraph(f"<b>{name}</b>", styles["ResumeTitle"]),
        Paragraph(f"{email}", styles["ResumeBodyText"]),
        Paragraph(f"GitHub: {github_url}" if github_url else "GitHub: unavailable", styles["ResumeBodyText"]),
        Spacer(1, 12),
        Paragraph("<b>Skills</b>", styles["ResumeHeading2"]),
        Paragraph(skills_text, styles["ResumeBodyText"]),
        Spacer(1, 12),
        Paragraph("<b>Projects</b>", styles["ResumeHeading2"]),
    ]
    story.extend(project_paragraphs)
    story.append(Spacer(1, 12))
    story.extend(experience)
    return story


def write_resume(filename, payload):
    doc = SimpleDocTemplate(
        str(filename),
        pagesize=LETTER,
        leftMargin=52,
        rightMargin=52,
        topMargin=40,
        bottomMargin=40,
    )
    story = build_resume(
        payload["name"],
        payload["email"],
        payload["skills"],
        payload["projects"],
        payload.get("github_url"),
        payload.get("experience"),
    )
    doc.build(story)


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="ResumeTitle", fontName="Helvetica-Bold", fontSize=18, leading=22, spaceAfter=6, textColor=colors.HexColor("#1f2937")))
styles.add(ParagraphStyle(name="ResumeHeading2", fontName="Helvetica-Bold", fontSize=11, leading=14, spaceBefore=8, spaceAfter=6, textColor=colors.HexColor("#111827")))
styles.add(ParagraphStyle(name="ResumeBodyText", fontName="Helvetica", fontSize=9.5, leading=13, spaceAfter=4, textColor=colors.HexColor("#1f2937")))


candidates = [
    {
        "name": "Alicia Moreno",
        "email": "alicia.moreno@gmail.com",
        "github_url": "https://github.com/aliciamoreno",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Redis", "LangGraph", "RAG", "Pinecone", "Docker", "GCP", "Pytest", "OpenTelemetry"],
        "projects": [
            "Built a multi-agent LangGraph customer support platform that orchestrated retrieval, tool-calling, and approval workflows for enterprise tickets. The system indexed technical docs into Pinecone vector stores, used hybrid retrieval with reranking, and compared multiple retrieval strategies in an evaluation harness to improve answer quality. I also added retry logic, observability, and async job queues for production reliability.",
            "Developed a FastAPI backend for a document intelligence assistant that processed support emails, extracted structured metadata, and routed actions through a decision graph. I implemented PostgreSQL persistence, Redis caching, and a deployment pipeline on GCP Cloud Run with Docker containers and monitoring dashboards.",
            "Created a benchmarking suite for retrieval quality with automated evals against customer queries, measuring precision, answer grounding, and latency across chunking strategies and retrieval backends."
        ],
        "experience": [
            "Senior AI Engineer, Northlake Labs — designed agentic workflows for internal automation and enterprise search.",
            "Software Engineer, DataForge — built Python APIs, async data pipelines, and observability for analytics services."
        ],
    },
    {
        "name": "Daniel Patel",
        "email": "daniel.patel@outlook.com",
        "github_url": "https://github.com/danielpatel",
        "skills": ["Python", "FastAPI", "AsyncIO", "PostgreSQL", "Redis", "LangChain", "FAISS", "Docker", "GCP", "SQLAlchemy", "Prometheus"],
        "projects": [
            "Built a retrieval-augmented knowledge assistant for internal engineering documentation using LangChain, FAISS, and async FastAPI services. The app chunked documentation, embedded it with OpenAI models, and implemented prompt chaining for answer generation with provenance logging.",
            "Engineered a support automation system with workflow state tracking, policy checks, and tool calling against internal APIs. The project used Redis for caching and PostgreSQL for session history, and it ran in Docker on Google Cloud Run.",
            "Implemented evaluation scripts for retrieval quality and response grounding, comparing semantic and keyword retrieval paths to guide tuning decisions."
        ],
        "experience": [
            "AI Engineer, SparkPilot — built internal search and workflow systems for product teams.",
            "Python Developer, ArcVector — designed backend APIs for analytics and document search."
        ],
    },
    {
        "name": "Mei Chen",
        "email": "mei.chen@protonmail.com",
        "github_url": "https://github.com/meichen",
        "skills": ["Python", "Django", "FastAPI", "Celery", "PostgreSQL", "Redis", "LangGraph", "OpenAI", "Docker", "Kubernetes", "pytest"],
        "projects": [
            "Designed and shipped an autonomous research assistant with LangGraph for research synthesis. It combined web search, document retrieval, summarization, and stateful planning loops for a multi-step workflow. I implemented retries, fallback prompts, and logging for tool failures.",
            "Created the API layer for a Python backend that served structured summaries to a React UI, with PostgreSQL persistence, Redis for rate limiting, and Celery task workers for asynchronous processing.",
            "Developed a synthetic benchmark suite for agent reasoning and tool use, comparing plan quality across model iterations and prompt strategies."
        ],
        "experience": [
            "Platform Engineer, Qualia Labs — built Python microservices and orchestration tooling.",
            "Senior Backend Engineer, Data Harbor — shipped APIs and data processing workflows."
        ],
    },
    {
        "name": "Omar Haddad",
        "email": "omar.haddad@icloud.com",
        "github_url": "https://github.com/omarhaddad",
        "skills": ["Python", "FastAPI", "Pydantic", "PostgreSQL", "Redis", "Pinecone", "RAG", "LangChain", "Terraform", "GCP", "Docker"],
        "projects": [
            "Built a retrieval engine for policy Q&A that turned internal regulations into searchable embeddings and served responses through a FastAPI app. The system used Pinecone, retrieval ranking, and answer summarization over policy excerpts to reduce manual lookup time.",
            "Created a document ingestion workflow that normalized PDFs, chunked content, and inserted embeddings into vector storage. I built an admin dashboard to monitor indexing health and query latency across multiple corpora.",
            "Deployed the service on GCP with Docker and Terraform, using Redis for cache invalidation and PostgreSQL for audit logs and user history."
        ],
        "experience": [
            "AI Engineer, GovernFlow — built compliance and retrieval workflows across public policy corpora.",
            "Software Engineer, Northstack — implemented backend systems for analytics and customer workflows."
        ],
    },
    {
        "name": "Priya Nair",
        "email": "priya.nair@outlook.com",
        "github_url": "https://github.com/priyanair",
        "skills": ["Python", "FastAPI", "LangChain", "RAG", "OpenAI", "Chroma", "PostgreSQL", "Redis", "Docker"],
        "projects": [
            "Built a RAG chatbot for internal product documentation using LangChain, Chroma, and a FastAPI backend. Users could ask questions about architecture, onboarding, and release notes, and the app surfaced source snippets and citations.",
            "Implemented an ingestion pipeline that normalized Markdown and PDF files, chunked them for retrieval, and retrained vector indexes after content updates. I added cache warmups and answer logging to support faster subsequent queries.",
            "Worked with product and support teams to tune retrieval prompts and chunk size based on common user questions and documentation structure."
        ],
        "experience": [
            "Machine Learning Engineer, EchoWorks — developed retrieval and search experiences for internal docs.",
            "Python Developer, BuildHome — maintained API services and internal tooling."
        ],
    },
    {
        "name": "Lucas Bennett",
        "email": "lucas.bennett@gmail.com",
        "github_url": "https://github.com/lucasbennett",
        "skills": ["Python", "LangChain", "RAG", "Azure", "FastAPI", "OpenAI", "FAISS", "SQLAlchemy", "Docker"],
        "projects": [
            "Created a support chatbot for internal knowledge bases using LangChain and retrieval over hundreds of technical documents. The app combined prompt templates, vector search, and answer grounding to support over 50 common support topics.",
            "Built the backend in FastAPI with Azure deployment, SQLAlchemy models, and API endpoints for user sessions and conversation history. I also added basic conversation memory and fallback responses for unsupported queries.",
            "Collaborated on prompt and retrieval tuning to improve answer quality by reducing hallucinations and improving citation quality."
        ],
        "experience": [
            "AI Engineer, Signal Orbit — designed retrieval workflows and chatbot UX.",
            "Backend Engineer, TeleGrid — built Python services and API integrations."
        ],
    },
    {
        "name": "Sofia Alvarez",
        "email": "sofia.alvarez@me.com",
        "github_url": "https://github.com/sofiaalvarez",
        "skills": ["Python", "LangChain", "RAG", "OpenAI", "Flask", "PostgreSQL", "Redis", "AWS", "Docker"],
        "projects": [
            "Developed a customer service copilot using LangChain and vector retrieval over product documentation. The app passed user questions through prompt templates and retrieval steps to produce grounded responses with a fallback to knowledge base search.",
            "Built a lightweight Flask API that logged conversations, stored metadata in PostgreSQL, and used Redis to cache common retrieval queries. I tracked adoption and improved response freshness through an index refresh job.",
            "Wrote prompt evaluation notes and response quality checks for common service queries, with metrics around answer relevance and retrieval coverage."
        ],
        "experience": [
            "Software Engineer, NovaStack — built AI assistant experiences and internal tooling.",
            "Developer, Mariner Labs — maintained web services and deployment tasks."
        ],
    },
    {
        "name": "Nikhil Sharma",
        "email": "nikhil.sharma@live.com",
        "github_url": "https://github.com/nikhilsharma",
        "skills": ["Python", "OpenAI", "FastAPI", "Flask", "HTTP APIs", "PostgreSQL", "Redis"],
        "projects": [
            "Built a chatbot using the OpenAI API to answer user questions about company policies and product FAQs. The app exposed a REST API and used prompt templates, making it easy for the frontend to call the model and display responses.",
            "Created a small admin interface to track conversation logs and prompt usage, with basic session bookkeeping in PostgreSQL. There was no retrieval system or workflow orchestration beyond passing the request to the model.",
            "Deployed the app using a simple FastAPI service and container setup for internal demos."
        ],
        "experience": [
            "Backend Engineer, SupportFlow — built internal APIs and service tooling.",
            "Full-stack Developer, Altitude Studio — developed dashboards and customer-facing features."
        ],
    },
    {
        "name": "Julia Park",
        "email": "julia.park@outlook.com",
        "skills": ["Python", "OpenAI", "LangChain", "Flask", "APIs"],
        "projects": [
            "Built a small chatbot with LangChain and the OpenAI API to answer basic questions from a product knowledge base. It was a quick prototype using a few prompt templates and no formal retrieval strategies or business logic beyond the model response.",
            "Created a toy project for learning prompt chaining and a lightweight web interface to submit questions, with minimal persistence and no production operations or evaluation pipeline.",
            "Worked on a course project exploring LLMs and prompt templates, but did not integrate advanced state, retrieval, or backend workflows."
        ],
        "experience": [
            "Independent developer — built learning prototypes and educational demos for AI projects."
        ],
    },
    {
        "name": "Maya Ross",
        "email": "maya.ross@icloud.com",
        "skills": ["Python", "LangChain", "RAG", "FastAPI", "Vector DBs", "Docs Search"],
        "projects": [
            "Created a prototype for a document search assistant using LangChain and a vector database to help employees query onboarding materials. It used straightforward retrieval and basic prompt chaining, but the system was still in early development.",
            "Built a simple dashboard to present documents and summaries, and tracked a few example questions to test retrieval quality. There was limited evaluation and no multi-agent orchestration.",
            "Worked on pilot implementation for internal knowledge access with room to grow into a more robust product."
        ],
        "experience": [
            "Product Engineer, Kindred Labs — built prototypes for internal AI search tools."
        ],
    },
    {
        "name": "Ethan Brooks",
        "email": "ethan.brooks@company.com",
        "github_url": "https://github.com/ethanbrooks",
        "skills": ["Python", "Django", "FastAPI", "PostgreSQL", "Redis", "Celery", "AWS", "Docker", "pytest"],
        "projects": [
            "Developed a Python customer analytics platform with Django and FastAPI services for ingestion, aggregation, and policy processing. The system handled event data from mobile clients, built reporting endpoints, and stored results in PostgreSQL with Redis-based caching.",
            "Implemented background jobs with Celery for periodic refreshes and notification workflows, including retry logic and error tracking for failed jobs. I also added monitoring dashboards and regression tests around billing logic.",
            "Created internal APIs for reporting and operational decisions, using robust validation and structured logging for service reliability."
        ],
        "experience": [
            "Backend Engineer, Streamline Cloud — built data products and Python services for customer operations.",
            "Senior Engineer, GridWorks — owned API reliability and platform monitoring."
        ],
    },
    {
        "name": "Felix Nguyen",
        "email": "felix.nguyen@protonmail.com",
        "skills": ["JavaScript", "React", "Node.js", "Spring Boot", "MySQL", "Next.js"],
        "projects": [
            "Built a full-stack commerce platform with React and Next.js for storefront experiences, with a Spring Boot backend and MySQL persistence. The project handled checkout flows, catalog browsing, and inventory updates for a retailer client.",
            "Developed an internal admin dashboard with role-based access and analytics panels for sales and merchandising. I integrated payment and order APIs and worked closely with product teams on business requirements.",
            "Led the front-end architecture for a responsive web application and coordinated deployment with the team."
        ],
        "experience": [
            "Full-Stack Engineer, Vantage Commerce — built e-commerce systems and web experiences.",
            "Software Engineer, Nucleus Labs — built services for checkout and product management."
        ],
    },
    {
        "name": "Harper Singh",
        "email": "harper.singh@outlook.com",
        "github_url": "https://github.com/harpersingh",
        "skills": ["Java", "Spring Boot", "React", "Node.js", "PostgreSQL", "Docker", "AWS"],
        "projects": [
            "Built a Java-based microservices platform for shipping logistics and order processing. The system coordinated inventory updates, delivery status checks, and internal dashboards for operations staff using Spring Boot and PostgreSQL.",
            "Developed a React frontend for tracking shipments and warehouse inventory, and integrated with internal APIs for route optimization and status notifications.",
            "Deployed the platform on AWS with Docker-based services and supported observability workflows for incident response."
        ],
        "experience": [
            "Platform Engineer, RouteFlow — built enterprise systems for logistics and inventory monitoring.",
            "Software Developer, HarborOps — maintained backend services for operations teams."
        ],
    },
    {
        "name": "Chloe Martin",
        "email": "chloe.martin@gmail.com",
        "github_url": "https://github.com/chloemartin",
        "skills": ["Python", "FastAPI", "PostgreSQL", "React", "Docker", "GCP", "Redis"],
        "projects": [
            "Built an internal operations portal with FastAPI and PostgreSQL that aggregated deployment health, customer incidents, and service metrics. The system exposed a clean API for the dashboard, used Redis for hot query caching, and supported deployment in GCP.",
            "Worked with product teams to add role-based access controls, ticket workflows, and historical views for operations staff. I wrote tests for service endpoints and integrated a CI pipeline for automated checks.",
            "Worked on deployment tooling and dashboard reliability improvements to reduce incident response time."
        ],
        "experience": [
            "Full-Stack Engineer, Northspring — built platform tooling for reliability and operations.",
            "Product Engineer, Beacon Data — maintained interfaces for internal teams."
        ],
    },
    {
        "name": "Ibrahim Yusuf",
        "email": "ibrahim.yusuf@protonmail.com",
        "skills": ["JavaScript", "Next.js", "React", "Node.js", "GraphQL", "TypeScript"],
        "projects": [
            "Built a content platform with Next.js and React for editorial publishing, including a rich authoring dashboard and article management workflows. The UI was tightly integrated with a Node.js API and content services.",
            "Created a custom analytics dashboard for tracking engagement, article performance, and marketing funnels, using GraphQL APIs for data access and a server-rendered front-end architecture.",
            "Worked closely with stakeholders to redesign the user experience and improve conversion metrics across editor workflows."
        ],
        "experience": [
            "Frontend Engineer, Lumina Media — built editorial web experiences and dashboard tooling.",
            "Web Developer, Cedar Works — maintained marketing sites and product interfaces."
        ],
    },
]

# Create files in the expected order for the pipeline
for index, payload in enumerate(candidates, start=1):
    filename = RESUMES_DIR / f"candidate_{index:02d}.pdf"
    write_resume(filename, payload)

print(f"Generated {len(candidates)} sample resumes in {RESUMES_DIR}")
