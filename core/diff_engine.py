"""
Diff-Engine – vergleicht Quellverzeichnisse mit dem Backup-Ziel.

Die Engine durchläuft rekursiv alle Quelldateien, wendet Ausschluss-
muster an und klassifiziert jede Datei als NEU, AKTUALISIERT,
ÜBERSPRUNGEN oder FEHLER.

Unterstützte Vergleichsmethoden:
    - ``timestamp_size``: Dateigröße + Änderungsdatum (schnell)
    - ``hash``: SHA-256-Prüfsumme (gründlich, langsamer)
"""

from __future__ import annotations

import fnmatch
import hashlib
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional


class FileAction(Enum):
    """Mögliche Aktionen für eine Datei beim Backup."""

    NEW = "new"          # Datei existiert nur in der Quelle
    UPDATED = "updated"  # Datei hat sich seit dem letzten Backup geändert
    SKIPPED = "skipped"  # Datei ist identisch – wird übersprungen
    ERROR = "error"      # Datei konnte nicht gelesen/verglichen werden


@dataclass
class FileEntry:
    """Beschreibt eine einzelne Datei im Diff-Ergebnis.

    Attribute:
        source_path:   Absoluter Quellpfad.
        relative_path: Relativer Pfad (inkl. Quellordner-Name).
        target_path:   Absoluter Zielpfad auf dem Stick.
        action:        Geplante Aktion (NEW / UPDATED / SKIPPED / ERROR).
        source_size:   Dateigröße in Bytes.
        source_mtime:  Letzter Änderungszeitpunkt (Unix-Timestamp).
        reason:        Fehlerbeschreibung (nur bei ERROR).
    """

    source_path: Path
    relative_path: Path
    target_path: Path
    action: FileAction
    source_size: int = 0
    source_mtime: float = 0.0
    reason: str = ""


class DiffEngine:
    """Vergleichsmodul – scannt Quellen und erstellt die Datei-Aktionsliste.

    Args:
        compare_method: ``"timestamp_size"`` oder ``"hash"``.
        excludes:       Glob-Muster für auszuschließende Dateien/Ordner.
    """

    def __init__(
        self,
        compare_method: str = "timestamp_size",
        excludes: Optional[list[str]] = None,
    ):
        self.compare_method = compare_method
        self.excludes = excludes or []

    # ------------------------------------------------------------------
    def scan(
        self,
        sources: list[str],
        target_base: Path,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> list[FileEntry]:
        """Alle Quellverzeichnisse scannen und Diff-Liste erstellen."""
        entries: list[FileEntry] = []
        for src_str in sources:
            src = Path(src_str)
            if not src.exists():
                entries.append(
                    FileEntry(
                        source_path=src,
                        relative_path=Path(src.name),
                        target_path=target_base,
                        action=FileAction.ERROR,
                        reason=f"Source not found: {src_str}",
                    )
                )
                continue

            src_name = src.name
            for fp in src.rglob("*"):
                if not fp.is_file():
                    continue
                if self._is_excluded(fp, src):
                    continue
                try:
                    rel = fp.relative_to(src)
                    target = target_base / src_name / rel
                    st = fp.stat()
                    action = self._compare(fp, target, st)
                    entries.append(
                        FileEntry(
                            source_path=fp,
                            relative_path=Path(src_name) / rel,
                            target_path=target,
                            action=action,
                            source_size=st.st_size,
                            source_mtime=st.st_mtime,
                        )
                    )
                except PermissionError:
                    entries.append(
                        FileEntry(
                            source_path=fp,
                            relative_path=Path(src_name) / fp.name,
                            target_path=target_base,
                            action=FileAction.ERROR,
                            reason="Permission denied",
                        )
                    )
                except Exception as exc:
                    entries.append(
                        FileEntry(
                            source_path=fp,
                            relative_path=Path(src_name) / fp.name,
                            target_path=target_base,
                            action=FileAction.ERROR,
                            reason=str(exc),
                        )
                    )
                if progress_callback:
                    progress_callback(str(fp))
        return entries

    # ------------------------------------------------------------------
    def _compare(self, source: Path, target: Path, src_stat) -> FileAction:
        """Einzelne Datei vergleichen und passende Aktion bestimmen."""
        if not target.exists():
            return FileAction.NEW

        tgt_stat = target.stat()

        if self.compare_method == "hash":
            if self._file_hash(source) != self._file_hash(target):
                return FileAction.UPDATED
            return FileAction.SKIPPED

        # Standard: Zeitstempel + Größe
        if src_stat.st_size != tgt_stat.st_size:
            return FileAction.UPDATED
        # 1 Sekunde Toleranz wegen FAT32-Zeitstempelauflösung (2s)
        if src_stat.st_mtime > tgt_stat.st_mtime + 1:
            return FileAction.UPDATED
        return FileAction.SKIPPED

    # ------------------------------------------------------------------
    def _is_excluded(self, file_path: Path, source_root: Path) -> bool:
        """Prüfen, ob die Datei durch ein Ausschlussmuster gefiltert wird."""
        rel = file_path.relative_to(source_root)
        name = file_path.name
        for pat in self.excludes:
            if fnmatch.fnmatch(name, pat):
                return True
            if fnmatch.fnmatch(str(rel), pat):
                return True
            for part in rel.parts:
                if fnmatch.fnmatch(part, pat):
                    return True
        return False

    # ------------------------------------------------------------------
    @staticmethod
    def _file_hash(path: Path, block_size: int = 65536) -> str:
        """SHA-256-Hash einer Datei blockweise berechnen."""
        h = hashlib.sha256()
        with open(path, "rb") as f:
            while True:
                chunk = f.read(block_size)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()
