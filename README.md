# Candidate Ranker

Rule-based ranking pipeline for the Senior AI Engineer (Founding Team) role.
Processes 100k candidates in ~90 seconds, CPU-only, no external deps.

```bash
python rank.py --candidates ./candidates.jsonl --out ./submission.csv
python validate_and_submit.py submission.csv candidates.jsonl
```

### How it works

```
candidates.jsonl (100k lines)
       │
       ▼  stream line-by-line
[Honeypot Filter] ──(flagged)──> discard
       │
       ▼
[6-Dimension Scorer]
  ├─ Tech Depth       35%   (domain coverage across 5 JD areas)
  ├─ Shipped Systems   25%   (career history NLP for production ML evidence)
  ├─ BM25 Relevance    10%   (Okapi BM25 against JD query terms)
  ├─ Behavioral        10%   (recency, response rate, notice period)
  ├─ Experience        10%   (YoE fit, job stability, company types)
  └─ Location          10%   (Pune/Noida/NCR preferred)
       │
       ▼
[Penalties: Stuffing × Contradiction]
       │
       ▼
[Min-Heap top 200] ──sort──> [Top 100 → submission.csv]
```

### Config

All weights, keyword lists, and scoring thresholds live in `config.py`.

### Known issues

- `shipped_systems.py` is the computational bottleneck (heavy string matching per role description). Still finishes under 2 minutes.
- The dataset intentionally mismatches titles and skills. We scan career descriptions for ground truth instead of relying on the skills array.
- Consulting careers get a graduated shipped_systems penalty (50%/75%/90% at 90%/70%/50% consulting ratio). Not disqualified outright — some consulting engineers do ship real systems.
- No ML models. No training data exists, so deterministic rules + interpretable scores.

### Output

- Processed: 100,000 candidates
- Honeypots excluded: ~82
- Runtime: ~90s on CPU
- Top 100: all ML/AI/Data Science titles, 90%+ India-based
