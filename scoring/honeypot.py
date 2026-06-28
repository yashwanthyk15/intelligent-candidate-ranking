"""
Honeypot Detection
Implements disqualification filters based on JD requirements.
"""
import sys
import re
from pathlib import Path
from scoring import role_alignment, shipped_systems

from datetime import date
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import CONSULTING_COMPANIES, REFERENCE_DATE, TITLE_TIER_F

def is_honeypot(candidate: dict, ss_score: float = None) -> bool:
    """
    Returns True if candidate is disqualified.
    """
    skills = candidate.get('skills', [])
    career = candidate.get('career_history', [])
    signals = candidate.get('redrob_signals', {})
    profile = candidate.get('profile', {})
    title = profile.get('current_title', '').lower()
    
    # Evaluate shipped systems score once
    if ss_score is None:
        ss_score = shipped_systems.score(candidate)

    # 1. Role Mismatch (The Fake Marketer)
    # Tier F title but claims AI skills
    is_f_tier = any(f_title == title for f_title in TITLE_TIER_F)
    if is_f_tier and len(skills) > 0:
        return True

    # 2. Keyword Stuffing
    # Claims all AI buzzwords (20+ skills) but has basically 0 shipped systems
    if len(skills) >= 20 and ss_score < 0.05:
        return True

    # 3. Consulting Trap
    # Career-long at TCS/Infosys/Wipro without product experience
    if career:
        all_consulting = True
        for c in career:
            comp = c.get('company', '').lower()
            is_cons = any(re.search(rf"\b{re.escape(cons)}\b", comp) for cons in CONSULTING_COMPANIES)
            if not is_cons:
                all_consulting = False
                break
        if all_consulting:
            return True

    # 4. Pure Research
    # Academic background without production deployment
    academic_titles = ['research assistant', 'phd researcher', 'postdoctoral', 'graduate student']
    is_academic = any(t in title for t in academic_titles)
    if is_academic and ss_score < 0.1:
        return True
        
    # 5. LLM-only / LangChain Tourist
    # Career <= 2 years and only lists LLM skills (langchain, openai) without traditional ML
    yoe = profile.get('years_of_experience', 0)
    if yoe <= 2.0:
        skill_names = [s.get('name', '').lower() for s in skills]
        has_llm = any(kw in sn for sn in skill_names for kw in ['langchain', 'openai', 'llm', 'chatgpt'])
        has_trad_ml = any(kw in sn for sn in skill_names for kw in ['scikit', 'xgboost', 'random forest', 'pytorch', 'tensorflow'])
        if has_llm and not has_trad_ml and ss_score < 0.1:
            return True

    # 6. Inactivity
    # Perfect profile but inactive > 6 months (180 days)
    last_active = signals.get('last_active_date', '2000-01-01')
    try:
        parts = last_active.split('-')
        la_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
        if (REFERENCE_DATE - la_date).days > 180:
            return True
    except Exception as e:
        # print("Date parse error for", last_active, e)
        pass

    # 7. Low Engagement
    # <5% recruiter response rate despite high profile completeness
    comp_score = signals.get('profile_completeness_score', 0)
    resp_rate = signals.get('recruiter_response_rate', 1.0)
    if comp_score > 80 and resp_rate < 0.05:
        return True

    # 8. Architect Trap (hasn't written code)
    if 'architect' in title or 'director' in title:
        # Check if they have recent GitHub activity or recent coding skills
        github = signals.get('github_activity_score', -1)
        if github < 10 and ss_score < 0.2:
            return True

    return False
