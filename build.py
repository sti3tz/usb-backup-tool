#!/usr/bin/env python3
"""
Build-Skript – Erstellt portable Einzeldatei-Executables mit PyInstaller.

Voraussetzung:
    pip install pyinstaller

Verwendung:
    python build.py

Ergebnis:
    dist/USB-Backup-Tool.exe  (Windows)
    dist/USB-Backup-Tool      (macOS / Linux)
"""

import platform
import subprocess
import sys


def build():
    """PyInstaller ausführen und plattformspezifische Optionen setzen."""
    # Trennzeichen für --add-data: Semikolon unter Windows, Doppelpunkt sonst
    sep = ";" if platform.system() == "Windows" else ":"
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",       # Alles in eine Datei packen
        "--windowed",      # Kein Konsolenfenster anzeigen
        "--name", "USB-Backup-Tool",
        f"--add-data=locales{sep}locales",  # Sprachdateien einbetten
        "main.py",
    ]
    if platform.system() == "Darwin":
        cmd.append("--osx-bundle-identifier=com.usb-backup-tool")

    print("Starte Build:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print("\nBuild abgeschlossen.  Ergebnis → dist/USB-Backup-Tool")


if __name__ == "__main__":
    build()
