# AI Job Application Copilot

Automated job discovery, matching, and application preparation for DevOps/DevSecOps roles. Never submits without human approval.

## Architecture

```
React/TypeScript UI → FastAPI Backend → SQLite/PostgreSQL
                         ↓
              Claude API (matching, tailoring, cover letters)
              Apify API (LinkedIn job discovery)
              Playwright (form filling, human review gate)
```

## Prerequisites

- Python 3.12+
- Node.js 20+
- Anthropic API key (Claude)
- Apify API token
- Docker & Docker Compose (for production)

## Quick Start

### Local Development

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env   # Add your API keys
uvicorn app.main:app --reload --port 8000

# In another terminal:
cd frontend
npm install && npm run dev
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- API docs: `http://localhost:8000/docs`

### Docker (Production)

```bash
cp .env.example .env   # Add your API keys
docker compose up --build
```

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `ANTHROPIC_API_KEY` | Claude API key | (required) |
| `APIFY_API_TOKEN` | Apify API token | (required for job search) |
| `APIFY_ACTOR_ID` | LinkedIn Jobs actor | `apify/linkedin-jobs-scraper` |
| `DATABASE_URL` | Database connection | `sqlite:///./jobs.db` |
| `JOB_MATCH_THRESHOLD` | Minimum match to queue | `85` |
| `JOB_SEARCH_HOURS` | Only jobs posted within N hours | `24` |
| `PLAYWRIGHT_HEADLESS` | Run browser headless | `true` |
| `TARGET_COUNTRY` | Job search country | `India` |

## Workflow

1. **Upload Resume** — PDF/DOCX/TXT parsed by Claude into structured profile
2. **Search Jobs** — Apify fetches LinkedIn jobs for 15 DevOps/DevSecOps roles across 10 Indian cities
3. **Filter** — Only jobs posted within 24 hours, deduplicated
4. **Match** — Claude analyzes each JD vs resume with weighted scoring (AWS 15%, K8s 15%, Terraform 12%, CI/CD 12%, DevSecOps 12%, etc.)
5. **Queue** — Jobs scoring 85%+ with no mandatory gaps auto-queued
6. **Tailor** — Generate job-specific resume (Phase 2)
7. **Cover Letter** — Generate concise letter referencing resume evidence (Phase 2)
8. **Review** — Human reviews match, resume, cover letter
9. **Approve** — Explicit approval required before any submission
10. **Playwright** — Open application URL, detect CAPTCHA/MFA, fill verified fields only (Phase 3)
11. **Export** — Excel with Top Jobs, Candidate Profile, Skill Match, Application Tracker sheets

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/resume/upload` | Upload and parse resume |
| GET | `/api/resume/profile` | Get candidate profile |
| POST | `/api/jobs/search` | Search LinkedIn via Apify |
| GET | `/api/jobs` | List jobs (filter by status, min_score) |
| GET | `/api/jobs/{id}` | Get job details |
| POST | `/api/jobs/analyze` | Analyze all discovered jobs |
| POST | `/api/jobs/{id}/analyze-single` | Analyze single job |
| POST | `/api/jobs/{id}/tailor-resume` | Generate tailored resume |
| POST | `/api/jobs/{id}/cover-letter` | Generate cover letter |
| GET | `/api/applications` | List applications |
| POST | `/api/applications/{id}/prepare` | Prepare for review |
| POST | `/api/applications/{id}/approve` | Approve for submission |
| POST | `/api/applications/{id}/cancel` | Cancel application |
| POST | `/api/applications/{id}/fill-form` | Playwright form analysis |
| POST | `/api/applications/{id}/submit` | Submit (after approval) |
| GET | `/api/dashboard` | Dashboard statistics |
| GET | `/api/export/excel` | Download Excel |
| GET | `/api/export/csv` | Download CSV |

## Database

SQLite for development, PostgreSQL for Docker/production.

### Tables

- **jobs** — Discovered and analyzed job postings with match scores
- **applications** — Application tracking with workflow status
- **candidate_profiles** — Parsed resume data with skill categories

### Statuses

```
DISCOVERED → ANALYZING → MATCHED → QUEUED → READY_FOR_REVIEW → SUBMITTED
```

## Target Search Criteria

**Roles:** DevOps Engineer, Senior DevOps, DevSecOps, Platform Engineer, SRE, Kubernetes Platform Engineer, Infrastructure Engineer (15 total)

**Locations:** Remote India, Hyderabad, Bangalore, Pune, Chennai, Mumbai, Gurgaon, Noida, Delhi NCR

## Testing

```bash
cd backend
source .venv/bin/activate
python -m pytest tests/ -v
```

47 tests covering resume parsing, deduplication, job matching, API endpoints, Excel export, Playwright form handling, and human approval gate.

## Security

- Never fabricates resume information
- Never submits applications without explicit human approval
- Never bypasses CAPTCHA/MFA/anti-bot controls
- API keys in environment variables only, never logged
- Structured logging without secrets or credentials

## Troubleshooting

- **Apify fails:** Check `APIFY_API_TOKEN` in `.env`
- **Claude fails:** Check `ANTHROPIC_API_KEY` in `.env`
- **No jobs found:** Ensure API keys are valid, try reducing `JOB_SEARCH_HOURS`
- **Low match scores:** Check resume has relevant DevOps/Cloud experience
- **Playwright errors:** Run `playwright install chromium`
