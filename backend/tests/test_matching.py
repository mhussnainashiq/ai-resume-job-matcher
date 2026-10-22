from app.ml.skill_dictionary import extract_skills_from_text, normalize_skill
from app.ml.matcher import compute_match, skill_gap_analysis, tfidf_similarity

def test_normalize_skill():
    assert normalize_skill("Python") == "python"
    assert normalize_skill("ReactJS") == "react"
    assert normalize_skill("unknownskill") == "unknownskill"

def test_extract_skills():
    text = "I have experience with Python, FastAPI, React, and Docker containers."
    skills = extract_skills_from_text(text)
    assert "python" in skills
    assert "fastapi" in skills
    assert "react" in skills
    assert "docker" in skills

def test_tfidf_similarity():
    sim = tfidf_similarity("python fastapi backend api", "python fastapi backend developer")
    assert 0.0 <= sim <= 1.0
    assert sim > 0.3

def test_compute_match():
    result = compute_match(
        resume_text="Experienced Python developer with FastAPI and PostgreSQL. Built REST APIs and used Docker.",
        resume_skills=["python", "fastapi", "postgresql", "docker"],
        experience=[{"title": "Backend Engineer", "description": "Built APIs with FastAPI"}],
        projects=[],
        job_description="Looking for Python FastAPI engineer with Docker and SQL experience.",
        required_skills=["python", "fastapi", "docker"],
        preferred_skills=["postgresql", "aws"],
        method="tfidf",
    )
    assert "overall_score" in result
    assert 0 <= result["overall_score"] <= 100
    assert "python" in result["matched_required_skills"]
    assert result["matching_method"] == "tfidf"

def test_skill_gap():
    gap = skill_gap_analysis(
        resume_skills=["python", "docker"],
        required_skills=["python", "kubernetes"],
        preferred_skills=["aws"],
    )
    assert "python" in gap["demonstrated_skills"]
    assert "kubernetes" in gap["missing_required"]
    assert "aws" in gap["missing_preferred"]
