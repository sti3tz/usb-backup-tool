"""
Tägliche Logdateien – eine Datei pro Tag, Append bei wiederholten Backups.

Pfad:   ``Logs/YYYY-MM-DD.log``
Regel:  Wenn am selben Tag mehrere Backups laufen, werden alle Sessions
        in dieselbe Datei angehängt (nicht überschrieben).

Jede Session enthält:
    - Start-/Endzeitpunkt, Rechnername, Betriebssystem
    - Quell- und Zielpfade
    - Liste aller bearbeiteten Dateien mit Aktion und Größe
    - Statistik: Kopiert, Übersprungen, Fehler, Datenmenge, Dauer
"""

from __future__ import annotations

import json
import platform
from datetime import datetime
from pathlib import Path
from typing import Optional


class BackupLogger:
    """Schreibt strukturierte Logeinträge in tägliche Textdateien.

    Attribute:
        log_dir: Verzeichnis für die Logdateien (``Logs/``).
    """

    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)

    @property
    def log_path(self) -> Path:
        """Pfad zur heutigen Logdatei."""
        return self.log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"

    # ------------------------------------------------------------------
    def start_session(self, sources: list[str], target: str):
        """Session-Header in die Logdatei schreiben."""
        self._w("")
        self._w("=" * 70)
        self._w("BACKUP SESSION START")
        self._w(f"  Timestamp : {datetime.now().isoformat()}")
        self._w(f"  Computer  : {platform.node()}")
        self._w(f"  OS        : {platform.system()} {platform.release()}")
        self._w(f"  Sources   : {', '.join(sources)}")
        self._w(f"  Target    : {target}")
        self._w("-" * 70)

    def log_file(self, relative_path: str, action: str,
                 size: int = 0, detail: str = ""):
        """Einzelne Datei-Aktion loggen (COPIED, SKIPPED, ERROR etc.)."""
        size_str = f"  ({self._fmt(size)})" if size > 0 else ""
        extra = f"  -- {detail}" if detail else ""
        self._w(f"  [{action:>15}] {relative_path}{size_str}{extra}")

    def end_session(self, stats: dict):
        """Session-Footer mit Statistik in die Logdatei schreiben."""
        self._w("-" * 70)
        self._w("STATISTICS:")
        self._w(f"  Copied    : {stats.get('copied', 0)} files")
        self._w(f"  Skipped   : {stats.get('skipped', 0)} files")
        self._w(f"  Errors    : {stats.get('errors', 0)}")
        self._w(f"  Data      : {self._fmt(stats.get('bytes_copied', 0))}")
        self._w(f"  Duration  : {stats.get('duration', 0):.1f}s")
        if stats.get("error_details"):
            self._w("  Errors detail:")
            for err in stats["error_details"]:
                self._w(f"    - {err}")
        self._w(f"BACKUP SESSION END: {datetime.now().isoformat()}")
        self._w("=" * 70)

    # ------------------------------------------------------------------
    def get_last_session_info(self) -> Optional[dict]:
        """Letzte Session aus der neuesten Logdatei extrahieren.

        Wird für die Sidebar-Anzeige im Hauptfenster verwendet.
        Gibt ``None`` zurück, wenn keine Logs vorhanden sind.
        """
        log_files = sorted(self.log_dir.glob("*.log"), reverse=True)
        if not log_files:
            return None
        try:
            content = log_files[0].read_text(encoding="utf-8")
            parts = content.split("BACKUP SESSION START")
            if len(parts) < 2:
                return None
            last = parts[-1]
            info: dict = {"log_file": log_files[0].name, "date": log_files[0].stem}
            for line in last.splitlines():
                s = line.strip()
                if s.startswith("Timestamp"):
                    info["timestamp"] = s.split(":", 1)[1].strip()
                elif s.startswith("Copied"):
                    info["copied"] = s.split(":")[1].strip()
                elif s.startswith("Errors") and "detail" not in s:
                    info["errors"] = s.split(":")[1].strip()
            return info
        except Exception:
            return None

    # ------------------------------------------------------------------
    def _w(self, line: str):
        """Zeile an die heutige Logdatei anhängen."""
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    @staticmethod
    def _fmt(size_bytes: int) -> str:
        """Bytes in lesbares Format umwandeln."""
        v = float(size_bytes)
        for u in ("B", "KB", "MB", "GB"):
            if abs(v) < 1024:
                return f"{v:.1f} {u}"
            v /= 1024
        return f"{v:.1f} TB"
