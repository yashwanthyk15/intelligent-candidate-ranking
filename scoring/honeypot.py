# Honeypot filter — flags obviously fake/trap candidates for exclusion
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

    if ss_score is None:
        ss_score = shipped_systems.score(candidate)

    # 1. F-tier title with zero production ML evidence
    # The dataset scrambles titles on purpose, so we only flag if
    # both the title is non-tech AND there's no career evidence of ML work.
    is_f_tier = any(f_title == title for f_title in TITLE_TIER_F)
    if is_f_tier and ss_score < 0.05:
        return True

    # 2. Keyword stuffing: 20+ skills listed but no real shipped work
    if len(skills) >= 20 and ss_score < 0.05:
        return True

    # 3. Pure academic without any deployment evidence
    academic_titles = ['research assistant', 'phd researcher', 'postdoctoral', 'graduate student']
    is_academic = any(t in title for t in academic_titles)
    if is_academic and ss_score < 0.1:
        return True

    # 4. LLM tourist: <= 2 YoE, only knows LLM wrappers, no traditional ML
    yoe = profile.get('years_of_experience', 0)
    if yoe <= 2.0:
        skill_names = [s.get('name', '').lower() for s in skills]
        has_llm = any(kw in sn for sn in skill_names for kw in ['langchain', 'openai', 'llm', 'chatgpt'])
        has_trad_ml = any(kw in sn for sn in skill_names for kw in ['scikit', 'xgboost', 'random forest', 'pytorch', 'tensorflow'])
        if has_llm and not has_trad_ml and ss_score < 0.1:
            return True

    # 5. Architect/Director with no code activity and no shipped systems
    if 'architect' in title or 'director' in title:
        github = signals.get('github_activity_score', -1)
        if github < 10 and ss_score < 0.2:
            return True

    return False
