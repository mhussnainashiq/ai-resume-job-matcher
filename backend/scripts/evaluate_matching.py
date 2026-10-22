"""
Small evaluation script comparing TF-IDF vs semantic matching.
Uses synthetic labeled pairs. Expand the dataset for more reliable metrics.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.ml.matcher import compute_match, is_semantic_available

PAIRS = [
    (
        "Senior Python developer with FastAPI, PostgreSQL, Docker. Built REST APIs for 5 years.",
        ["python", "fastapi", "postgresql", "docker"],
        "Looking for Python FastAPI engineer with Docker and SQL.",
        ["python", "fastapi", "docker"],
        ["postgresql"],
        True,
    ),
    (
        "Frontend React developer. JavaScript, CSS, HTML. Built SPAs.",
        ["javascript", "react", "css", "html"],
        "Need ML engineer with PyTorch and NLP experience.",
        ["python", "pytorch", "nlp"],
        ["tensorflow"],
        False,
    ),
    (
        "Data analyst skilled in SQL, Python, pandas, statistics and dashboards.",
        ["sql", "python", "pandas", "statistics"],
        "Data Analyst role requiring SQL, Python, and data analysis skills.",
        ["sql", "python", "data analysis"],
        ["statistics"],
        True,
    ),
    (
        "DevOps engineer: Kubernetes, Docker, AWS, Terraform, CI/CD pipelines.",
        ["kubernetes", "docker", "aws", "terraform", "ci/cd"],
        "DevOps position needing Docker, K8s and cloud experience.",
        ["docker", "kubernetes", "aws"],
        ["terraform"],
        True,
    ),
    (
        "Java Spring Boot backend developer with MySQL.",
        ["java", "spring", "mysql"],
        "React frontend developer needed for UI work.",
        ["react", "javascript", "css"],
        ["typescript"],
        False,
    ),
]

def main():
    print("=== Matching Evaluation (synthetic fixtures) ===\n")
    print(f"Semantic model available: {is_semantic_available()}\n")
    correct_tfidf = 0
    correct_sem = 0
    threshold = 40.0
    for i, (rtext, rskills, jdesc, req, pref, label) in enumerate(PAIRS):
        res_tf = compute_match(rtext, rskills, [], [], jdesc, req, pref, method="tfidf")
        pred_tf = res_tf["overall_score"] >= threshold
        if pred_tf == label:
            correct_tfidf += 1
        res_sm = compute_match(rtext, rskills, [], [], jdesc, req, pref, method="semantic")
        pred_sm = res_sm["overall_score"] >= threshold
        if pred_sm == label:
            correct_sem += 1
        print(f"Pair {i+1}: label={'relevant' if label else 'irrelevant'}")
        print(f"  TF-IDF score={res_tf['overall_score']} pred={'rel' if pred_tf else 'irrel'}")
        print(f"  Semantic score={res_sm['overall_score']} pred={'rel' if pred_sm else 'irrel'}")
        print()
    n = len(PAIRS)
    print(f"TF-IDF accuracy: {correct_tfidf}/{n} = {correct_tfidf/n:.0%}")
    print(f"Semantic accuracy: {correct_sem}/{n} = {correct_sem/n:.0%}")
    print("\nLimitations: only 5 synthetic pairs; expand with real labeled data.")

if __name__ == "__main__":
    main()
