# AI Resume & Job Matching System

A complete full-stack portfolio project that uploads resumes (PDF/DOCX), extracts structured information with NLP, matches them against job descriptions using **TF-IDF + cosine similarity** and optional **Sentence Transformers** semantic embeddings, surfaces skill gaps, recommends jobs, and tracks applications.

> Scores are **compatibility heuristics**, not hiring probabilities.

## Features

- **Authentication**: Register / login / JWT / protected routes / ownership checks
- **Resume upload & parsing**: PDF (PyMuPDF) and DOCX (python-docx); skills, experience, education, projects, certifications
- **AI analyzer**: Completeness score, strengths, weaknesses, actionable suggestions
- **Job manager**: Create / edit / delete own jobs; sample jobs pre-seeded
- **Matching engine**: Explainable component scores (required skills, preferred skills, text similarity, experience, projects)
- **Skill gap analysis**: Demonstrated / missing / transferable / learning priorities
- **Recommendations**: Rank jobs by compatibility
- **Application tracker**: Applied → Interview → Offer → Rejected → Withdrawn
- **Dashboard**: Real stats from stored records, charts (Recharts)
- **Security**: bcrypt, JWT, file validation, CORS, no hardcoded secrets

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, Vite, React Router, Axios, Lucide icons, Recharts, custom CSS |
| Backend | Python 3.10+, FastAPI, SQLAlchemy, Pydantic, SQLite |
| Auth | JWT (python-jose), passlib/bcrypt |
| ML/NLP | scikit-learn (TF-IDF), sentence-transformers (optional), skill dictionary |
| Docs | PyMuPDF, python-docx |

## Project Structure

```
ai-resume-job-matcher/
├── frontend/                 # React + Vite
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── layouts/
│       ├── context/
│       ├── services/
│       └── styles/
├── backend/
│   ├── app/
│   │   ├── api/              # Route modules
│   │   ├── core/             # Config, security, DB
│   │   ├── models/           # SQLAlchemy
│   │   ├── schemas/          # Pydantic
│   │   ├── services/         # Business logic
│   │   ├── ml/               # Parser, matcher, skills
│   │   └── main.py
│   ├── tests/
│   ├── scripts/evaluate_matching.py
│   └── requirements.txt
├── data/
├── docs/architecture.md
├── README.md
└── .env.example
```

## Installation (Windows PowerShell)

### 1. Prerequisites

```powershell
python --version    # 3.10+
node --version      # 18+
npm --version
git --version
```

### 2. Clone / enter project

```powershell
cd ai-resume-job-matcher
```

### 3. Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy ..\.env.example .env
# Edit .env and set SECRET_KEY (optional for local): openssl rand -hex 32
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API docs: http://127.0.0.1:8000/docs  
Health: http://127.0.0.1:8000/api/health

### 4. Frontend (new terminal)

```powershell
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

### 5. Tests

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pytest tests/ -v
python scripts/evaluate_matching.py
```

## ML Methodology

1. **Skill extraction**: Maintainable synonym dictionary → canonical skill names; substring matching with short-word safeguards.
2. **TF-IDF baseline**: `TfidfVectorizer` (1–2 grams, English stop words) + cosine similarity on resume vs job text.
3. **Semantic (optional)**: `sentence-transformers/all-MiniLM-L6-v2`. If download fails, system falls back to TF-IDF and continues.
4. **Overall score**: Weighted combination of required coverage (35%), preferred (15%), text sim (30%), experience (12%), projects (8%). Normalized to 0–100.

## Evaluation

Run `python backend/scripts/evaluate_matching.py` for accuracy on 5 synthetic labeled pairs.  
**Limitations**: tiny fixture set; labels are heuristic. Expand with real annotated pairs for meaningful metrics.

## API Overview

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/auth/register | Register |
| POST | /api/auth/login | Login (form) |
| GET | /api/auth/me | Current user |
| POST | /api/resumes/upload | Upload PDF/DOCX |
| GET | /api/resumes | List resumes |
| GET/DELETE | /api/resumes/{id} | Detail / delete |
| POST/GET | /api/jobs | Create / list jobs |
| GET/PUT/DELETE | /api/jobs/{id} | Job CRUD |
| POST | /api/matching/analyze | Run match |
| GET | /api/matching/skill-gap | Skill gaps |
| GET | /api/matching/recommendations | Ranked jobs |
| GET | /api/matching/history | Past analyses |
| POST/GET | /api/applications/saved | Save jobs |
| POST/GET/PUT/DELETE | /api/applications/track | Application tracker |
| GET | /api/dashboard/stats | Dashboard metrics |

## Security Notes

- Never commit `.env` or `uploads/`
- Change `SECRET_KEY` for any non-local deployment
- Sample jobs are labeled; they are not real vacancies
- Resume text is stored only for the owning user and used for matching

## Limitations

- Resume parsing is heuristic (section headers vary widely)
- Semantic model requires ~90MB download on first use
- Evaluation set is intentionally small and synthetic
- No generative LLM for rewrite suggestions (by design — no paid API)

## Future Enhancements

- Multi-file batch matching
- Export match reports as PDF
- Improved section detection with layout-aware parsers
- Larger labeled evaluation suite
- OAuth providers

## License

MIT — for educational / portfolio use.
