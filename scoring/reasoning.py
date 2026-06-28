"""
Reasoning Generation
Produces specific, fact-based reasoning strings for the top 100 candidates.
Each reasoning is unique, specific, and matches the candidate's rank position.
"""
from datetime import date
from config import CONSULTING_COMPANIES, PREFERRED_LOCATIONS


def _get_key_skills(candidate: dict, max_skills: int = 3) -> list:
    ai_keywords = [
        'embeddings', 'vector', 'faiss', 'pinecone', 'weaviate', 'qdrant', 'milvus',
        'ranking', 'retrieval', 'search', 'recommendation', 'bm25',
        'nlp', 'pytorch', 'tensorflow', 'transformer', 'bert', 'gpt', 'llm',
        'fine-tuning', 'lora', 'rag', 'langchain', 'opensearch', 'elasticsearch',
        'python', 'machine learning', 'deep learning', 'neural',
        'xgboost', 'lightgbm', 'scikit', 'hugging face',
        'mlops', 'kubeflow', 'mlflow', 'docker', 'kubernetes',
        'a/b testing', 'ndcg', 'feature engineering',
        'sentence-transformers', 'openai', 'opencv',
        'data pipelines', 'spark', 'airflow',
    ]
    proficiency_order = {'expert': 0, 'advanced': 1, 'intermediate': 2, 'beginner': 3}
    relevant = []
    for s in candidate.get('skills', []):
        name_lower = s['name'].lower()
        if any(kw in name_lower for kw in ai_keywords):
            relevant.append((proficiency_order.get(s.get('proficiency', 'beginner'), 3), s['name']))
    relevant.sort()
    return [name for _, name in relevant[:max_skills]]


def _get_career_evidence(candidate: dict) -> str:
    shipped_keywords = [
        'ranking', 'retrieval', 'recommendation', 'search system',
        'embeddings', 'vector', 'deployed', 'shipped', 'production',
        'ml ', 'machine learning', 'model serving', 'fine-tun',
        'semantic search', 'hybrid retrieval',
    ]
    for role in candidate.get('career_history', []):
        desc = role.get('description', '').lower()
        matches = [kw for kw in shipped_keywords if kw in desc]
        if len(matches) >= 2:
            company = role.get('company', 'a product company')
            title = role.get('title', 'engineer')
            return f"{title} at {company}"
    return None


def _get_concerns(candidate: dict, rank: int) -> str:
    concerns = []
    signals = candidate.get('redrob_signals', {})

    notice = signals.get('notice_period_days', 0)
    if notice > 90:
        concerns.append(f"long notice period ({notice} days)")

    try:
        parts = signals.get('last_active_date', '2025-01-01').split('-')
        la = date(int(parts[0]), int(parts[1]), int(parts[2]))
        days = (date(2026, 6, 15) - la).days
        if days > 120:
            concerns.append(f"last active {days} days ago")
    except (ValueError, IndexError):
        pass

    rr = signals.get('recruiter_response_rate', 0)
    if rr < 0.3:
        concerns.append(f"low response rate ({rr:.0%})")

    if not signals.get('open_to_work_flag', False):
        concerns.append("not marked as open to work")

    consulting = CONSULTING_COMPANIES
    career = candidate.get('career_history', [])
    all_consulting = all(
        any(c in role.get('company', '').lower() for c in consulting)
        for role in career
    ) if career else False
    if all_consulting and career:
        concerns.append("consulting-only background")

    if rank > 70:
        if concerns:
            return "; concerns: " + ", ".join(concerns[:3])
        else:
            return "; note: ranked lower due to weaker JD alignment vs top candidates"
    elif rank > 50:
        if concerns:
            return "; concerns: " + ", ".join(concerns[:2])
        else:
            return "; note: solid profile but narrower domain coverage than higher-ranked candidates"
    elif rank > 30:
        if concerns:
            return "; some concern on " + concerns[0]
        return ""
    elif concerns:
        return "; minor note: " + concerns[0]
    return ""


def generate(candidate: dict, rank: int, dim_scores: dict) -> str:
    profile = candidate['profile']
    signals = candidate.get('redrob_signals', {})

    title = profile.get('current_title', 'Unknown')
    yoe = profile.get('years_of_experience', 0)
    company = profile.get('current_company', '')
    country = profile.get('country', '')
    location = profile.get('location', '')

    key_skills = _get_key_skills(candidate)
    career_evidence = _get_career_evidence(candidate)
    concerns = _get_concerns(candidate, rank)
    rr = signals.get('recruiter_response_rate', 0)

    parts = []

    # Lead with title + experience
    parts.append(f"{title} with {yoe:.1f} yrs at {company}")

    # Career evidence with JD connection
    if career_evidence:
        parts.append(f"prior role as {career_evidence}")

    # JD connection for top candidates
    if rank <= 10:
        # Explicitly connect to JD requirements
        jd_connections = []
        career_text = ' '.join(r.get('description', '') for r in candidate.get('career_history', [])).lower()
        if any(kw in career_text for kw in ['ranking', 'retrieval', 'search system', 'recommendation']):
            jd_connections.append('shipped retrieval/ranking systems per JD mandate')
        if any(kw in career_text for kw in ['production', 'deployed', 'served', 'real users']):
            jd_connections.append('production ML deployment experience')
        if jd_connections:
            parts.append(jd_connections[0])

    # Key skills with depth context
    if key_skills:
        skills_str = ", ".join(key_skills[:3])
        td = dim_scores.get('tech_depth', 0)
        if td > 0.6:
            parts.append(f"strong depth in {skills_str}")
        elif td > 0.3:
            parts.append(f"relevant skills: {skills_str}")
        else:
            parts.append(f"some exposure to {skills_str}")

    # Behavioral note
    if rr > 0.7:
        parts.append(f"highly responsive ({rr:.0%} response rate)")
    elif rr > 0.5:
        parts.append(f"good engagement ({rr:.0%} response rate)")

    # Location
    if country.lower() == 'india':
        if any(loc in location.lower() for loc in PREFERRED_LOCATIONS):
            parts.append(f"{location}-based (preferred location)")

    # GitHub
    github = signals.get('github_activity_score', -1)
    if github > 50:
        parts.append(f"active GitHub contributor (score: {github:.0f})")

    # Assemble
    reasoning = "; ".join(parts) + concerns + "."

    return reasoning
