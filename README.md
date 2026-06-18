# Intelligent Candidate Ranking — Redrob Hackathon

> A production-grade, rule-based ranking system for the **Senior AI Engineer (Founding Team)** position. Ranks 100,000 candidates in under 90 seconds on CPU with zero external dependencies.

## Quick Start

```bash
# Reproduce the submission (single command)
python rank.py --candidates ./candidates.jsonl --out ./submission.csv

# Validate the output
python validate_and_submit.py submission.csv candidates.jsonl
```

**Runtime:** ~85 seconds on CPU | **Memory:** < 2 GB | **Dependencies:** Python 3.9+ (stdlib only)

---

## Architecture

### Why Not Embeddings?

The JD itself warns:

> *"The 'right answer' is NOT 'find candidates whose skills section contains the most AI keywords.' That's a trap we've explicitly built into the dataset."*

Embedding-based approaches suffer from exactly this flaw — they encode keyword proximity as similarity, which rewards keyword stuffers and honeypots. We use a **multi-dimensional scoring architecture** that reads and reasons about candidate profiles the way a skilled hiring manager would.

### 6-Dimension Scoring System

```
Final Score = (D1×0.28 + D2×0.25 + D3×0.20 + D4×0.12 + D5×0.10 + D6×0.05)
              × Stuffing_Penalty × Contradiction_Penalty
              + GitHub_Bonus + Recruiter_Interest_Bonus
```

| # | Dimension | Weight | What It Measures |
|---|-----------|--------|------------------|
| D1 | **Role Alignment** | 28% | Title tier (S/A/B/C/F) + historical career title boost |
| D2 | **Shipped Systems** | 25% | NLP scan of career descriptions for production ML evidence |
| D3 | **Technical Depth** | 20% | Coverage of 5 core JD domains (embeddings, vector DBs, ranking, evaluation, Python+prod) |
| D4 | **Experience Trajectory** | 12% | YoE fit (5-9yr ideal), stability, company types, progression |
| D5 | **Behavioral Availability** | 10% | Recency, response rate, open-to-work, notice period, recruiter interest |
| D6 | **Location Fit** | 5% | Pune/Noida/Delhi NCR preference, India-based, relocation willingness |

### Anti-Gaming Systems

| System | What It Catches |
|--------|----------------|
| **Honeypot Detector** | Expert skills with 0 months duration, impossible experience-to-skill ratios, career duration anomalies, assessment contradictions |
| **Keyword-Stuffing Penalty** | Non-tech titles with 8+ AI skills, all-expert profiles with zero endorsements, high skill count with low assessment scores |
| **Contradiction Detector** | ML title with non-tech career descriptions, summary admitting limited AI experience, headline-title mismatches |

### Processing Pipeline

```
100K candidates.jsonl
    → Stream line-by-line (memory efficient)
    → Honeypot check → exclude if flagged
    → 6-dimension scoring
    → Stuffing penalty × Contradiction penalty
    → Min-heap of top 200
    → Sort, take top 100
    → Generate per-candidate reasoning
    → Output submission.csv
```

---

## Key Design Decisions

### 1. Why Rule-Based Over ML?

- **No training data.** There's no labeled ground truth to train a model against.
- **Interpretability.** Every score can be explained — critical for Stage 4 (manual review) and Stage 5 (interview).
- **Reproducibility.** Deterministic output. Same input → same output every time.
- **Speed.** 85 seconds for 100K candidates on CPU. No model loading, no GPU.

### 2. Why Career History NLP > Skill Keywords?

The dataset deliberately mismatches titles, skills, and descriptions. A "Civil Engineer" may have AI skills listed but describe marketing work in their career history. We read the actual descriptions — that's where the truth is.

### 3. Why Consulting Company Penalty?

The JD explicitly states:
> *"If you've spent your career in pure research environments or consulting without any production deployment — we will not move forward."*

Candidates with consulting-only backgrounds (TCS, Infosys, Wipro, etc.) get a 50% reduction on shipped systems score and a -0.20 experience penalty.

---

## Project Structure

```
├── rank.py                    # Main entry point
├── config.py                  # All weights, thresholds, keyword lists
├── scoring/
│   ├── __init__.py
│   ├── role_alignment.py      # D1: Title tier mapping
│   ├── shipped_systems.py     # D2: Career history NLP
│   ├── tech_depth.py          # D3: Core domain coverage
│   ├── experience.py          # D4: Trajectory analysis
│   ├── behavioral.py          # D5: Availability signals
│   ├── location.py            # D6: Location fit
│   ├── honeypot.py            # Honeypot detection
│   ├── stuffing.py            # Keyword-stuffing penalty
│   ├── contradiction.py       # Contradiction detection
│   └── reasoning.py           # Reasoning generation
├── validate_and_submit.py     # Analysis & sanity checks
├── requirements.txt           # No external deps
├── submission_metadata.yaml   # Competition metadata
└── README.md                  # This file
```

---

## Results Summary

| Metric | Value |
|--------|-------|
| Total candidates processed | 100,000 |
| Honeypots detected & excluded | 22 |
| Runtime | ~85 seconds |
| Memory usage | < 2 GB |
| Top 100 title distribution | 100% ML/AI/Data Science roles |
| Top 100 country distribution | 91% India |
| Unique reasonings | 100/100 |
| Official validator | ✅ PASSED |

### Top 10 Output

| Rank | Candidate | Title | YoE | Company | Location |
|------|-----------|-------|-----|---------|----------|
| 1 | CAND_0064326 | Search Engineer | 7.6 | Sarvam AI | Gurgaon |
| 2 | CAND_0041669 | Recommendation Systems Eng. | 8.0 | CRED | Noida |
| 3 | CAND_0039383 | Applied ML Engineer | 7.1 | Meesho | Gurgaon |
| 4 | CAND_0046525 | Senior ML Engineer | 6.1 | Genpact AI | Pune |
| 5 | CAND_0061265 | Recommendation Systems Eng. | 6.6 | Zoho | Delhi |
| 6 | CAND_0077337 | Staff ML Engineer | 7.0 | Paytm | Kochi |
| 7 | CAND_0018499 | Senior ML Engineer | 7.2 | Zomato | Noida |
| 8 | CAND_0016163 | Applied ML Engineer | 6.7 | Dream11 | Gurgaon |
| 9 | CAND_0042506 | Search Engineer | 4.2 | Verloop.io | Mumbai |
| 10 | CAND_0071974 | Senior AI Engineer | 7.8 | Netflix | Mumbai |

---

## Reproducing

### Prerequisites

- Python 3.9 or later
- No pip packages required

### Steps

```bash
# 1. Clone this repository
git clone https://github.com/YOUR_USERNAME/intelligent-candidate-ranking.git
cd intelligent-candidate-ranking

# 2. Place candidates.jsonl in the project directory
# (or point to it with --candidates flag)

# 3. Run the ranker
python rank.py --candidates ./candidates.jsonl --out ./submission.csv

# 4. Validate
python validate_and_submit.py submission.csv ./candidates.jsonl
```

---

## AI Tools Declaration

- **AI Assistance:** Used standard tools (like ChatGPT / Copilot) strictly for brainstorming algorithmic approaches (such as BM25 optimizations) and as intelligent autocomplete.
- **No AI tools used during ranking.** The ranking pipeline is pure Python with zero external API calls.
- All engineering decisions, core architecture design, weight tuning, and algorithmic logic were entirely human-driven.
