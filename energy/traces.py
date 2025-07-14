"""Utilities for loading renewable generation traces."""
from typing import Sequence, Tuple
import csv


def load_traces(path: str) -> Tuple[Sequence[float], Sequence[float]]:
    """Load solar and wind capacity factors from a CSV file.

    The CSV must contain 'solar' and 'wind' columns giving hourly
    capacity factors (0-1)."""
    solar: list[float] = []
    wind: list[float] = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            solar.append(float(row.get("solar", 0)))
            wind.append(float(row.get("wind", 0)))
    return solar, wind
