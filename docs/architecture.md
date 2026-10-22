# Architecture

## Overview

Monorepo with React (Vite) frontend and FastAPI backend. SQLite for persistence. ML pipeline uses TF-IDF + optional Sentence Transformers.

## Backend Layers

- **API** (`app/api/`): Route handlers, auth dependency injection
- **Services** (`app/services/`): Business logic (upload, match, jobs)
- **ML** (`app/ml/`): Skill dictionary, text extraction, resume parser, matcher
- **Models** (`app/models/`): SQLAlchemy ORM
- **Schemas** (`app/schemas/`): Pydantic request/response validation
- **Core** (`app/core/`): Config, security (JWT, bcrypt), database

## Matching Pipeline

1. Extract text (PyMuPDF / python-docx)
2. Parse sections + dictionary-based skill extraction
3. For a job pair:
   - Required skill coverage (normalized synonyms)
   - Preferred skill coverage
   - TF-IDF or semantic cosine similarity on full text
   - Experience / project relevance via TF-IDF
4. Weighted sum → overall compatibility score (0–100)
5. Persist analysis with component breakdown

**Weights:** required skills 35%, text similarity 30%, preferred 15%, experience 12%, projects 8%.

## Security

- bcrypt password hashing
- JWT Bearer tokens
- Ownership checks on every private resource
- File type/size validation
- CORS restricted to frontend origin
