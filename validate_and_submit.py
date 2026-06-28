#!/usr/bin/env python3
"""
Validation + summary report for the submission.
Runs sanity checks and prints detailed analysis.
"""
import csv
import json
import sys
from pathlib import Path
from collections import Counter


def analyze_submission(csv_path: str, candidates_path: str = None):
    """Print detailed analysis of submission."""
    print("=" * 60)
    print("  Submission Analysis Report")
    print("=" * 60)

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"\nTotal rows: {len(rows)}")
    assert len(rows) == 100, f"ERROR: Expected 100 rows, got {len(rows)}"

    # Check ranks
    ranks = [int(r['rank']) for r in rows]
    assert sorted(ranks) == list(range(1, 101)), "ERROR: Ranks not 1-100!"

    # Check unique candidate_ids
    cids = [r['candidate_id'] for r in rows]
    assert len(set(cids)) == 100, "ERROR: Duplicate candidate_ids!"

    # Score distribution
    scores = [float(r['score']) for r in rows]
    print(f"Score range: {min(scores):.4f} — {max(scores):.4f}")
    print(f"Score mean: {sum(scores)/len(scores):.4f}")

    # Check non-increasing
    non_increasing = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
    print(f"Scores non-increasing: {'YES' if non_increasing else 'NO !!!'}")

    # Check reasoning
    empty_reasons = sum(1 for r in rows if not r.get('reasoning', '').strip())
    print(f"Empty reasonings: {empty_reasons}")

    # Check reasoning variation
    reasons = [r.get('reasoning', '') for r in rows]
    unique_reasons = len(set(reasons))
    print(f"Unique reasonings: {unique_reasons}/100")

    if candidates_path and Path(candidates_path).exists():
        print("\nLoading candidate profiles for cross-check...")
        cand_lookup = {}
        with open(candidates_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    c = json.loads(line)
                    cand_lookup[c['candidate_id']] = c

        # Verify all candidate_ids exist
        missing = [cid for cid in cids if cid not in cand_lookup]
        print(f"Missing candidate_ids: {len(missing)} {'FAIL' if missing else 'OK'}")

        print(f"\n{'='*70}")
        print("TOP 10 CANDIDATES — DETAILED")
        print(f"{'='*70}")
        for row in rows[:10]:
            cid = row['candidate_id']
            if cid in cand_lookup:
                c = cand_lookup[cid]
                p = c['profile']
                s = c['redrob_signals']
                print(f"\n  Rank {row['rank']}: {cid}")
                print(f"    Title: {p['current_title']} @ {p['current_company']}")
                print(f"    YoE: {p['years_of_experience']} | Country: {p['country']} | Location: {p.get('location', 'N/A')}")
                print(f"    Skills: {len(c['skills'])} | Industry: {p['current_industry']}")
                print(f"    Response Rate: {s['recruiter_response_rate']:.2f} | Open: {s['open_to_work_flag']}")
                print(f"    Last Active: {s['last_active_date']} | GitHub: {s['github_activity_score']}")
                print(f"    Notice: {s['notice_period_days']}d | Saved: {s['saved_by_recruiters_30d']}")
                print(f"    Score: {row['score']}")
                print(f"    Reasoning: {row['reasoning'][:120]}...")

        # Title distribution
        title_dist = Counter()
        industry_dist = Counter()
        country_dist = Counter()
        for row in rows:
            cid = row['candidate_id']
            if cid in cand_lookup:
                title_dist[cand_lookup[cid]['profile']['current_title']] += 1
                industry_dist[cand_lookup[cid]['profile']['current_industry']] += 1
                country_dist[cand_lookup[cid]['profile']['country']] += 1

        print(f"\n{'='*50}")
        print("TITLE DISTRIBUTION IN TOP 100")
        print(f"{'='*50}")
        for title, count in title_dist.most_common():
            print(f"  {title}: {count}")

        print(f"\nINDUSTRY DISTRIBUTION")
        for ind, count in industry_dist.most_common():
            print(f"  {ind}: {count}")

        print(f"\nCOUNTRY DISTRIBUTION")
        for co, count in country_dist.most_common():
            print(f"  {co}: {count}")

    print(f"\n{'='*60}")
    print("  ALL CHECKS PASSED" if non_increasing and len(rows) == 100 else "  ISSUES FOUND")
    print(f"{'='*60}")


if __name__ == '__main__':
    csv_path = sys.argv[1] if len(sys.argv) > 1 else 'submission.csv'
    candidates_path = sys.argv[2] if len(sys.argv) > 2 else None
    analyze_submission(csv_path, candidates_path)
