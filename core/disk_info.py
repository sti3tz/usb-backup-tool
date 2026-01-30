"""
Speicherplatz-Informationen für den USB-Stick.

Stellt eine ``DiskUsage``-Datenklasse und eine Hilfsfunktion bereit,
um den belegten und freien Speicherplatz eines Pfades abzufragen.
"""

import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DiskUsage:
    """Speicherplatz-Daten: Gesamtgröße, belegt, frei (in Bytes)."""

    total: int
    used: int
    free: int

    @property
    def used_percent(self) -> float:
        """Prozentualer Anteil des belegten Speicherplatzes."""
        return (self.used / self.total * 100) if self.total else 0.0

    @property
    def free_percent(self) -> float:
        """Prozentualer Anteil des freien Speicherplatzes."""
        return (self.free / self.total * 100) if self.total else 0.0

    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Bytes in lesbares Format umwandeln (z.B. ``'12.3 MB'``)."""
        v = float(size_bytes)
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if abs(v) < 1024:
                return f"{v:.1f} {unit}"
            v /= 1024
        return f"{v:.1f} PB"


def get_disk_usage(path: Path) -> DiskUsage:
    """Speicherplatz des Datenträgers ermitteln, auf dem *path* liegt."""
    try:
        u = shutil.disk_usage(str(path))
        return DiskUsage(total=u.total, used=u.used, free=u.free)
    except (OSError, FileNotFoundError):
        return DiskUsage(total=0, used=0, free=0)
