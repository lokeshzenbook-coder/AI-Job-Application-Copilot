# AI Job Application Copilot

An AI-powered job discovery and application-preparation platform that finds relevant DevOps/DevSecOps opportunities, evaluates resume-to-JD fit using weighted skill scoring, generates tailored application materials, and keeps final submission under explicit human control.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [Architecture](#architecture)
4. [Technology Stack](#technology-stack)
5. [How It Works](#how-it-works)
6. [AI Matching System](#ai-matching-system)
7. [Safety and Human Approval](#safety-and-human-approval)
8. [Project Structure](#project-structure)
9. [Prerequisites](#prerequisites)
10. [Installation](#installation)
11. [Environment Variables](#environment-variables)
12. [Configuration](#configuration)
13. [Running the Application](#running-the-application)
14. [API Documentation](#api-documentation)
15. [Database](#database)
16. [Excel Export](#excel-export)
17. [Playwright Workflow](#playwright-workflow)
18. [Testing](#testing)
19. [Docker](#docker)
20. [Troubleshooting](#troubleshooting)
21. [Security](#security)
22. [Limitations](#limitations)
23. [Roadmap](#roadmap)
24. [Contributing](#contributing)
25. [License](#license)

---

## Project Overview

Job seekers in DevOps, DevSecOps, and Platform Engineering roles face a fragmented manual process: searching multiple job boards, reading hundreds of job descriptions, tailoring resumes for each application, and tracking submissions across spreadsheets.

This project automates the repetitive parts of that workflow while keeping the human in control of every submission decision.

**What it does:**

- Discovers relevant job postings from LinkedIn via Apify
- Filters by posting date (configurable window, default 24 hours)
- Removes exact and fuzzy duplicates across search results
- Parses uploaded resumes into structured candidate profiles using Claude
- Compares each job description against the resume using weighted AI scoring
- Generates job-specific tailored resumes and cover letters
- Prepares application forms using browser automation (Playwright)
- Requires explicit human approval before any application is submitted
- Tracks all jobs and applications through a web dashboard
- Exports results to formatted Excel and CSV files

**Who it is for:**

Engineers targeting DevOps, DevSecOps, SRE, Platform Engineering, and Infrastructure roles — particularly in the Indian market — who want to apply selectively rather than mass-apply.

---

## Key Features

### Job Discovery

- Apify-powered LinkedIn job scraping across configurable search terms
- 15 pre-configured DevOps/DevSecOps role titles as search keywords
- 10 Indian city/region location targets
- Configurable time-window filtering (default: last 24 hours)
- Automatic deduplication using SHA-256 fingerprinting and fuzzy title matching (85% similarity threshold)

### AI Analysis

- Resume parsing from PDF, DOCX, and TXT files via Claude
- Structured extraction of skills, experience, certifications, and employers into 10+ skill categories
- Resume-to-JD matching using weighted scoring across 11 skill dimensions
- Match score (0–100), interview probability (VERY_HIGH / HIGH / MEDIUM / LOW), and recommendation (APPLY / MANUAL_REVIEW / REJECT)
- Mandatory and nice-to-have skill gap detection
- Configurable match threshold (default: 85%) for automatic application queuing

### Application Preparation

- Job-specific resume tailoring that reorders and rephrases existing experience for ATS optimization
- Concise cover letter generation referencing only verified resume evidence
- Resume and cover letter stored per-job in `generated/` directory

### Browser Automation

- Playwright-based application page analysis
- CAPTCHA, MFA/2FA, and login-wall detection with 9+ selector patterns
- Standard field detection and filling (name, email, phone, location, LinkedIn, GitHub, portfolio)
- Resume file upload to detected file inputs
- Never clicks submit — stops before any irreversible action

### Tracking and Export

- SQLite database for development, PostgreSQL-compatible schema
- Dashboard with 8 key metrics
- Application status tracking through full lifecycle
- Multi-sheet XLSX export (Top Jobs, Candidate Profile, Skill Match, Application Tracker)
- CSV export for job matches

---

## Architecture

```mermaid
graph TD
    A[Resume Upload] --> B[Text Extraction<br/>PDF / DOCX / TXT]
    B --> C[Claude Resume Parsing]
    C --> D[Candidate Profile<br/>Structured JSON]

    E[Apify API] --> F[LinkedIn Job Search<br/>15 Roles × 10 Locations]
    F --> G[24h Time Filter]
    G --> H[Deduplication<br/>Exact + Fuzzy]
    H --> I[Job Database]

    D --> J[Claude JD Analysis]
    I --> J
    J --> K[Weighted Match Scoring<br/>11 Skill Dimensions]
    K --> L{Score ≥ 85%<br/>AND<br/>No Mandatory Gaps?}
    L -->|Yes| M[Application Queue]
    L -->|No| N[Matched — Visible but Not Queued]

    M --> O[Resume Tailoring<br/>Claude]
    M --> P[Cover Letter Generation<br/>Claude]
    O --> Q[Playwright<br/>Form Analysis]
    P --> Q
    Q --> R{CAPTCHA / MFA / Login?}
    R -->|Yes| S[Human Action Required]
    R -->|No| T[Form Fields Filled]
    T --> U[Human Review]
    S --> U
    U -->|Approve| V[Application Submitted<br/>Manual]
    U -->|Reject| W[Application Cancelled]

    I --> X[Dashboard]
    M --> X
    X --> Y[Excel / CSV Export]
```

---

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Backend | Python 3.12, FastAPI 0.115, Pydantic 2.10, SQLAlchemy 2.0 | REST API, data validation, ORM |
| AI | Claude (claude-sonnet-4-20250514 via Anthropic SDK) | Resume parsing, JD matching, tailoring, cover letters |
| Job Discovery | Apify API (apify/linkedin-jobs-scraper actor) | LinkedIn job scraping |
| Browser Automation | Playwright 1.49 (Chromium) | Application form detection and filling |
| Database | SQLite 3 (dev) / PostgreSQL 16 (Docker) | Persistent storage |
| Frontend | React 18, TypeScript 5.6, Vite 6, Tailwind CSS 3.4 | Web dashboard |
| Export | openpyxl 3.1 (XLSX), csv module (CSV) | Formatted data export |
| Infrastructure | Docker, Docker Compose, nginx | Production deployment |

---

## How It Works

1. **Upload resume** — User uploads a PDF, DOCX, or TXT resume through the dashboard.

2. **Extract candidate profile** — pdfplumber or python-docx extracts raw text. Claude parses it into a structured profile with 10+ skill categories (AWS, Kubernetes, Terraform, CI/CD, DevSecOps, Python, GitOps, Linux, Observability, Docker), work history, certifications, and education. Only information explicitly present in the resume is captured.

3. **Search jobs** — Apify fetches LinkedIn job listings for each combination of search keywords (15 role titles) and locations (10 Indian cities), returning up to 25 results per search.

4. **Filter by recency** — Jobs are filtered to only include postings within the configured time window (default: 24 hours). Jobs with unknown posting dates are retained.

5. **Deduplicate** — Exact duplicates (same URL) are removed by SHA-256 fingerprint. Fuzzy duplicates (same company + ≥85% title similarity after removing seniority prefixes) are also removed.

6. **AI matching** — For each job, Claude receives the full job description and the candidate's structured profile. It produces a weighted match score, per-skill scores, mandatory and nice-to-have gap lists, and a written rationale.

7. **Score and queue** — Jobs scoring ≥85% with zero mandatory gaps are automatically queued for application. All other analyzed jobs remain visible in the dashboard.

8. **Tailor resume** — For queued jobs, Claude generates a job-specific resume by reordering and rephrasing existing experience. No new information is invented.

9. **Generate cover letter** — Claude writes a concise 3-paragraph cover letter referencing 2–3 specific strengths from the resume.

10. **Prepare application** — Playwright opens the job application URL, detects form fields, and fills verified candidate data (name, email, phone, location). If CAPTCHA, MFA, or login is detected, the application is marked as requiring human action.

11. **Human review** — The dashboard presents the match score, tailored resume, cover letter, and application status for review.

12. **Approve or reject** — The user explicitly approves (sets status to SUBMITTED) or cancels (sets status to WITHDRAWN). The system never auto-submits.

13. **Track** — All jobs and applications are stored in the database with full status history. Results are exportable to Excel and CSV.

---

## AI Matching System

### How Scoring Works

Claude receives the complete job description and the candidate's structured resume profile. It is instructed to be conservative — keyword presence alone does not produce a high score.

### Weighted Skill Dimensions

| Dimension | Weight | What It Evaluates |
|---|---|---|
| AWS | 15% | EC2, EKS, Lambda, IAM, CloudFormation, S3, RDS, etc. |
| Kubernetes / EKS | 15% | K8s administration, Helm, Kustomize, service mesh |
| Terraform / IaC | 12% | Terraform modules, state management, infrastructure as code |
| CI/CD | 12% | Jenkins, GitHub Actions, GitLab CI, ArgoCD pipelines |
| DevSecOps | 12% | SAST, DAST, container scanning, security policy |
| Docker / Containers | 8% | Dockerfile, container orchestration, registry |
| GitOps / Argo CD | 8% | GitOps workflows, declarative deployment |
| Python / Automation | 6% | Scripting, automation, tooling |
| Linux / Networking | 5% | System administration, networking fundamentals |
| Observability | 4% | Prometheus, Grafana, ELK, distributed tracing |
| Other | 3% | Additional relevant skills |

### Output Structure

Each analysis produces:

- `match_score` — Weighted average (0–100)
- `interview_probability` — VERY_HIGH, HIGH, MEDIUM, or LOW
- `recommendation` — APPLY, MANUAL_REVIEW, or REJECT
- Per-skill scores (aws_match, kubernetes_match, etc.)
- `mandatory_gaps` — Required skills missing from resume
- `nice_to_have_gaps` — Preferred skills missing from resume
- `reason` — Written rationale

### Configurable Threshold

Jobs scoring ≥ `JOB_MATCH_THRESHOLD` (default: 85) with zero mandatory gaps are automatically queued. This threshold is configurable via environment variable.

---

## Safety and Human Approval

This system is designed to assist — not replace — the job application process.

**The system never:**

- Fabricates resume information, experience, certifications, employers, or metrics
- Bypasses CAPTCHA, MFA, or anti-bot protections
- Circumvents website authentication or security controls
- Creates fake identities or credentials
- Automatically submits job applications without explicit human approval

**Human-in-the-loop workflow:**

1. Application enters `READY_FOR_REVIEW` status
2. Dashboard displays match score, tailored resume, cover letter, and application details
3. User clicks `Approve & Submit` (with confirmation dialog) or `Cancel`
4. Only after explicit approval does the status change to `SUBMITTED`
5. The `submit` endpoint returns a manual submission instruction — it does not auto-submit

**When Playwright detects CAPTCHA, MFA, or login walls:**

```
STATUS = HUMAN_ACTION_REQUIRED
```

The system stops and waits for the user to complete the interaction manually.

---

## Project Structure

```
ai-job-copilot/
├── .env.example                      # Environment variable template
├── .gitignore
├── docker-compose.yml                # PostgreSQL + backend + frontend
├── README.md
├── backend/
│   ├── Dockerfile                    # Python 3.12-slim
│   ├── pyproject.toml                # Build config + pytest config
│   ├── requirements.txt              # 16 Python dependencies
│   ├── app/
│   │   ├── config.py                 # Pydantic Settings (env vars, search keywords, scoring weights)
│   │   ├── database.py               # SQLAlchemy engine, session, init_db()
│   │   ├── main.py                   # FastAPI app, middleware, router registration
│   │   ├── models.py                 # Job, Application, CandidateProfile ORM models
│   │   ├── schemas.py                # Pydantic request/response schemas
│   │   ├── routers/
│   │   │   ├── resume.py             # Resume upload and profile endpoints
│   │   │   ├── jobs.py               # Job search, list, analyze, tailor, cover letter
│   │   │   ├── applications.py       # Application lifecycle + Playwright form fill
│   │   │   ├── dashboard.py          # Dashboard statistics
│   │   │   └── export.py             # Excel and CSV export
│   │   └── services/
│   │       ├── resume_parser.py      # PDF/DOCX/TXT extraction + Claude parsing
│   │       ├── claude_service.py     # All Claude API calls (match, tailor, cover letter)
│   │       ├── apify_service.py      # LinkedIn job discovery via Apify
│   │       ├── dedup.py              # Exact + fuzzy deduplication
│   │       ├── job_matcher.py        # Time filtering + batch analysis
│   │       ├── excel_export.py       # Multi-sheet XLSX + CSV generation
│   │       └── playwright_service.py # Browser automation + form filling
│   ├── generated/
│   │   ├── resumes/                  # Tailored resumes (per job)
│   │   └── cover_letters/            # Cover letters (per job)
│   ├── uploads/                      # Uploaded resume files
│   └── tests/
│       ├── conftest.py               # Test fixtures (transactional DB, TestClient)
│       ├── test_api.py               # API endpoint tests
│       ├── test_dedup.py             # Deduplication logic tests
│       ├── test_excel_export.py      # Export tests
│       ├── test_job_matcher.py       # Time filtering tests
│       ├── test_phase2.py            # Tailoring, cover letters, application workflow
│       ├── test_phase3.py            # Playwright form fill + human approval gate
│       └── test_resume_parser.py     # Resume extraction tests
└── frontend/
    ├── Dockerfile                    # Multi-stage: Node 20 build → nginx serve
    ├── nginx.conf                    # SPA routing + /api/ reverse proxy
    ├── package.json                  # React, TypeScript, Vite, Tailwind
    ├── vite.config.ts                # Dev proxy to localhost:8000
    ├── tailwind.config.js
    ├── postcss.config.js
    ├── tsconfig.json
    ├── index.html
    └── src/
        ├── main.tsx                  # React entry point
        ├── App.tsx                   # Tab navigation (Dashboard / Jobs / Applications)
        ├── index.css                 # Tailwind base styles
        ├── api/
        │   └── client.ts             # Typed fetch wrapper for all 18 API endpoints
        ├── types/
        │   └── index.ts              # TypeScript interfaces (Job, Application, etc.)
        └── components/
            ├── Dashboard.tsx         # 8-stat-card grid
            ├── ResumeUpload.tsx      # File upload with format validation
            ├── JobTable.tsx          # Searchable, filterable job listing table
            ├── JobDetail.tsx         # Full-screen modal with skill breakdown + actions
            └── ApplicationTracker.tsx # Expandable cards with resume/cover letter status
```

---

## Prerequisites

| Requirement | Version | Purpose |
|---|---|---|
| Python | 3.12+ | Backend runtime |
| Node.js | 20+ | Frontend build |
| npm | 10+ | Frontend package management |
| Anthropic API key | — | Claude for resume parsing, matching, tailoring, cover letters |
| Apify API token | — | LinkedIn job discovery |
| Docker & Docker Compose | 20+ | Production deployment (optional for local dev) |
| Playwright Chromium | — | Browser automation (installed via `playwright install chromium`) |

---

## Installation

### Option A — Local Development

```bash
# Clone the repository
git clone https://github.com/lokeshzenbook-coder/AI-Job-Application-Copilot.git
cd AI-Job-Application-Copilot

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows
pip install -r requirements.txt

# Frontend setup (separate terminal)
cd frontend
npm install
```

### Option B — Docker

```bash
git clone https://github.com/lokeshzenbook-coder/AI-Job-Application-Copilot.git
cd AI-Job-Application-Copilot
cp .env.example .env            # Edit with your API keys
docker compose up --build
```

### Playwright Setup

Playwright requires browser binaries to be installed separately:

```bash
cd backend
source venv/bin/activate
playwright install chromium
playwright install-deps          # Installs OS-level dependencies
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Required | Description | Default |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Claude API key for AI features | (empty) |
| `APIFY_API_TOKEN` | Yes | Apify API token for job discovery | (empty) |
| `APIFY_ACTOR_ID` | No | Apify actor ID for LinkedIn scraping | `apify/linkedin-jobs-scraper` |
| `DATABASE_URL` | No | Database connection string | `sqlite:///./jobs.db` |
| `JOB_MATCH_THRESHOLD` | No | Minimum match score to auto-queue | `85` |
| `JOB_SEARCH_HOURS` | No | Only include jobs posted within N hours | `24` |
| `PLAYWRIGHT_HEADLESS` | No | Run Chromium headless (`true`/`false`) | `true` |
| `TARGET_COUNTRY` | No | Country for job searches | `India` |

**Docker users:** The `docker-compose.yml` overrides `DATABASE_URL` to `postgresql://postgres:postgres@postgres:5432/jobcopilot`. You do not need to set this in `.env` for Docker.

---

## Configuration

### Search Keywords

Defined in `backend/app/config.py` as `SEARCH_KEYWORDS`. Default set of 15 roles:

```
DevOps Engineer, Senior DevOps Engineer, DevSecOps Engineer,
Senior DevSecOps Engineer, AWS DevOps Engineer, Cloud DevOps Engineer,
Platform Engineer, Senior Platform Engineer, Cloud Platform Engineer,
SRE, Site Reliability Engineer, DevOps/SRE Engineer,
DevSecOps/Platform Engineer, Kubernetes Platform Engineer,
Infrastructure Engineer
```

### Search Locations

Defined in `backend/app/config.py` as `SEARCH_LOCATIONS`. Default set of 10 locations:

```
Remote India, India, Hyderabad, Bangalore, Pune,
Chennai, Mumbai, Gurgaon, Noida, Delhi NCR
```

### Scoring Weights

Defined in `backend/app/config.py` as `SCORING_WEIGHTS`:

```python
{
    "aws": 15.0,
    "kubernetes": 15.0,
    "terraform": 12.0,
    "cicd": 12.0,
    "devsecops": 12.0,
    "docker": 8.0,
    "gitops": 8.0,
    "python": 6.0,
    "linux": 5.0,
    "observability": 4.0,
    "other": 3.0,
}
```

All search terms, locations, weights, and thresholds are configurable via environment variables or by editing `config.py`.

---

## Running the Application

### Backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

API documentation available at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm run dev
```

Available at `http://localhost:5173`. The Vite dev server proxies `/api` requests to the backend at `http://localhost:8000`.

### Docker

```bash
cp .env.example .env    # Edit with your API keys
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | `http://localhost:5173` |
| Backend API | `http://localhost:8000` |
| API Docs | `http://localhost:8000/docs` |
| PostgreSQL | `localhost:5432` |

### Tests

```bash
cd backend
source venv/bin/activate
python -m pytest tests/ -v
```

---

## API Documentation

Interactive API documentation is available at `http://localhost:8000/docs` (Swagger UI) when the backend is running.

### Resume

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/resume/upload` | Upload resume (PDF/DOCX/TXT), parse with Claude, create candidate profile |
| GET | `/api/resume/profile` | Retrieve parsed candidate profile |

### Jobs

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/jobs/search` | Search LinkedIn via Apify, filter, deduplicate, store |
| GET | `/api/jobs` | List jobs (query params: `status`, `min_score`, `limit`, `offset`) |
| GET | `/api/jobs/{id}` | Get single job details |
| POST | `/api/jobs/analyze` | Analyze all discovered jobs against resume |
| POST | `/api/jobs/{id}/analyze-single` | Analyze single job |
| POST | `/api/jobs/{id}/tailor-resume` | Generate tailored resume for specific job |
| POST | `/api/jobs/{id}/cover-letter` | Generate cover letter for specific job |

### Applications

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/applications` | List applications (query param: `status`) |
| POST | `/api/applications/{id}/prepare` | Set status to READY_FOR_REVIEW |
| POST | `/api/applications/{id}/approve` | Approve application (human approval gate) |
| POST | `/api/applications/{id}/cancel` | Cancel application (sets WITHDRAWN) |
| POST | `/api/applications/{id}/fill-form` | Playwright form analysis and field filling |
| POST | `/api/applications/{id}/submit` | Final submission gate (manual only) |

### Dashboard and Export

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/dashboard` | Dashboard statistics (8 metrics) |
| GET | `/api/export/excel` | Download multi-sheet XLSX |
| GET | `/api/export/csv` | Download CSV |
| GET | `/api/health` | Health check |

---

## Database

### Engine

- **Development:** SQLite (`sqlite:///./jobs.db`) — zero-config, file-based
- **Docker/Production:** PostgreSQL 16 (`postgresql://postgres:postgres@postgres:5432/jobcopilot`)

The schema is PostgreSQL-compatible. SQLite is used for local development convenience.

### Tables

#### `jobs`

Discovered and analyzed job postings.

| Column | Type | Notes |
|---|---|---|
| id | Integer PK | Auto-increment |
| company | String(500) | Required |
| title | String(500) | Required |
| location | String(500) | |
| remote_type | String(100) | |
| posted_at | DateTime | Nullable |
| url | Text | Required, unique per job |
| description | Text | Full JD text |
| match_score | Float | 0–100, nullable until analyzed |
| interview_probability | String(50) | VERY_HIGH / HIGH / MEDIUM / LOW |
| recommendation | String(50) | APPLY / MANUAL_REVIEW / REJECT |
| experience_match ... gitops_match | Float | Per-skill scores (0–100) |
| mandatory_gaps | Text | JSON array of missing required skills |
| nice_to_have_gaps | Text | JSON array of missing preferred skills |
| match_reason | Text | Written rationale from Claude |
| status | String(50) | See lifecycle below |
| created_at / updated_at | DateTime | Auto-managed |

#### `applications`

Tracks application lifecycle per job.

| Column | Type | Notes |
|---|---|---|
| id | Integer PK | |
| job_id | Integer FK | References `jobs.id` |
| resume_version | String(500) | Path to tailored resume file |
| cover_letter | Text | Generated cover letter text |
| application_url | Text | |
| status | String(50) | See lifecycle below |
| applied_at | DateTime | Nullable |
| interview_date | DateTime | Nullable |
| notes | Text | |
| created_at / updated_at | DateTime | |

#### `candidate_profiles`

Parsed resume data. One row per uploaded resume.

| Column | Type | Notes |
|---|---|---|
| id | Integer PK | |
| raw_text | Text | Full extracted resume text |
| full_name, email, phone, location | String | Contact info |
| summary | Text | Professional summary |
| experience_years | Float | Nullable |
| current_role | String(500) | Most recent title |
| employers, technologies, certifications, education, projects, achievements | Text | JSON arrays |
| aws_experience ... docker_experience | Text | JSON arrays — 10 skill categories |
| structured_profile | Text | Complete JSON profile |
| created_at / updated_at | DateTime | |

### Application Status Lifecycle

```
DISCOVERED → ANALYZING → MATCHED → QUEUED → READY_FOR_REVIEW → SUBMITTED
                                         ↘                    ↗
                                    REJECTED            INTERVIEW
                                                           ↓
                                                          OFFER
                                                           or
                                                        WITHDRAWN
```

| Status | Meaning |
|---|---|
| DISCOVERED | Found by Apify, not yet analyzed |
| ANALYZING | Claude is processing the JD |
| MATCHED | Analyzed, below threshold or has gaps |
| QUEUED | Meets threshold, auto-queued for application |
| READY_FOR_REVIEW | Prepared for human review |
| SUBMITTED | Approved by user (manual submission) |
| REJECTED | User decided not to apply |
| INTERVIEW | Interview scheduled |
| OFFER | Offer received |
| WITHDRAWN | Application cancelled |

---

## Excel Export

### How to Export

- **Dashboard:** Click the "Export Excel" button in the header
- **API:** `GET /api/export/excel` (XLSX) or `GET /api/export/csv` (CSV)

### XLSX Sheets

**Sheet 1 — Top Jobs**

| Column | Content |
|---|---|
| Rank | Ordered by match score |
| Job Title, Company, Location, Remote Type | Job details |
| Posted Time | When the job was posted |
| Job URL | Clickable hyperlink |
| Match Score | 0–100% |
| Interview Probability | VERY_HIGH / HIGH / MEDIUM / LOW |
| Matching Skills | Skills with score ≥ 70% |
| Missing Skills | Mandatory + nice-to-have gaps |
| Strongest Resume Evidence | Top 3 skill scores |
| Priority | HIGH (≥90%) / MEDIUM (≥85%) / LOW |
| Recommended Action | APPLY / MANUAL_REVIEW / REJECT |

**Sheet 2 — Candidate Profile**

Parsed resume fields as field/value pairs.

**Sheet 3 — Skill Match**

Per-job comparison of AWS, Kubernetes, Terraform, CI/CD, DevSecOps, Python, and GitOps scores.

**Sheet 4 — Application Tracker**

Company, role, URL, priority, status, date applied, notes.

### Formatting

- Styled headers (dark blue background, white bold text)
- Auto-filter on all columns
- Frozen header row
- Wrapped text and appropriate column widths

---

## Playwright Workflow

```
Job Application URL
        ↓
   Open Chromium (headless by default)
        ↓
   Navigate to URL (30s timeout)
        ↓
   Detect Blockers
   ├── CAPTCHA detected? → HUMAN_ACTION_REQUIRED
   ├── MFA/2FA detected? → HUMAN_ACTION_REQUIRED
   └── Login wall detected? → HUMAN_ACTION_REQUIRED
        ↓
   Detect Form Fields
   (all visible inputs, textareas, selects)
        ↓
   Fill Verified Candidate Data
   (name, email, phone, location, LinkedIn, GitHub, portfolio)
        ↓
   Upload Tailored Resume
   (if file input detected)
        ↓
   STOP — Do Not Submit
        ↓
   Return results to dashboard for human review
```

### Authentication

Playwright does not handle authentication sessions. If a login wall is detected, the system marks the application as `HUMAN_ACTION_REQUIRED` and stops. The user must log in manually or provide session cookies.

### Selector Coverage

- **CAPTCHA:** 9 CSS selectors (reCAPTCHA, hCAPTCHA, generic challenge patterns)
- **MFA/2FA:** 7 CSS selectors (OTP inputs, code fields)
- **Login:** 5 CSS selectors (password fields, login forms)

---

## Testing

### Framework

- **pytest** 8.3.4 with pytest-asyncio 0.25.0
- **FastAPI TestClient** for HTTP-level integration tests
- **Transaction-based isolation** — each test runs in a rolled-back transaction

### Test Files

| File | Tests | Coverage |
|---|---|---|
| `test_api.py` | 11 | Health, resume upload, job listing, applications, dashboard, export |
| `test_dedup.py` | 13 | Fingerprinting, normalization, exact dedup, fuzzy dedup |
| `test_excel_export.py` | 3 | Empty export, export with job data |
| `test_job_matcher.py` | 4 | 24h filtering, boundary conditions |
| `test_phase2.py` | 6 | Resume tailoring, cover letters, application workflow |
| `test_phase3.py` | 4 | Playwright form fill, human approval gate |
| `test_resume_parser.py` | 5 | TXT extraction, unsupported format, basic parsing |
| **Total** | **47** | |

### Running Tests

```bash
cd backend
source venv/bin/activate
python -m pytest tests/ -v
```

Tests mock external APIs (Anthropic, Apify) by setting empty API keys. No real job applications are submitted during testing.

---

## Docker

### Services

| Service | Image / Build | Port | Purpose |
|---|---|---|---|
| `backend` | `./backend` (Python 3.12-slim) | 8000 | FastAPI API server |
| `frontend` | `./frontend` (Node 20 build → nginx) | 5173 → 80 | Static SPA served by nginx |
| `postgres` | `postgres:16-alpine` | 5432 | Production database |

### Volumes

| Volume | Purpose |
|---|---|
| `pgdata` | PostgreSQL data persistence |
| `backend_generated` | Generated resumes and cover letters |
| `backend_uploads` | Uploaded resume files |

### Health Checks

- **Backend:** `http://localhost:8000/api/health` every 30s
- **PostgreSQL:** `pg_isready -U postgres` every 10s
- **Frontend:** Depends on backend health

### Startup

```bash
docker compose up --build
```

The backend waits for PostgreSQL to be healthy before starting. The frontend waits for the backend.

### Development vs Production

| Aspect | Local Development | Docker |
|---|---|---|
| Database | SQLite (file) | PostgreSQL 16 |
| Frontend dev server | Vite (HMR) | nginx (static build) |
| API proxy | Vite proxy config | nginx reverse proxy |
| File uploads | Local `uploads/` dir | Docker volume |
| Generated files | Local `generated/` dir | Docker volume |

---

## Troubleshooting

### Apify Connection Failure

**Symptoms:** "Search LinkedIn Jobs" returns empty results or error.

**Check:**
1. `APIFY_API_TOKEN` is set in `.env` and is valid
2. Your Apify account has available compute units
3. The actor ID (`APIFY_ACTOR_ID`) is correct — default is `apify/linkedin-jobs-scraper`
4. LinkedIn hasn't rate-limited your Apify account

**Fix:** Verify at `https://console.apify.com/account/integrations`.

### Claude API Failure

**Symptoms:** Resume parsing, matching, or tailoring returns fallback results.

**Check:**
1. `ANTHROPIC_API_KEY` is set in `.env` and is valid
2. Your Anthropic account has available credits
3. The model `claude-sonnet-4-20250514` is accessible from your account

**Fix:** Verify at `https://console.anthropic.com/settings/keys`.

### Playwright Failure

**Symptoms:** `fill-form` endpoint returns ERROR status.

**Check:**
1. Playwright is installed: `pip install playwright`
2. Chromium browser is installed: `playwright install chromium`
3. OS dependencies are installed: `playwright install-deps`
4. `PLAYWRIGHT_HEADLESS=true` for server environments

**Fix:**
```bash
playwright install chromium
playwright install-deps
```

### No Jobs Found

**Symptoms:** Search returns 0 results.

**Check:**
1. Apify token is valid and has compute units
2. Try increasing `JOB_SEARCH_HOURS` (e.g., to 48 or 72) to widen the window
3. LinkedIn may have limited scraping — wait and retry

### Database Errors

**Symptoms:** 500 errors on API calls.

**Check:**
1. `DATABASE_URL` in `.env` points to an accessible database
2. For SQLite, the `backend/` directory is writable
3. For PostgreSQL in Docker, the `postgres` service is healthy: `docker compose ps`

---

## Security

### Secret Management

- API keys (`ANTHROPIC_API_KEY`, `APIFY_API_TOKEN`) are stored in `.env` — never committed to the repository
- `.gitignore` excludes `.env`, `*.db`, `uploads/`, `generated/`, `node_modules/`, `dist/`
- Structured logging never includes API keys, tokens, or credentials

### Input Validation

- Resume uploads are validated against allowed extensions (`.pdf`, `.docx`, `.txt`)
- Pydantic schemas enforce type and field validation on all API inputs
- SQL injection prevented by SQLAlchemy ORM (parameterized queries)

### Browser Automation Safety

- Playwright never clicks submit buttons
- CAPTCHA, MFA, and login walls cause immediate halt with `HUMAN_ACTION_REQUIRED` status
- Only verified candidate data from the parsed resume is used to fill forms

### Application Submission

- Applications require explicit human approval before status changes to SUBMITTED
- The `submit` endpoint returns instructions — it does not auto-submit
- Approval requires confirmation in the frontend (browser `confirm()` dialog)

---

## Limitations

- **Job source:** Only LinkedIn via Apify. LinkedIn may rate-limit or block scraping.
- **Posting date accuracy:** Relative dates ("2 hours ago") parsed from Apify results may be approximate.
- **Dynamic application forms:** Each company uses different ATS platforms (Greenhouse, Lever, Workday, etc.). Playwright form-filling works best on standard HTML forms; heavily JavaScript-driven SPAs may not be fully covered.
- **Authentication:** Playwright does not handle SSO, OAuth, or authenticated sessions. Login-required application pages require manual intervention.
- **AI scoring:** Match scores are generated by Claude and may not perfectly reflect hiring manager judgment. The system is designed to be conservative, not optimistic.
- **Rate limits:** Both Apify and Anthropic have rate limits. Large batch analyses may be throttled.
- **Resume quality:** Matching accuracy depends on resume content. A resume with thin descriptions will produce lower-confidence matches.
- **Single candidate:** The system currently supports one candidate profile. Multi-user support is not implemented.

---

## Roadmap

### Completed

- [x] Resume parsing (PDF, DOCX, TXT) via Claude
- [x] LinkedIn job discovery via Apify
- [x] 24-hour time filtering and deduplication
- [x] AI-powered weighted match scoring (11 dimensions)
- [x] Mandatory and nice-to-have gap detection
- [x] Job-specific resume tailoring
- [x] Cover letter generation
- [x] Application queue with status tracking
- [x] Playwright form detection and field filling
- [x] CAPTCHA/MFA/login-wall detection
- [x] Human approval gate (no auto-submit)
- [x] React/TypeScript dashboard with 3 views
- [x] Multi-sheet Excel export and CSV export
- [x] SQLite development database
- [x] PostgreSQL Docker configuration
- [x] Structured JSON logging
- [x] 47 automated tests
- [x] Docker Compose with health checks

### Planned

- [ ] Scheduled recurring job searches (cron-like)
- [ ] Email notifications for strong matches
- [ ] Multiple candidate profile support
- [ ] More job sources (Indeed, Naukri, company career pages)
- [ ] ATS-specific form adapters (Greenhouse, Lever, Workday)
- [ ] Application analytics and follow-up reminders
- [ ] Cloud deployment templates (AWS, GCP)
- [ ] Advanced dashboard with charts and trends
- [ ] Browser session persistence for authenticated sites
- [ ] Match score feedback loop (interview outcomes improve scoring)

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `cd backend && python -m pytest tests/ -v`
5. Ensure all 47 tests pass
6. Commit with a clear message
7. Push to your fork: `git push origin feature/your-feature`
8. Open a Pull Request against `main`

### Code Standards

- Backend: Python 3.12+, type hints, Pydantic models for all API data
- Frontend: TypeScript strict mode, functional components, Tailwind CSS
- Tests: Mock external APIs (Anthropic, Apify), never submit real applications
- Security: Never log secrets, never hardcode API keys

---

## License

Not yet specified.
