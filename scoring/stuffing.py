"""
Keyword-Stuffing Penalty
Detects candidates who pad their profiles with AI keywords they don't possess.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    STUFFING_HIGH_SKILL_COUNT, STUFFING_EXPERT_RATIO,
    STUFFING_TITLE_SKILL_MISMATCH, AI_ML_SKILL_KEYWORDS,
    TITLE_TIER_F,
)


def _count_ai_skills(candidate: dict) -> int:
    count = 0
    for s in candidate.get('skills', []):
        skill_lower = s['name'].lower()
        if any(kw in skill_lower for kw in AI_ML_SKILL_KEYWORDS):
            count += 1
    return count


def _is_f_tier_title(title: str) -> bool:
    t = title.lower().strip()
    return any(pattern in t for pattern in TITLE_TIER_F)


def compute_penalty(candidate: dict) -> float:
    """
    Compute stuffing penalty multiplier (0.3 to 1.0).
    1.0 = no penalty, lower = more penalty.
    """
    skills = candidate.get('skills', [])
    if not skills:
        return 1.0

    penalty = 1.0
    total_skills = len(skills)

    # 1. Too many skills
    if total_skills > STUFFING_HIGH_SKILL_COUNT:
        penalty *= 0.85

    # 2. Too many expert skills
    expert_count = sum(1 for s in skills if s.get('proficiency') == 'expert')
    if total_skills > 0 and expert_count / total_skills > STUFFING_EXPERT_RATIO:
        penalty *= 0.80

    # 3. F-tier title with many AI skills
    title = candidate['profile'].get('current_title', '')
    ai_skill_count = _count_ai_skills(candidate)
    if _is_f_tier_title(title) and ai_skill_count >= STUFFING_TITLE_SKILL_MISMATCH:
        penalty *= 0.65

    # 4. All skills have 0 endorsements but many marked advanced/expert
    advanced_plus = sum(1 for s in skills if s.get('proficiency') in ('advanced', 'expert'))
    zero_endorsement = sum(1 for s in skills if s.get('endorsements', 0) == 0)
    if advanced_plus > 5 and zero_endorsement == total_skills:
        penalty *= 0.75

    # 5. Assessment scores very low despite expert claims
    assessments = candidate.get('redrob_signals', {}).get('skill_assessment_scores', {})
    if assessments:
        low_assessments = sum(1 for v in assessments.values() if v < 30)
        if low_assessments > len(assessments) * 0.7 and expert_count > 3:
            penalty *= 0.80

    return round(max(0.3, penalty), 4)
