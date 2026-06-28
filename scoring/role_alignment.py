import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))



from config import TITLE_TIER_S, TITLE_TIER_A, TITLE_TIER_B, TITLE_TIER_C, TITLE_TIER_F

def _normalize_title(title: str) -> str:
    return re.sub(r'\s+', ' ', title.lower().strip())


def _get_title_tier_score(title: str) -> float:
    t = _normalize_title(title)
    for tier_list, score in [
        (TITLE_TIER_S, 1.0),
        (TITLE_TIER_A, 0.85),
        (TITLE_TIER_B, 0.65),
        (TITLE_TIER_C, 0.45),
    ]:
        for pattern in tier_list:
            if pattern in t or t in pattern:
                return score

    for pattern in TITLE_TIER_F:
        if pattern in t or t in pattern:
            return 0.0

    return 0.35


def score(candidate: dict) -> float:
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
