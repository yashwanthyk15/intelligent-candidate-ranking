"""
Dimension 3: Specific Technical Depth
Measures coverage of the 5 core domains from the JD.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import CORE_DOMAINS


def _skill_names_lower(candidate: dict) -> set:
    return {s['name'].lower() for s in candidate.get('skills', [])}


def _career_text(candidate: dict) -> str:
    texts = [candidate['profile'].get('summary', '')]
    for role in candidate.get('career_history', []):
        texts.append(role.get('description', ''))
    return ' '.join(texts).lower()


def score(candidate: dict) -> float:
    """Score technical depth (0.0 to 1.0)."""
    skill_names = _skill_names_lower(candidate)
    career_text = _career_text(candidate)
    assessments = candidate.get('redrob_signals', {}).get('skill_assessment_scores', {})
    assessments_lower = {k.lower(): v for k, v in assessments.items()}

    domain_scores = []

    for domain_name, keywords in CORE_DOMAINS.items():
        in_skills = any(kw in sn for kw in keywords for sn in skill_names)
        in_career = any(kw in career_text for kw in keywords)

        has_strong_assessment = False
        for kw in keywords:
            for assess_skill, assess_score in assessments_lower.items():
                if kw in assess_skill and assess_score > 50:
                    has_strong_assessment = True
                    break
            if has_strong_assessment:
                break

        if in_skills and in_career and has_strong_assessment:
            domain_scores.append(1.0)
        elif in_skills and in_career:
            domain_scores.append(0.8)
        elif in_career:
            domain_scores.append(0.7)
        elif in_skills:
            domain_scores.append(0.4)
        else:
            domain_scores.append(0.0)

    if not domain_scores:
        return 0.0

    avg_score = sum(domain_scores) / len(domain_scores)

    domains_covered = sum(1 for s in domain_scores if s > 0.3)
    if domains_covered >= 5:
        avg_score = min(1.0, avg_score * 1.25)
    elif domains_covered >= 4:
        avg_score = min(1.0, avg_score * 1.15)
    elif domains_covered >= 3:
        avg_score = min(1.0, avg_score * 1.05)

    return round(avg_score, 4)
