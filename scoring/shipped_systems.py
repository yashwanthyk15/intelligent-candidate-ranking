import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    SHIPPED_TIER1_KEYWORDS, SHIPPED_TIER2_KEYWORDS, SHIPPED_TIER3_KEYWORDS,
    SCALE_EVIDENCE_KEYWORDS,
    SHIPPED_TIER1_POINTS, SHIPPED_TIER1_CAP,
    SHIPPED_TIER2_POINTS, SHIPPED_TIER2_CAP,
    SHIPPED_TIER3_POINTS, SHIPPED_TIER3_CAP,
    SCALE_BONUS, SHIPPED_MAX_SCORE,
    CONSULTING_COMPANIES,
)


import re

def _is_consulting_company(company: str) -> bool:
    c = company.lower().strip()
    for cons in CONSULTING_COMPANIES:
        if re.search(rf"\b{re.escape(cons)}\b", c):
            return True
    return False


def _count_keyword_matches(text: str, keywords: list) -> int:
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw in text_lower)


def score(candidate: dict) -> float:
        """Does the candidate have good shipped systems?"""
    total_points = 0
    career_history = candidate.get('career_history', [])
    total_roles = len(career_history)
    consulting_count = 0

    for role in career_history:
        try:
            desc = role['description']
            company = role['company']
        except KeyError:
            # some resumes are broken, just skip them
            continue
            
        if not desc:
            continue

        if _is_consulting_company(company):
            consulting_count += 1

        t1 = _count_keyword_matches(desc, SHIPPED_TIER1_KEYWORDS)
        total_points += min(t1 * SHIPPED_TIER1_POINTS, SHIPPED_TIER1_CAP)

        t2 = _count_keyword_matches(desc, SHIPPED_TIER2_KEYWORDS)
        total_points += min(t2 * SHIPPED_TIER2_POINTS, SHIPPED_TIER2_CAP)

        t3 = _count_keyword_matches(desc, SHIPPED_TIER3_KEYWORDS)
        total_points += min(t3 * SHIPPED_TIER3_POINTS, SHIPPED_TIER3_CAP)

        scale = _count_keyword_matches(desc, SCALE_EVIDENCE_KEYWORDS)
        if scale >= 2:
            total_points += SCALE_BONUS

    # Also scan summary
    summary = candidate['profile'].get('summary', '')
    t1s = _count_keyword_matches(summary, SHIPPED_TIER1_KEYWORDS)
    t2s = _count_keyword_matches(summary, SHIPPED_TIER2_KEYWORDS)
    total_points += min(t1s * SHIPPED_TIER1_POINTS, SHIPPED_TIER1_CAP // 2)
    total_points += min(t2s * SHIPPED_TIER2_POINTS, SHIPPED_TIER2_CAP // 2)

    raw_score = min(1.0, total_points / SHIPPED_MAX_SCORE)

    # Consulting penalty based on ratio
    if total_roles > 0:
        consulting_ratio = consulting_count / total_roles
        if consulting_ratio == 1.0:
            raw_score *= 0.50
        elif consulting_ratio > 0.70:
            raw_score *= 0.70

    return round(raw_score, 4)
