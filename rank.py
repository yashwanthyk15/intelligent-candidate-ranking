#!/usr/bin/env python3
"""
Redrob Hackathon — Intelligent Candidate Ranking System

Usage:
    python rank.py --candidates ./candidates.jsonl --out ./submission.csv

Produces a ranked top-100 CSV for the Senior AI Engineer role.
Runs in < 60 seconds on CPU with < 16 GB RAM. No network calls.
"""
import json
import csv
import sys
import time
import heapq
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import WEIGHTS
from scoring import role_alignment
from scoring import shipped_systems
from scoring import tech_depth
from scoring import experience
from scoring import behavioral
from scoring import location
from scoring import honeypot
from scoring import stuffing
from scoring import contradiction
from scoring import reasoning
from scoring import bm25


def score_candidate(candidate: dict) -> dict:
    """
    Score a single candidate across all dimensions.
    Returns dict with scores and metadata.
    """
    # Check honeypot first — if flagged, score = 0
    is_hp = honeypot.is_honeypot(candidate)
    if is_hp:
        return {
            'candidate_id': candidate['candidate_id'],
            'final_score': 0.0,
            'is_honeypot': True,
            'dim_scores': {},
            'candidate': candidate,
        }

    # Score all 6 dimensions
    bm25_score = bm25.score(candidate)
    dim_scores = {
        'role_alignment': role_alignment.score(candidate),
        'shipped_systems': shipped_systems.score(candidate),
        'tech_depth': tech_depth.score(candidate),
        'experience': experience.score(candidate),
        'behavioral': behavioral.score(candidate),
        'location': location.score(candidate),
        'bm25_semantic': bm25_score,
    }

    # Compute weighted sum
    weighted_sum = sum(
        dim_scores[dim] * weight
        for dim, weight in WEIGHTS.items()
    )

    # Apply stuffing penalty
    stuff_penalty = stuffing.compute_penalty(candidate)

    # Apply contradiction penalty
    contra_penalty = contradiction.compute_penalty(candidate)

    # Final score
    final_score = weighted_sum * stuff_penalty * contra_penalty
    
    # BM25 math boost for dense JD keyword overlap
    final_score += (bm25_score * 0.05)

    # GitHub bonus (additive, small)
    github = candidate.get('redrob_signals', {}).get('github_activity_score', -1)
    if github > 50:
        final_score += 0.02
    elif github > 20:
        final_score += 0.01

    # Saved-by-recruiters bonus (market validation)
    saved = candidate.get('redrob_signals', {}).get('saved_by_recruiters_30d', 0)
    if saved > 10:
        final_score += 0.01

    # No upper clamp — we need differentiation among top candidates
    # Scores naturally cap around 1.03 from weighted sum + small bonuses
    final_score = max(0.0, final_score)

    return {
        'candidate_id': candidate['candidate_id'],
        'final_score': final_score,
        'is_honeypot': False,
        'dim_scores': dim_scores,
        'stuff_penalty': stuff_penalty,
        'contra_penalty': contra_penalty,
        'candidate': candidate,
    }


def process_candidates(candidates_path: str, top_n: int = 200) -> list:
    """
    Stream through candidates.jsonl and keep top N scored candidates.
    Uses a min-heap to efficiently track top N.
    """
    heap = []
    total = 0
    honeypots = 0

    with open(candidates_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            candidate = json.loads(line)
            result = score_candidate(candidate)
            total += 1

            if result['is_honeypot']:
                honeypots += 1
                continue

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
    """
    Generate the submission CSV with top 100 ranked candidates.
    Ensures scores are strictly non-increasing.
    """
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
