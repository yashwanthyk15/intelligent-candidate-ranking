"""
Contradiction Detection
Detects mismatches between title, headline, summary, and career history.
Separate from honeypots — these are 'misleading' rather than 'impossible' profiles.
"""


def compute_penalty(candidate: dict) -> float:
    # Calculate and return contradiction multiplier
    penalty = 1.0
    profile = candidate['profile']
    career = candidate.get('career_history', [])

    title = profile.get('current_title', '').lower()
    headline = profile.get('headline', '').lower()
    summary = profile.get('summary', '').lower()

    # 1. Title words not in headline at all
    title_words = set(title.split())
    headline_words = set(headline.split())
    if title_words and not title_words.intersection(headline_words):
        penalty *= 0.95

    non_tech_professions = [
        'marketing', 'sales', 'accounting', 'hr ', 'human resource',
        'customer support', 'operations', 'civil engineer', 'mechanical',
        'graphic design', 'content writ',
    ]
    ml_indicators = [
        'machine learning', 'ml ', 'ai ', 'data scien', 'deep learning',
        'nlp', 'search engineer', 'ranking', 'retrieval',
    ]

    # 2. Title suggests ML but summary describes non-tech work
    title_is_ml = any(kw in title for kw in ['ml', 'ai', 'data', 'machine', 'research'])
    summary_is_nontech = any(kw in summary for kw in non_tech_professions)
    if title_is_ml and summary_is_nontech:
        penalty *= 0.85

    # 3. Career history descriptions contradict title
    if career:
        ml_career_count = 0
        nontech_career_count = 0
        for role in career:
            desc = role.get('description', '').lower()
            if any(kw in desc for kw in ['machine learning', 'ml ', 'model', 'embeddings',
                                          'neural', 'ranking', 'retrieval', 'nlp',
                                          'pytorch', 'tensorflow', 'deployed model']):
                ml_career_count += 1
            elif any(kw in desc for kw in non_tech_professions):
                nontech_career_count += 1

        # ML title but all career descriptions are non-tech
        if title_is_ml and nontech_career_count > 0 and ml_career_count == 0:
            penalty *= 0.70

        # Non-tech title but career IS ML — hidden gem boost
        title_is_nontech = any(kw in title for kw in ['manager', 'executive', 'accountant',
                                                       'support', 'writer', 'designer'])
        if title_is_nontech and ml_career_count > 0 and nontech_career_count == 0:
            penalty = min(1.1, penalty * 1.10)

    # 4. Summary explicitly claims different profession
    career_claim_nontech = any(
        phrase in summary for phrase in [
            'spent my career in marketing', 'spent my career in sales',
            'spent my career in hr', 'spent my career in operations',
        ]
    )
    if career_claim_nontech and title_is_ml:
        penalty *= 0.75

    # 5. Summary admits limited AI experience
    limited_ai = any(
        phrase in summary for phrase in [
            'my own technical depth in ai is limited',
            'my technical depth in ai is limited',
            'experimented with chatgpt',
            'curious about how ai tools',
        ]
    )
    if limited_ai:
        penalty *= 0.80

    return round(max(0.3, min(1.1, penalty)), 4)
