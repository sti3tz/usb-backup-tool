"""
Konfigurationsverwaltung – lädt und speichert config.json auf dem USB-Stick.

Die Konfigurationsdatei enthält Sprache, Quellpfade, Ausschlüsse,
Vergleichsmethode und weitere Benutzereinstellungen.  Beim Laden
werden fehlende Schlüssel automatisch mit Standardwerten ergänzt.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Standardwerte – werden verwendet, wenn config.json fehlt oder unvollständig ist.
DEFAULT_CONFIG = {
    "language": "de",
    "sources": [],
    "target_subfolder": "Backups",
    "excludes": [
        "*.tmp", "*.temp", "*.log", "Thumbs.db", ".DS_Store",
        "desktop.ini", "node_modules", "__pycache__", ".git",
    ],
    "compare_method": "timestamp_size",
    "delete_removed": False,
    "auto_preview_on_start": True,
    "window_width": 1000,
    "window_height": 700,
}


class ConfigManager:
    """Verwaltet die JSON-Konfigurationsdatei auf dem USB-Stick.

    Attribute:
        config_path: Absoluter Pfad zur config.json.
        data:        Aktuelles Konfigurations-Dictionary.
    """

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.data: dict = dict(DEFAULT_CONFIG)
        self.load()

    def load(self):
        """Konfiguration aus der JSON-Datei lesen (falls vorhanden)."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as fh:
                    loaded = json.load(fh)
                self.data.update(loaded)
            except (json.JSONDecodeError, IOError):
                pass  # Bei Fehler: Standardwerte beibehalten

    def save(self):
        """Aktuelle Konfiguration als JSON auf den Stick schreiben."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as fh:
            json.dump(self.data, fh, indent=2, ensure_ascii=False)

    def get(self, key: str, default: Any = None) -> Any:
        """Einzelnen Konfigurationswert auslesen."""
        return self.data.get(key, default)

    def set(self, key: str, value: Any):
        """Einzelnen Konfigurationswert setzen (ohne sofortiges Speichern)."""
        self.data[key] = value
