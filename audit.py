"""Forensic audit: hallucination check + score analysis + spec compliance."""
import json, csv, random

# Load submission
rows = []
with open('submission.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Load candidates
cand = {}
with open(r'C:\Users\yashw\.gemini\antigravity\scratch\redrob_hackathon\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            c = json.loads(line)
            cand[c['candidate_id']] = c

# Check 10 random rows for hallucination
random.seed(42)
sample_indices = sorted(random.sample(range(100), 10))

print('=== HALLUCINATION CHECK: 10 RANDOM SAMPLES ===')
print()
issues = 0
for idx in sample_indices:
    row = rows[idx]
    cid = row['candidate_id']
    reason = row['reasoning']
    c = cand[cid]
    p = c['profile']
    s = c['redrob_signals']
    
    print(f'Rank {row["rank"]}: {cid}')
    print(f'  TITLE:   {p["current_title"]}')
    print(f'  COMPANY: {p["current_company"]}')
    print(f'  YoE:     {p["years_of_experience"]}')
    print(f'  Country: {p["country"]} | Location: {p.get("location", "N/A")}')
    print(f'  Response Rate: {s["recruiter_response_rate"]:.2f}')
    
    # Check: does reasoning mention current_title?
    title_in_reason = p['current_title'] in reason
    print(f'  Title in reasoning: {"YES" if title_in_reason else "NO !!!"}')
    if not title_in_reason:
        issues += 1
    
    # Check: does reasoning mention company?
    company_in_reason = p['current_company'] in reason
    print(f'  Company in reasoning: {"YES" if company_in_reason else "NO"}')
    
    # Check YoE in reasoning
    yoe_str = f"{p['years_of_experience']:.1f}"
    yoe_in_reason = yoe_str in reason
    print(f'  YoE in reasoning: {"YES" if yoe_in_reason else "NO"}')
    
    # Check: skills mentioned in reasoning actually exist in profile
    skill_names_in_profile = {sk['name'] for sk in c['skills']}
    mentioned_skills = [sk['name'] for sk in c['skills'] if sk['name'] in reason]
    print(f'  Skills in reasoning: {mentioned_skills}')
    
    # Check for response rate hallucination
    rr = s['recruiter_response_rate']
    if f'{rr:.0%}' in reason:
        print(f'  Response rate in reasoning: YES ({rr:.0%})')
    
    # Check rank-tone consistency
    rank_num = int(row['rank'])
    has_concern = 'concern' in reason.lower()
    if rank_num <= 20 and has_concern:
        print(f'  WARN: Top-20 candidate has concern mentioned')
    if rank_num >= 80 and not has_concern:
        print(f'  NOTE: Bottom-20 candidate has no concern mentioned')
    
    print(f'  REASONING: {reason}')
    print()

# Score analysis
scores = [float(r['score']) for r in rows]
print(f'=== SCORE ANALYSIS ===')
print(f'Score at rank 1:   {scores[0]}')
print(f'Score at rank 10:  {scores[9]}')
print(f'Score at rank 50:  {scores[49]}')
print(f'Score at rank 100: {scores[99]}')
print(f'Score spread (1-100): {scores[0] - scores[99]:.6f}')
print(f'Score spread (1-10):  {scores[0] - scores[9]:.6f}')
num_ties = sum(1 for i in range(99) if abs(scores[i] - scores[i+1]) < 1e-8)
print(f'Number of score ties: {num_ties}')

# Check for identical reasonings
reasons = [r['reasoning'] for r in rows]
print(f'Unique reasons: {len(set(reasons))}/100')

# Check all candidate_ids exist
missing = [r['candidate_id'] for r in rows if r['candidate_id'] not in cand]
print(f'Missing candidate_ids: {len(missing)}')

# Check ranks 1-100
ranks = sorted([int(r['rank']) for r in rows])
print(f'Ranks correct (1-100): {ranks == list(range(1, 101))}')

# Check non-increasing
non_inc = all(scores[i] >= scores[i+1] for i in range(99))
print(f'Scores non-increasing: {non_inc}')

# Filename check
print(f'\nFILENAME NOTE: Submission must be named <participant_id>.csv, not submission.csv')

# Common rejection checks
print(f'\n=== COMMON REJECTION CHECKS ===')
print(f'Exactly 100 rows: {len(rows) == 100}')
print(f'Ranks start at 1: {min(int(r["rank"]) for r in rows) == 1}')
print(f'No duplicate cids: {len(set(r["candidate_id"] for r in rows)) == 100}')
print(f'All scores different or properly tied: {non_inc}')
print(f'All have reasoning: {all(r.get("reasoning", "").strip() for r in rows)}')

print(f'\nTotal hallucination issues found: {issues}')
