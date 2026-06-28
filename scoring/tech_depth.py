import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import CORE_DOMAINS

def _skill_names_lower(candidate: dict) -> set:
    return {s['name'].lower() for s in candidate.get('skills', [])}

def _career_text(candidate: dict) -> str:
    texts = [candidate['profile'].get('summary', '')]
    for role in candidate.get('career_history', []):
        texts.append(role.get('description', ''))
    return ' '.join(texts).lower()

def score(candidate: dict) -> float:
    # Require production evidence (career_text) and skills across 5 domains
    skill_names = _skill_names_lower(candidate)
    career_text = _career_text(candidate)
    assessments = candidate.get('redrob_signals', {}).get('skill_assessment_scores', {})
    assessments_lower = {k.lower(): v for k, v in assessments.items()}

    # We want all 5 critical domains
    must_haves = ['embeddings_retrieval', 'vector_db_search', 'ranking_systems', 'evaluation_frameworks', 'python_production']
    
    domain_scores = []
    
    for domain_name in must_haves:
        keywords = CORE_DOMAINS[domain_name]
        in_skills = any(kw in sn for kw in keywords for sn in skill_names)
        in_career = any(kw in career_text for kw in keywords)

        has_strong_assessment = False
        for kw in keywords:
            for assess_skill, assess_score in assessments_lower.items():
                if kw in assess_skill and assess_score > 50:
                    has_strong_assessment = True
                    break
            if has_strong_assessment:
                break

        # Scoring logic: Must have production evidence (career_text) and skills
        if in_skills and in_career and has_strong_assessment:
            domain_scores.append(1.0)
        elif in_skills and in_career:
            domain_scores.append(0.8)
        elif in_career:
            # Experience over keywords!
            domain_scores.append(0.7)
        elif in_skills:
            # Just a keyword without proof
            domain_scores.append(0.4)
        else:
            domain_scores.append(0.0)

    # average across all domains
    if not domain_scores:
        return 0.0
        
    depth_score = sum(domain_scores) / len(domain_scores)
    return round(depth_score, 4)
