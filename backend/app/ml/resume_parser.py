"""Parse resume text into structured profile using heuristics + skill dictionary."""
import re
from typing import Dict, List, Any, Optional
from app.ml.skill_dictionary import extract_skills_from_text, normalize_skill

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_PATTERN = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}")
SECTION_HEADERS = {
    "summary": ["summary", "professional summary", "profile", "objective", "about me"],
    "experience": ["experience", "work experience", "employment", "professional experience", "work history"],
    "education": ["education", "academic", "qualifications"],
    "skills": ["skills", "technical skills", "core competencies", "technologies", "tech stack"],
    "projects": ["projects", "personal projects", "key projects"],
    "certifications": ["certifications", "certificates", "licenses"],
}

def _find_section(text: str, headers: List[str]) -> Optional[str]:
    text_lower = text.lower()
    for h in headers:
        pattern = re.compile(rf"(?i)(?:^|\n)\s*{re.escape(h)}\s*[:\n]", re.MULTILINE)
        match = pattern.search(text)
        if match:
            start = match.end()
            # Find next section or end
            next_starts = []
            for other_headers in SECTION_HEADERS.values():
                for oh in other_headers:
                    if oh == h:
                        continue
                    m2 = re.compile(rf"(?i)(?:^|\n)\s*{re.escape(oh)}\s*[:\n]", re.MULTILINE).search(text, start)
                    if m2:
                        next_starts.append(m2.start())
            end = min(next_starts) if next_starts else len(text)
            return text[start:end].strip()
    return None

def parse_name(text: str) -> Optional[str]:
    lines = [l.strip() for l in text.split("\n") if l.strip()][:8]
    for line in lines:
        if EMAIL_PATTERN.search(line) or PHONE_PATTERN.search(line):
            continue
        if len(line) < 3 or len(line) > 60:
            continue
        if any(h in line.lower() for headers in SECTION_HEADERS.values() for h in headers):
            continue
        # Likely a name: mostly letters and spaces
        if re.match(r"^[A-Za-z\s.\-']+$", line) and len(line.split()) <= 5:
            return line
    return None

def parse_contact(text: str) -> Dict[str, Optional[str]]:
    email = None
    phone = None
    m = EMAIL_PATTERN.search(text)
    if m:
        email = m.group(0)
    m = PHONE_PATTERN.search(text[:1500])  # look near top
    if m:
        phone = m.group(0)
    return {"email": email, "phone": phone}

def parse_experience(section: Optional[str]) -> List[Dict[str, Any]]:
    if not section:
        return []
    entries = []
    # Split by common patterns like company / title lines
    blocks = re.split(r"\n(?=[A-Z][^\n]{5,80}\n)", section)
    for block in blocks[:10]:
        lines = [l.strip() for l in block.strip().split("\n") if l.strip()]
        if not lines:
            continue
        entry = {"title": lines[0][:120], "company": "", "duration": "", "description": " ".join(lines[1:])[:500]}
        # Try to find duration
        for line in lines:
            if re.search(r"\d{4}", line) and any(m in line.lower() for m in ["present", "current", "-", "–", "to"]):
                entry["duration"] = line[:80]
                break
        entries.append(entry)
    return entries

def parse_education(section: Optional[str]) -> List[Dict[str, Any]]:
    if not section:
        return []
    entries = []
    lines = [l.strip() for l in section.split("\n") if l.strip()]
    for i, line in enumerate(lines[:15]):
        if any(kw in line.lower() for kw in ["bachelor", "master", "phd", "b.s", "m.s", "b.a", "degree", "university", "college", "diploma"]):
            entries.append({"degree": line[:150], "institution": lines[i+1][:100] if i+1 < len(lines) else "", "year": ""})
    return entries[:5]

def parse_projects(section: Optional[str]) -> List[Dict[str, Any]]:
    if not section:
        return []
    entries = []
    blocks = re.split(r"\n(?=[A-Z*•\-])", section)
    for block in blocks[:8]:
        lines = [l.strip() for l in block.strip().split("\n") if l.strip()]
        if lines:
            entries.append({"name": lines[0][:100], "description": " ".join(lines[1:])[:400]})
    return entries

