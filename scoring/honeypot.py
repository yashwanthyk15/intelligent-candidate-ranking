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

    # Honeypot red flag: expert with zero duration = obvious fake
    bad = 0
    for s in skills:
        p = s.get('proficiency')
        d = s.get('duration_months', 1)
        if p == 'expert' and d == 0:
            bad += 1
    if bad >= HONEYPOT_EXPERT_ZERO_DURATION_MIN:
        flags += 2

    # You can't be a 1-year junior with 6 expert skills, come on
    e_cnt = sum(1 for s in skills if s.get('proficiency') == 'expert')
    if yoe < HONEYPOT_EXPERIENCE_SKILL_RATIO and e_cnt >= 6:
        flags += 2

    # Some resumes have overlapping concurrent jobs making them look like they worked 20 years in 5 years
    career = candidate.get('career_history', [])
    tot_m = sum(r.get('duration_months', 0) for r in career)
    exp_m = yoe * 12
    if exp_m > 0 and tot_m > 0:
        r = tot_m / exp_m
        if r > 2.0 or r < 0.3:
            flags += 1

    # Claiming expert but bombing the assessment? Liar.
    for s in skills:
        n = s.get('name', '')
        if s.get('proficiency') == 'expert':
            for a_name, a_score in assessments.items():
                if n.lower() in a_name.lower() or a_name.lower() in n.lower():
                    if a_score < 20:
                        flags += 1
                        break

    # 5. Many expert skills but zero platform endorsements
    total_skill_endorsements = sum(s.get('endorsements', 0) for s in skills)
    platform_endorsements = signals.get('endorsements_received', 0)
    if total_skill_endorsements > 50 and platform_endorsements == 0:
        flags += 1

    return flags >= 2
