import json

def check_rules(candidate):
    skills = candidate.get('skills', [])
    career = candidate.get('career_history', [])
    signals = candidate.get('redrob_signals', {})
    profile = candidate.get('profile', {})
    title = profile.get('current_title', '').lower()
    
    flags = {}
    
    # 0-month roles
    for job in career:
        if job.get('duration_months') == 0:
            flags['0_month_job'] = True
            if 'expert' in [s.get('level', '').lower() for s in skills]:
                flags['0_month_expert'] = True

    # Assessment contradiction (highly endorsed, low assessment)
    endorsements = sum(s.get('endorsements', 0) for s in skills)
    assessments = [s.get('assessment_score', 0) for s in skills if 'assessment_score' in s]
    avg_assess = sum(assessments) / len(assessments) if assessments else 0
    if endorsements > 20 and avg_assess > 0 and avg_assess < 50:
        flags['contradiction_1'] = True
    if endorsements > 50 and avg_assess > 0 and avg_assess < 30:
        flags['contradiction_2'] = True
        
    # Impossible combinations
    expert_skills = [s for s in skills if s.get('level', '').lower() == 'expert']
    if profile.get('years_of_experience', 0) < 1.0 and len(expert_skills) > 3:
        flags['junior_expert'] = True
        
    return flags

counts = {}
with open(r"C:\Users\yashw\.gemini\antigravity\scratch\redrob_hackathon\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl", 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        c = json.loads(line)
        flags = check_rules(c)
        for k in flags:
            counts[k] = counts.get(k, 0) + 1

print("Honeypot hit counts:")
for k, v in counts.items():
    print(f"{k}: {v}")
