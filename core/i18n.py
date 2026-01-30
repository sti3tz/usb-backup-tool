"""
Internationalisierung (i18n) – lädt Übersetzungen aus JSON-Locale-Dateien.

Jede Sprachdatei (z.B. ``locales/de.json``) enthält ein flaches
Schlüssel-/Wert-Dictionary.  Platzhalter im Format ``{name}`` werden
beim Abruf über ``t()`` automatisch ersetzt.

Neue Sprache hinzufügen: Einfach ``locales/xx.json`` anlegen – die
Sprache erscheint automatisch im GUI-Menü.
"""

from __future__ import annotations

import json
from pathlib import Path


class I18n:
    """Übersetzungsmanager für die Benutzeroberfläche.

    Attribute:
        locales_dir: Verzeichnis mit den Sprachdateien.
        language:    Aktuell geladener Sprachcode (z.B. ``"de"``).
        strings:     Geladene Schlüssel/Wert-Paare.
    """

    def __init__(self, locales_dir: Path, language: str = "en"):
        self.locales_dir = locales_dir
        self.strings: dict[str, str] = {}
        self.language = language
        self.load(language)

    def load(self, language: str):
        """Sprachdatei für den gegebenen Code laden."""
        self.language = language
        path = self.locales_dir / f"{language}.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as fh:
                self.strings = json.load(fh)

    def t(self, key: str, **kwargs) -> str:
        """Übersetzung für *key* zurückgeben.

        Optionale ``{name}``-Platzhalter werden durch die übergebenen
        Keyword-Argumente ersetzt.  Fehlt ein Schlüssel in der aktuellen
        Sprache, wird der Schlüsselname selbst zurückgegeben.
        """
        value = self.strings.get(key, key)
        if kwargs:
            try:
                value = value.format(**kwargs)
            except (KeyError, IndexError):
                pass
        return value

    def available_languages(self) -> list[tuple[str, str]]:
        """Liste aller verfügbaren Sprachen als ``[(code, Name), …]``."""
        langs: list[tuple[str, str]] = []
        for f in sorted(self.locales_dir.glob("*.json")):
            code = f.stem
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                name = data.get("_language_name", code)
            except Exception:
                name = code
            langs.append((code, name))
        return langs
