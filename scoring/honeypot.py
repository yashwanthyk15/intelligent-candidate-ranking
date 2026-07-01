# Honeypot filter — flags candidates with impossible/fabricated profiles
import sys
from pathlib import Path
from scoring import shipped_systems

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import TITLE_TIER_F

def is_honeypot(candidate: dict, ss_score: float = None) -> bool:
    skills = candidate.get('skills', [])
    signals = candidate.get('redrob_signals', {})
    profile = candidate.get('profile', {})
    title = profile.get('current_title', '').lower()
    career = candidate.get('career_history', [])
    yoe = profile.get('years_of_experience', 0)

    if ss_score is None:
        ss_score = shipped_systems.score(candidate)

    # 1. Impossible tenure: a single role duration exceeds total stated YoE.
    #    Spec example: "8 years of experience at a company founded 3 years ago."
    if yoe > 0:
        for role in career:
            dur = role.get('duration_months', 0)
            if dur > 0 and dur > (yoe * 12 + 24):  # 24-month tolerance
                return True

    # 2. LLM tourist: very junior, only knows LLM wrappers, zero real ML career
    if yoe <= 1.2:
        skill_names = [s.get('name', '').lower() for s in skills]
        has_llm = any(kw in sn for sn in skill_names for kw in ['langchain', 'openai', 'llm', 'chatgpt'])
        has_trad_ml = any(kw in sn for sn in skill_names for kw in ['scikit', 'xgboost', 'random forest', 'pytorch', 'tensorflow'])
        if has_llm and not has_trad_ml and ss_score == 0.0:
            return True

    # 3. Architect/Director who hasn't written code and has no shipped systems
    if 'architect' in title or 'director' in title:
        github = signals.get('github_activity_score', -1)
        if github < 10 and ss_score == 0.0:
            return True

    return False
