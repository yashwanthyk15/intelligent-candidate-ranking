import sys
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import REFERENCE_DATE, BEHAVIORAL_WEIGHTS, RECENCY_SCORES, NOTICE_SCORES


def _days_since_active(last_active_str: str) -> int:
    try:
        parts = last_active_str.split('-')
        la_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
        return (REFERENCE_DATE - la_date).days
    except (ValueError, IndexError):
        return 999


def _score_from_thresholds(value: float, thresholds: list) -> float:
    for threshold, s in thresholds:
        if value <= threshold:
            return s
    return thresholds[-1][1] if thresholds else 0.0


def score(candidate: dict) -> float:
        """Calculate behavioral score"""
    signals = candidate.get('redrob_signals', {})

    days_ago = _days_since_active(signals.get('last_active_date', '2020-01-01'))
    recency_score = _score_from_thresholds(days_ago, RECENCY_SCORES)

    otw_score = 1.0 if signals.get('open_to_work_flag', False) else 0.30

    rr = signals.get('recruiter_response_rate', 0.0)
    if rr > 0.7: rr_score = 1.0
    elif rr > 0.5: rr_score = 0.80
    elif rr > 0.3: rr_score = 0.55
    elif rr > 0.1: rr_score = 0.30
    else: rr_score = 0.10

    notice = signals.get('notice_period_days', 90)
    notice_score = _score_from_thresholds(notice, NOTICE_SCORES)

    # Market validation: recruiter interest signals
    saved = signals.get('saved_by_recruiters_30d', 0)
    views = signals.get('profile_views_received_30d', 0)
    search_app = signals.get('search_appearance_30d', 0)
    saved_norm = min(1.0, saved / 15.0)
    views_norm = min(1.0, views / 30.0)
    search_norm = min(1.0, search_app / 300.0)
    market_score = saved_norm * 0.4 + views_norm * 0.3 + search_norm * 0.3

    w = BEHAVIORAL_WEIGHTS
    final = (
        recency_score * w['recency'] +
        otw_score * w['open_to_work'] +
        rr_score * w['response_rate'] +
        notice_score * w['notice_period'] +
        market_score * w['market_validation']
    )

    return round(max(0.0, min(1.0, final)), 4)
