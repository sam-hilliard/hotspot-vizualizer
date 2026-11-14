#!/usr/bin/env python3

from dataclasses import dataclass
from pathlib import Path

@dataclass
class SourceFile:
    path: Path
    loc: int
    hotspot_count: int

    @property
    def hotspot_density(self) -> float:
        """Number of hotspots per 100 lines of code."""
        return (self.hotspot_count / max(self.loc, 1)) * 100
