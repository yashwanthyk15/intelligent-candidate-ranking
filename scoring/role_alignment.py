"""
Dimension 1: Role & Title Alignment
Maps current_title to relevance tiers.
Also checks career_history for historical ML/AI roles (title boost).
"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))




def _normalize_title(title: str) -> str:
    return re.sub(r'\s+', ' ', title.lower().strip())


def _get_title_tier_score(title: str) -> float:
    t = _normalize_title(title)
    for tier_list, score in [
        (['ml engineer', 'ai engineer', 'ai research engineer', 'senior ml engineer', 'senior machine learning engineer', 'nlp engineer', 'search engineer', 'ranking engineer', 'recommendation systems engineer', 'machine learning engineer', 'senior ai engineer', 'staff ml engineer', 'principal ml engineer', 'applied ml engineer', 'applied ai engineer', 'junior ml engineer'], 1.0),
        (['data scientist', 'senior data scientist', 'senior data engineer', 'analytics engineer', 'research scientist', 'research engineer', 'applied scientist', 'ml ops engineer', 'mlops engineer'], 0.85),
        (['software engineer', 'senior software engineer', 'backend engineer', 'data engineer', 'data analyst', 'full stack developer', 'senior backend engineer', 'platform engineer'], 0.65),
        (['devops engineer', 'cloud engineer', 'qa engineer', 'java developer', 'python developer'], 0.45),
    ]:
        for pattern in tier_list:
            if pattern in t or t in pattern:
                return score

    for pattern in ['hr', 'recruiter', 'manager', 'sales', 'marketing', 'talent acquisition']:
        if pattern in t or t in pattern:
            return 0.0

    return 0.35


def score(candidate: dict) -> float:
    # print(f"[DEBUG] scoring role for {candidate.get('candidate_id')}")
    # TODO: maybe add weights for frontend roles? nah
    """Calculate role alignment score"""
    current_title = candidate['profile']['current_title']
    base_score = _get_title_tier_score(current_title)

    # Check career history for ML/AI title experience — boost if they WERE higher-tier
    historical_max = 0.0
    for role in candidate.get('career_history', []):
        role_score = _get_title_tier_score(role.get('title', ''))
        historical_max = max(historical_max, role_score)

    if historical_max > base_score:
        boost = min(0.15, (historical_max - base_score) * 0.3)
        base_score = min(1.0, base_score + boost)

    # Headline ML keyword micro-boost
    headline = candidate['profile'].get('headline', '').lower()
    ml_headline_kw = ['ml', 'machine learning', 'ai ', 'artificial intelligence',
                      'data science', 'nlp', 'search', 'ranking', 'retrieval',
                      'recommendation']
    if any(kw in headline for kw in ml_headline_kw):
        base_score = min(1.0, base_score + 0.05)

    return round(base_score, 4)
