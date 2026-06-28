#!/usr/bin/env python3
"""
Redrob Hackathon — Intelligent Candidate Ranking System

Usage:
    python rank.py --candidates ./candidates.jsonl --out ./submission.csv

Produces a ranked top-100 CSV for the Senior AI Engineer role.
Runs in < 60 seconds on CPU with < 16 GB RAM. No network calls.
"""
import time
from pathlib import Path
import json
from scoring import role_alignment

import sys
# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import csv
from scoring import tech_depth
from config import WEIGHTS
import argparse
from scoring import shipped_systems
from scoring import experience
import heapq
from scoring import location
from scoring import behavioral
from scoring import honeypot
from scoring import bm25
from scoring import stuffing
from scoring import contradiction
from scoring import reasoning


def score_candidate(candidate: dict, ss_score: float = None) -> dict:
    penalties = stuffing.compute_penalty(candidate) * contradiction.compute_penalty(candidate)

    if ss_score is None:
        ss_score = shipped_systems.score(candidate)

    dim_scores = {
        'tech_depth': tech_depth.score(candidate),
        'shipped_systems': ss_score,
        'bm25_semantic': bm25.score(candidate),
        'experience': experience.score(candidate),
        'behavioral': behavioral.score(candidate),
        'location': location.score(candidate),
        'role_alignment': role_alignment.score(candidate),  # not weighted, for radar chart
    }

    final_score = sum(dim_scores.get(dim, 0) * w for dim, w in WEIGHTS.items())
    final_score *= penalties

    # tiebreak: slight bump from yoe + response rate so no two scores are identical
    yoe_val = candidate.get('profile', {}).get('years_of_experience', 0.0)
    resp_val = candidate.get('redrob_signals', {}).get('recruiter_response_rate', 0.0)
    final_score += (yoe_val * 0.0001) + (resp_val * 0.00001)
    final_score = max(0.0, final_score)

    return {
        'candidate_id': candidate['candidate_id'],
        'final_score': final_score,
        'is_honeypot': False,
        'dim_scores': dim_scores,
        'candidate': candidate,
    }


def process_candidates(candidates_path: str, top_n: int = 200) -> list:
    # Stream JSONL, keep top N in a min-heap
    heap = []
    total = 0
    honeypots = 0

    with open(candidates_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            candidate = json.loads(line)
            ss_score = shipped_systems.score(candidate)

            if honeypot.is_honeypot(candidate, ss_score):
                honeypots += 1
                continue

            result = score_candidate(candidate, ss_score)
            total += 1

            score_val = result['final_score']
            cid = result['candidate_id']

            if len(heap) < top_n:
                heapq.heappush(heap, (score_val, cid, result))
            elif score_val > heap[0][0]:
                heapq.heapreplace(heap, (score_val, cid, result))

            if total % 20000 == 0:
                print(f"  Processed {total:,} candidates...", file=sys.stderr)

    print(f"\nTotal candidates processed: {total:,}", file=sys.stderr)
    print(f"Honeypots detected & excluded: {honeypots}", file=sys.stderr)
    print(f"Top candidates in heap: {len(heap)}", file=sys.stderr)

    # Sort by score descending, then candidate_id ascending for ties
    results = [(score_val, cid, result) for score_val, cid, result in heap]
    results.sort(key=lambda x: (-x[0], x[1]))

    stats = {
        'total_processed': total,
        'honeypots': honeypots,
    }

    return results, stats


def generate_output(results: list, output_path: str):
    top_100 = results[:100]

    # Ensure scores are strictly non-increasing with proper tiebreak
    # Spec says: ties allowed, but tiebreak by candidate_id ascending.
    # Our sort already handles (-score, cid), so ties are in correct order.
    # We just need scores to be non-increasing (ties OK with ascending cid).
    raw_scores = []
    prev_score = float('inf')
    for i, (score_val, cid, result) in enumerate(top_100):
        # Keep original score — ties are OK as long as tiebreak is correct
        if score_val > prev_score:
            score_val = prev_score  # shouldn't happen after sort, but safety
        raw_scores.append(score_val)
        prev_score = score_val

    # Re-normalize so top score matches sample format exactly
    max_raw = max(raw_scores) if raw_scores else 1.0
    adjusted_scores = [(s / max_raw) * 0.992 for s in raw_scores]

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['candidate_id', 'rank', 'score', 'reasoning'])

        for i, (_, cid, result) in enumerate(top_100):
            rank = i + 1
            score_val = round(adjusted_scores[i], 6)

            reason = reasoning.generate(
                result['candidate'],
                rank,
                result.get('dim_scores', {}),
            )

            writer.writerow([cid, rank, f"{score_val:.6f}", reason])

    print(f"\nSubmission written to: {output_path}", file=sys.stderr)
    print(f"Top score: {adjusted_scores[0]:.4f}", file=sys.stderr)
    print(f"Bottom score (rank 100): {adjusted_scores[-1]:.4f}", file=sys.stderr)

    # Sanity check: print top 10
    print(f"\n{'='*70}", file=sys.stderr)
    print(f"{'RANK':<6} {'CANDIDATE_ID':<16} {'TITLE':<30} {'YoE':<6} {'SCORE':<8}", file=sys.stderr)
    print(f"{'='*70}", file=sys.stderr)
    for i, (_, cid, result) in enumerate(top_100[:10]):
        c = result['candidate']
        print(f"{i+1:<6} {cid:<16} {c['profile']['current_title']:<30} "
              f"{c['profile']['years_of_experience']:<6.1f} {adjusted_scores[i]:<8.4f}",
              file=sys.stderr)
    print(f"{'='*70}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description='Redrob Hackathon — Intelligent Candidate Ranking System'
    )
    parser.add_argument(
        '--candidates', '-c',
        required=True,
        help='Path to candidates.jsonl file'
    )
    parser.add_argument(
        '--out', '-o',
        default='./submission.csv',
        help='Output CSV path (default: ./submission.csv)'
    )
    args = parser.parse_args()

    if not Path(args.candidates).exists():
        print(f"Error: candidates file not found: {args.candidates}", file=sys.stderr)
        sys.exit(1)

    print("=" * 60, file=sys.stderr)
    print("  Redrob Hackathon — Intelligent Candidate Ranking", file=sys.stderr)
    print("  6-Dimension Scoring | Honeypot Detection | Anti-Stuffing", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    start_time = time.time()

    print("\n[Stage 1-4] Scoring all candidates...", file=sys.stderr)
    results, stats = process_candidates(args.candidates)

    print("\n[Stage 5-6] Generating final ranking + reasoning...", file=sys.stderr)
    generate_output(results, args.out)

    elapsed = time.time() - start_time
    print(f"\nTotal time: {elapsed:.1f} seconds", file=sys.stderr)
    print(f"Within 5-min budget: {'✅ YES' if elapsed < 300 else '❌ NO'} (limit: 300s)", file=sys.stderr)
    print("=" * 60, file=sys.stderr)


if __name__ == '__main__':
    main()
