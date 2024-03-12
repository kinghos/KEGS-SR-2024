"""Game specific code."""
from __future__ import annotations

from typing import Iterable

# Marker sizes are in mm
MARKER_SIZES: dict[Iterable[int], int] = {
    range(50): 150,  # 0-49 = 150mm
    range(50, 100): 200,  # 50-99 = 200mm
    range(100, 200): 80,  # 100-199 = 80mm
}
