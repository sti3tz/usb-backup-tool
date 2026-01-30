"""
Backup-Engine – QThread-Worker für Scan und Kopiervorgang.

Enthält zwei Worker-Klassen, die in Hintergrund-Threads laufen,
damit die GUI während des Scannens und Kopierens reaktionsfähig bleibt:

- ``ScanWorker``:   Führt den Dateivergleich (DiffEngine) aus.
- ``BackupWorker``: Kopiert Dateien und sendet Fortschrittssignale.
"""

from __future__ import annotations

import shutil
import time
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from .diff_engine import DiffEngine, FileAction, FileEntry


class ScanWorker(QThread):
    """Hintergrund-Thread für den Dateivergleich (Dry-Run / Vorschau).

    Signale:
        progress(str):       Aktuell gescannte Datei.
        finished_scan(list): Fertige Liste aller FileEntry-Objekte.
        error(str):          Fehlermeldung bei Abbruch.
    """

    progress = Signal(str)
    finished_scan = Signal(list)
    error = Signal(str)

    def __init__(self, diff_engine: DiffEngine, sources: list[str],
                 target_base: Path, parent=None):
        super().__init__(parent)
        self.diff_engine = diff_engine
        self.sources = sources
        self.target_base = target_base

    def run(self):
        """Scan starten und Ergebnis per Signal zurückgeben."""
        try:
            entries = self.diff_engine.scan(
                self.sources,
                self.target_base,
                progress_callback=lambda f: self.progress.emit(f),
            )
            self.finished_scan.emit(entries)
        except Exception as exc:
            self.error.emit(str(exc))


class BackupWorker(QThread):
    """Hintergrund-Thread für den eigentlichen Kopiervorgang.

    Kopiert alle als NEU oder AKTUALISIERT markierten Dateien und
    sendet dabei Echtzeit-Fortschrittssignale an die GUI.

    Signale:
        progress(int, int, str):   Aktueller Index, Gesamt, Dateiname.
        file_done(str, str, int):  Dateipfad, Status, Größe.
        speed_update(float):       Aktuelle Geschwindigkeit in Bytes/s.
        finished_backup(dict):     Statistik-Dictionary nach Abschluss.
    """

    progress = Signal(int, int, str)
    file_done = Signal(str, str, int)
    speed_update = Signal(float)
    finished_backup = Signal(dict)

    def __init__(self, entries: list[FileEntry], parent=None):
        super().__init__(parent)
        self.entries = entries
        self._cancelled = False

    def cancel(self):
        """Kopiervorgang abbrechen (wird nach der aktuellen Datei wirksam)."""
        self._cancelled = True

    def run(self):
        """Dateien kopieren und Fortschritt melden."""
        stats = {
            "copied": 0,
            "skipped": 0,
            "errors": 0,
            "bytes_copied": 0,
            "error_details": [],
            "start_time": time.time(),
        }

        # Nur Dateien mit Aktion NEU oder AKTUALISIERT werden kopiert
        actionable = [
            e for e in self.entries
            if e.action in (FileAction.NEW, FileAction.UPDATED)
        ]
        stats["skipped"] = sum(
            1 for e in self.entries if e.action == FileAction.SKIPPED
        )
        total = len(actionable)

        # Gleitendes Fenster für Geschwindigkeitsberechnung (letzte 20 Dateien)
        window: list[tuple[int, float]] = []

        for idx, entry in enumerate(actionable):
            if self._cancelled:
                stats["cancelled"] = True
                break

            self.progress.emit(idx + 1, total, str(entry.relative_path))

            try:
                # Zielverzeichnis anlegen (falls nötig)
                entry.target_path.parent.mkdir(parents=True, exist_ok=True)
                t0 = time.time()
                # copy2 erhält Metadaten (Zeitstempel etc.)
                shutil.copy2(str(entry.source_path), str(entry.target_path))
                elapsed = max(time.time() - t0, 0.001)

                stats["copied"] += 1
                stats["bytes_copied"] += entry.source_size
                self.file_done.emit(str(entry.relative_path), "OK", entry.source_size)

                # Geschwindigkeit berechnen (gleitendes Fenster)
                window.append((entry.source_size, elapsed))
                if len(window) > 20:
                    window.pop(0)
                total_bytes = sum(b for b, _ in window)
                total_time = sum(t for _, t in window)
                if total_time > 0:
                    self.speed_update.emit(total_bytes / total_time)

            except PermissionError:
                stats["errors"] += 1
                stats["error_details"].append(
                    f"{entry.relative_path}: Zugriff verweigert"
                )
                self.file_done.emit(
                    str(entry.relative_path), "PERMISSION_ERROR", 0
                )
            except OSError as exc:
                stats["errors"] += 1
                stats["error_details"].append(
                    f"{entry.relative_path}: {exc}"
                )
                self.file_done.emit(str(entry.relative_path), "ERROR", 0)

        stats["end_time"] = time.time()
        stats["duration"] = stats["end_time"] - stats["start_time"]
        self.finished_backup.emit(stats)
