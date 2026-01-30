#!/usr/bin/env python3
"""
USB Backup Tool – Einstiegspunkt der Anwendung.

Ermittelt das Stammverzeichnis (USB-Stick-Root), legt die
erforderlichen Unterordner an und startet die Qt-GUI.
"""

import os
import sys
from pathlib import Path


def get_app_root() -> Path:
    """Stammverzeichnis der App ermitteln (= USB-Stick-Root).

    Bei einer PyInstaller-EXE ist das der Ordner der .exe,
    ansonsten der Ordner, in dem main.py liegt.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


def main():
    """Hauptfunktion: Verzeichnisse vorbereiten, GUI starten."""
    app_root = get_app_root()
    os.chdir(str(app_root))

    # Benötigte Unterordner sicherstellen
    for sub in ("Config", "Backups", "Logs"):
        (app_root / sub).mkdir(exist_ok=True)

    from PySide6.QtWidgets import QApplication

    from gui.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("USB Backup Tool")
    # Fusion-Stil sorgt für einheitliches Aussehen auf allen Plattformen
    app.setStyle("Fusion")

    window = MainWindow(app_root)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
