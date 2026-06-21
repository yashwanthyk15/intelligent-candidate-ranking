import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))



def score(candidate: dict) -> float:
        """Returns score for location"""
    location = candidate['profile'].get('location', '').lower()
    country = candidate['profile'].get('country', '').lower()
    willing = candidate.get('redrob_signals', {}).get('willing_to_relocate', False)

    if any(loc in location for loc in ['pune', 'noida']):
        return 1.0

    if any(loc in location for loc in ['gurgaon', 'delhi', 'delhi ncr', 'bangalore', 'mumbai']):
        return 0.85

    if country == 'india':
        return 0.75 if willing else 0.55

    if willing:
        return 0.60
    return 0.15
