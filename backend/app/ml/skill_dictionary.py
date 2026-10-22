"""Maintainable skill dictionary with synonyms for robust skill extraction and matching."""

SKILL_SYNONYMS = {
    # Programming Languages
    "python": ["python", "py", "python3", "python 3"],
    "javascript": ["javascript", "js", "ecmascript", "es6", "es2015"],
    "typescript": ["typescript", "ts"],
    "java": ["java", "jdk", "jvm"],
    "c++": ["c++", "cpp", "cplusplus"],
    "c#": ["c#", "csharp", "c sharp", ".net"],
    "go": ["go", "golang"],
    "rust": ["rust"],
    "ruby": ["ruby", "rb"],
    "php": ["php"],
    "swift": ["swift"],
    "kotlin": ["kotlin"],
    "scala": ["scala"],
    "r": ["r programming", "r language"],
    "sql": ["sql", "structured query language", "t-sql", "pl/sql"],

    # Web / Frontend
    "react": ["react", "reactjs", "react.js"],
    "vue": ["vue", "vuejs", "vue.js"],
    "angular": ["angular", "angularjs"],
    "html": ["html", "html5"],
    "css": ["css", "css3", "cascading style sheets"],
    "sass": ["sass", "scss"],
    "tailwind": ["tailwind", "tailwindcss", "tailwind css"],
    "bootstrap": ["bootstrap"],
    "next.js": ["next.js", "nextjs", "next"],
    "redux": ["redux"],

    # Backend / Frameworks
    "node.js": ["node.js", "nodejs", "node"],
    "express": ["express", "expressjs", "express.js"],
    "django": ["django"],
    "flask": ["flask"],
    "fastapi": ["fastapi", "fast api"],
    "spring": ["spring", "spring boot", "springboot"],
    "laravel": ["laravel"],
    "rails": ["rails", "ruby on rails"],

    # Databases
    "postgresql": ["postgresql", "postgres", "psql"],
    "mysql": ["mysql"],
    "mongodb": ["mongodb", "mongo"],
    "redis": ["redis"],
    "elasticsearch": ["elasticsearch", "elastic search"],
    "sqlite": ["sqlite"],
    "oracle": ["oracle", "oracle db"],
    "dynamodb": ["dynamodb", "dynamo"],

    # Cloud / DevOps
    "aws": ["aws", "amazon web services", "amazon aws"],
    "azure": ["azure", "microsoft azure"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "docker": ["docker", "containerization"],
    "kubernetes": ["kubernetes", "k8s"],
    "terraform": ["terraform"],
    "jenkins": ["jenkins"],
    "ci/cd": ["ci/cd", "cicd", "continuous integration", "continuous deployment"],
    "linux": ["linux", "unix"],
    "git": ["git", "github", "gitlab", "version control"],

    # Data / ML
    "machine learning": ["machine learning", "ml", "supervised learning", "unsupervised learning"],
    "deep learning": ["deep learning", "dl", "neural networks", "neural nets"],
    "nlp": ["nlp", "natural language processing", "text processing"],
    "computer vision": ["computer vision", "cv", "image processing"],
    "tensorflow": ["tensorflow", "tf"],
    "pytorch": ["pytorch", "torch"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "spark": ["spark", "apache spark", "pyspark"],
    "hadoop": ["hadoop"],
    "data analysis": ["data analysis", "data analytics", "analytics"],
    "data science": ["data science", "data scientist"],
    "statistics": ["statistics", "statistical analysis"],

    # Soft / Other
    "agile": ["agile", "scrum", "kanban"],
    "project management": ["project management", "pmp"],
    "communication": ["communication", "written communication", "verbal communication"],
    "leadership": ["leadership", "team leadership", "team lead"],
    "problem solving": ["problem solving", "analytical skills"],
}

# Flatten for quick lookup: synonym -> canonical
SYNONYM_TO_CANONICAL = {}
for canonical, synonyms in SKILL_SYNONYMS.items():
    for syn in synonyms:
        SYNONYM_TO_CANONICAL[syn.lower()] = canonical

# All known skills for extraction
ALL_SKILLS = set(SKILL_SYNONYMS.keys()) | set(SYNONYM_TO_CANONICAL.keys())

def normalize_skill(skill: str) -> str:
    """Normalize a skill name to its canonical form if known."""
    s = skill.lower().strip()
    return SYNONYM_TO_CANONICAL.get(s, s)

def extract_skills_from_text(text: str) -> list:
    """Rule-based skill extraction using dictionary matching."""
    if not text:
        return []
    text_lower = text.lower()
    found = set()
    # Sort by length descending to match longer phrases first
    sorted_synonyms = sorted(SYNONYM_TO_CANONICAL.keys(), key=len, reverse=True)
    for syn in sorted_synonyms:
        # Word boundary-ish matching
        if syn in text_lower:
            # Simple check: ensure it's not a substring of a larger word for short skills
            idx = text_lower.find(syn)
            if idx >= 0:
                before = text_lower[idx - 1] if idx > 0 else " "
                after = text_lower[idx + len(syn)] if idx + len(syn) < len(text_lower) else " "
                if (before.isalnum() or after.isalnum()) and len(syn) < 4:
                    continue  # skip short matches inside words
                found.add(SYNONYM_TO_CANONICAL[syn])
    return sorted(list(found))
