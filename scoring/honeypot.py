"""
Honeypot Detection
Identifies ~80 candidates with subtly impossible profiles.
Honeypot rate > 10% in top 100 = disqualification.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import HONEYPOT_EXPERT_ZERO_DURATION_MIN, HONEYPOT_EXPERIENCE_SKILL_RATIO


def is_honeypot(candidate: dict) -> bool:
    """
    Returns True if candidate is likely a honeypot.

    Heuristics:
    1. Expert proficiency with 0 duration_months
    2. Very junior but many expert skills
    3. Career durations don't add up
    4. Assessment scores contradict proficiency
    5. Endorsement anomalies
    """
    skills = candidate.get('skills', [])
    yoe = candidate['profile'].get('years_of_experience', 0)
    signals = candidate.get('redrob_signals', {})
    assessments = signals.get('skill_assessment_scores', {})

    flags = 0

    # 1. Expert skills with 0 duration
    expert_zero_dur = sum(
        1 for s in skills
        if s.get('proficiency') == 'expert' and s.get('duration_months', 1) == 0
    )
    if expert_zero_dur >= HONEYPOT_EXPERT_ZERO_DURATION_MIN:
        flags += 2

    # 2. Very junior with many expert skills
    expert_count = sum(1 for s in skills if s.get('proficiency') == 'expert')
    if yoe < HONEYPOT_EXPERIENCE_SKILL_RATIO and expert_count >= 6:
        flags += 2

    # 3. Career duration anomaly
    career = candidate.get('career_history', [])
    total_career_months = sum(r.get('duration_months', 0) for r in career)
    expected_months = yoe * 12
    if expected_months > 0 and total_career_months > 0:
        ratio = total_career_months / expected_months
        if ratio > 2.0 or ratio < 0.3:
            flags += 1

    # 4. Assessment score contradicts proficiency
    for s in skills:
        skill_name = s.get('name', '')
        if s.get('proficiency') == 'expert':
            for assess_name, assess_score in assessments.items():
                if skill_name.lower() in assess_name.lower() or assess_name.lower() in skill_name.lower():
                    if assess_score < 20:
                        flags += 1
                        break

    # 5. Many expert skills but zero platform endorsements
    total_skill_endorsements = sum(s.get('endorsements', 0) for s in skills)
    platform_endorsements = signals.get('endorsements_received', 0)
    if total_skill_endorsements > 50 and platform_endorsements == 0:
        flags += 1

    return flags >= 2
