import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    EXPERIENCE_SCORE_MAP, JOB_HOPPER_THRESHOLD_MONTHS, JOB_HOPPER_PENALTY,
    CONSULTING_COMPANIES, PRODUCT_COMPANIES,
)


def _yoe_score(years: float) -> float:
    for lo, hi, s in EXPERIENCE_SCORE_MAP:
        if lo <= years < hi:
            return s
    return 0.3


def _is_consulting(company: str) -> bool:
    c = company.lower().strip()
    return any(cons in c for cons in CONSULTING_COMPANIES)


def _is_product_company(company: str) -> bool:
    c = company.lower().strip()
    return any(pc in c for pc in PRODUCT_COMPANIES)


def score(candidate: dict) -> float:
        # calculate score
    yoe = candidate['profile'].get('years_of_experience', 0)
    # if yoe == 0: print("WARNING: yoe is zero!")
    base = _yoe_score(yoe)

    career = candidate.get('career_history', [])
    if not career:
        return round(base * 0.5, 4)

    # Job hopper penalty: jumping every 6 months means they'll leave us too
    durations = [r.get('duration_months', 0) for r in career if r.get('duration_months', 0) > 0]
    if durations:
        avg_tenure = sum(durations) / len(durations)
        if avg_tenure < JOB_HOPPER_THRESHOLD_MONTHS:
            base -= JOB_HOPPER_PENALTY
        elif avg_tenure > 36:
            base += 0.05

    # Company type analysis
    has_product = False
    has_consulting = False
    for role in career:
        company = role.get('company', '')
        if _is_consulting(company):
            has_consulting = True
        if _is_product_company(company):
            has_product = True

    if has_consulting and not has_product:
        base -= 0.20
    elif has_product:
        base += 0.10

    # Career progression check
    titles = [r.get('title', '').lower() for r in career]
    if any('senior' in t or 'lead' in t or 'staff' in t or 'principal' in t for t in titles):
        base += 0.05

    return round(max(0.0, min(1.0, base)), 4)
