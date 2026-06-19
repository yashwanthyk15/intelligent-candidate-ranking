"""
Dimension 6: Location & Logistics Fit
Scores proximity to Pune/Noida and willingness to relocate.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import PREFERRED_LOCATIONS, TIER1_INDIA_LOCATIONS


def score(candidate: dict) -> float:
    """Score location fit (0.0 to 1.0)."""
    location = candidate['profile'].get('location', '').lower()
    country = candidate['profile'].get('country', '').lower()
    willing = candidate.get('redrob_signals', {}).get('willing_to_relocate', False)

    if any(loc in location for loc in PREFERRED_LOCATIONS):
        return 1.0

    if any(loc in location for loc in TIER1_INDIA_LOCATIONS):
        return 0.85

    if country == 'india':
        return 0.75 if willing else 0.55

    if willing:
        return 0.60
    return 0.15
