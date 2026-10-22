"""Resume-Job matching engine: TF-IDF baseline + optional Sentence Transformers semantic matching."""
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.ml.skill_dictionary import normalize_skill, extract_skills_from_text

# Lazy-loaded semantic model
_semantic_model = None
_semantic_available = None

def _load_semantic_model():
    global _semantic_model, _semantic_available
    if _semantic_available is not None:
        return _semantic_model
    try:
        from sentence_transformers import SentenceTransformer
        from app.core.config import settings
        _semantic_model = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)
        _semantic_available = True
        return _semantic_model
    except Exception as e:
        print(f"[WARN] Semantic model unavailable, falling back to TF-IDF only: {e}")
        _semantic_available = False
        _semantic_model = None
        return None

def is_semantic_available() -> bool:
    _load_semantic_model()
    return bool(_semantic_available)

def _normalize_skills_list(skills: List[str]) -> List[str]:
    return sorted(set(normalize_skill(s) for s in skills if s))

def skill_coverage(resume_skills: List[str], required: List[str]) -> Tuple[float, List[str], List[str]]:
    """Return coverage ratio, matched, missing."""
    rset = set(_normalize_skills_list(resume_skills))
    req = _normalize_skills_list(required)
    if not req:
        return 1.0, [], []
    matched = [s for s in req if s in rset]
    missing = [s for s in req if s not in rset]
    return len(matched) / len(req), matched, missing

def tfidf_similarity(text_a: str, text_b: str) -> float:
    if not text_a.strip() or not text_b.strip():
        return 0.0
    try:
        vec = TfidfVectorizer(stop_words="english", max_features=5000, ngram_range=(1, 2))
        matrix = vec.fit_transform([text_a, text_b])
        sim = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        return float(max(0.0, min(1.0, sim)))
    except Exception:
        return 0.0

def semantic_similarity(text_a: str, text_b: str) -> float:
    model = _load_semantic_model()
    if model is None:
        return tfidf_similarity(text_a, text_b)  # fallback
    try:
        embeddings = model.encode([text_a[:2000], text_b[:2000]], convert_to_numpy=True)
        sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        return float(max(0.0, min(1.0, sim)))
    except Exception:
        return tfidf_similarity(text_a, text_b)

def experience_relevance(experience: List[Dict], job_text: str) -> float:
    if not experience:
        return 0.0
    exp_text = " ".join(
        f"{e.get('title', '')} {e.get('company', '')} {e.get('description', '')}"
        for e in experience
    )
    return tfidf_similarity(exp_text, job_text)

def project_relevance(projects: List[Dict], job_text: str) -> float:
    if not projects:
        return 0.0
    proj_text = " ".join(
        f"{p.get('name', '')} {p.get('description', '')}" for p in projects
    )
    return tfidf_similarity(proj_text, job_text)

def compute_match(
    resume_text: str,
    resume_skills: List[str],
    experience: List[Dict],
    projects: List[Dict],
    job_description: str,
    required_skills: List[str],
    preferred_skills: List[str],
    method: str = "hybrid",
) -> Dict[str, Any]:
    """
    Compute explainable compatibility score.
    Components (weights documented):
      - required_skill_coverage: 0.35
      - preferred_skill_coverage: 0.15
      - semantic/tfidf text similarity: 0.30
      - experience_relevance: 0.12
      - project_relevance: 0.08
    Overall is weighted sum, scaled 0-100.
    This is a compatibility heuristic, NOT a hiring probability.
    """
    req_cov, matched_req, missing_req = skill_coverage(resume_skills, required_skills)
    pref_cov, matched_pref, missing_pref = skill_coverage(resume_skills, preferred_skills)

    # Text similarity
    if method == "semantic" or (method == "hybrid" and is_semantic_available()):
        text_sim = semantic_similarity(resume_text, job_description)
        used_method = "semantic" if is_semantic_available() else "tfidf"
    else:
        text_sim = tfidf_similarity(resume_text, job_description)
        used_method = "tfidf"

    exp_rel = experience_relevance(experience, job_description)
    proj_rel = project_relevance(projects, job_description)

    weights = {
        "required_skill_coverage": 0.35,
        "preferred_skill_coverage": 0.15,
        "semantic_similarity": 0.30,
        "experience_relevance": 0.12,
        "project_relevance": 0.08,
    }
    component_scores = {
        "required_skill_coverage": round(req_cov * 100, 1),
        "preferred_skill_coverage": round(pref_cov * 100, 1),
        "semantic_similarity": round(text_sim * 100, 1),
        "experience_relevance": round(exp_rel * 100, 1),
        "project_relevance": round(proj_rel * 100, 1),
    }
    overall = (
        weights["required_skill_coverage"] * req_cov
        + weights["preferred_skill_coverage"] * pref_cov
        + weights["semantic_similarity"] * text_sim
        + weights["experience_relevance"] * exp_rel
        + weights["project_relevance"] * proj_rel
    ) * 100
    overall = round(min(100.0, max(0.0, overall)), 1)

    # Strengths & suggestions
    strengths = []
    suggestions = []
    evidence = []
    if req_cov >= 0.7:
        strengths.append(f"Strong coverage of required skills ({len(matched_req)}/{len(required_skills or [1])})")
    if matched_req:
        evidence.append(f"Matched required skills: {', '.join(matched_req[:8])}")
    if missing_req:
        suggestions.append(f"Consider developing or highlighting: {', '.join(missing_req[:5])}")
    if text_sim >= 0.4:
        strengths.append("Resume language aligns well with the job description")
    elif text_sim < 0.2:
        suggestions.append("Tailor resume wording more closely to the job description keywords")
    if exp_rel >= 0.3:
        strengths.append("Relevant work experience detected")
        evidence.append("Experience section shows topical overlap with the role")
    if proj_rel >= 0.25:
        strengths.append("Projects demonstrate relevant capabilities")
    if not strengths:
        strengths.append("Baseline compatibility computed; review missing skills for improvement")

    return {
        "overall_score": overall,
        "component_scores": component_scores,
        "matched_required_skills": matched_req,
        "missing_required_skills": missing_req,
        "matched_preferred_skills": matched_pref,
        "missing_preferred_skills": missing_pref,
        "strengths": strengths,
        "suggestions": suggestions,
        "evidence": evidence,
        "matching_method": used_method,
    }

def skill_gap_analysis(
    resume_skills: List[str],
    required_skills: List[str],
    preferred_skills: List[str],
) -> Dict[str, Any]:
    rset = set(_normalize_skills_list(resume_skills))
    req = _normalize_skills_list(required_skills)
    pref = _normalize_skills_list(preferred_skills)
    demonstrated = sorted(rset & (set(req) | set(pref)))
    missing_req = [s for s in req if s not in rset]
    missing_pref = [s for s in pref if s not in rset]
    # Simple transferable: skills that share a category keyword
    transferable = []
    for s in rset:
        for m in missing_req:
            if any(part in s for part in m.split()) or any(part in m for part in s.split()):
                if s not in transferable:
                    transferable.append(s)
    learning = missing_req[:5] + [p for p in missing_pref if p not in missing_req][:3]
    return {
        "demonstrated_skills": demonstrated,
        "missing_required": missing_req,
        "missing_preferred": missing_pref,
        "transferable_skills": transferable[:5],
        "learning_priorities": learning[:8],
    }