def parse_certifications(section: Optional[str]) -> List[str]:
    if not section:
        return []
    certs = []
    for line in section.split("\n"):
        line = line.strip(" •-*\t")
        if line and len(line) > 3:
            certs.append(line[:120])
    return certs[:10]

def compute_completeness(profile: Dict) -> float:
    score = 0.0
    if profile.get("name"): score += 10
    if profile.get("email") or profile.get("phone"): score += 10
    if profile.get("summary") and len(profile["summary"]) > 50: score += 15
    if profile.get("skills") and len(profile["skills"]) >= 3: score += 20
    if profile.get("experience") and len(profile["experience"]) >= 1: score += 20
    if profile.get("education") and len(profile["education"]) >= 1: score += 15
    if profile.get("projects"): score += 5
    if profile.get("certifications"): score += 5
    return min(100.0, score)

def analyze_strengths_weaknesses(profile: Dict) -> tuple:
    strengths = []
    weaknesses = []
    suggestions = []
    skills = profile.get("skills") or []
    if len(skills) >= 8:
        strengths.append(f"Strong technical skill set ({len(skills)} skills identified)")
    elif len(skills) < 3:
        weaknesses.append("Few technical skills extracted — consider listing skills explicitly")
        suggestions.append("Add a dedicated Skills section with relevant technologies")
    if profile.get("experience") and len(profile["experience"]) >= 2:
        strengths.append("Multiple work experience entries present")
    else:
        weaknesses.append("Limited work experience details")
        suggestions.append("Expand work experience with quantifiable achievements")
    if profile.get("summary") and len(profile.get("summary", "")) > 80:
        strengths.append("Professional summary is present")
    else:
        weaknesses.append("Missing or weak professional summary")
        suggestions.append("Write a concise 3–4 sentence professional summary tailored to target roles")
    if not profile.get("projects"):
        suggestions.append("Add 1–2 relevant projects with technologies used and outcomes")
    if not profile.get("education"):
        weaknesses.append("Education section not clearly identified")
    return strengths, weaknesses, suggestions

def parse_resume(text: str) -> Dict[str, Any]:
    """Main entry: parse full resume text into structured profile."""
    if not text or len(text.strip()) < 30:
        return {
            "name": None, "email": None, "phone": None, "summary": None,
            "skills": [], "experience": [], "education": [], "projects": [],
            "certifications": [], "completeness_score": 0.0,
            "strengths": [], "weaknesses": ["Resume text too short or empty"],
            "suggestions": ["Upload a complete resume with clear sections"]
        }

    contact = parse_contact(text)
    name = parse_name(text)
    summary = _find_section(text, SECTION_HEADERS["summary"])
    exp_section = _find_section(text, SECTION_HEADERS["experience"])
    edu_section = _find_section(text, SECTION_HEADERS["education"])
    skills_section = _find_section(text, SECTION_HEADERS["skills"])
    proj_section = _find_section(text, SECTION_HEADERS["projects"])
    cert_section = _find_section(text, SECTION_HEADERS["certifications"])

    # Skills: from skills section + whole text
    skills = extract_skills_from_text(skills_section or "")
    skills_from_body = extract_skills_from_text(text)
    all_skills = sorted(set(skills + skills_from_body))

    profile = {
        "name": name,
        "email": contact["email"],
        "phone": contact["phone"],
        "summary": (summary[:800] if summary else None),
        "skills": all_skills,
        "experience": parse_experience(exp_section),
        "education": parse_education(edu_section),
        "projects": parse_projects(proj_section),
        "certifications": parse_certifications(cert_section),
    }
    profile["completeness_score"] = compute_completeness(profile)
    strengths, weaknesses, suggestions = analyze_strengths_weaknesses(profile)
    profile["strengths"] = strengths
    profile["weaknesses"] = weaknesses
    profile["suggestions"] = suggestions
    return profile
