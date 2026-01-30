# USB Backup Tool

Portables, plattformübergreifendes Backup-Werkzeug mit grafischer Oberfläche.
Läuft direkt vom USB-Stick – ohne Installation, ohne Admin-Rechte.

---

## Funktionen

- **Cross-Platform** – Windows 10/11, Windows Server 2019/2022, macOS
- **Portable** – Die komplette Anwendung lebt auf dem USB-Stick
- **Grafische Oberfläche** – Vorschau, Live-Fortschritt, Ergebnisübersicht
- **Mehrsprachig** – Deutsch, Englisch, Polnisch (zur Laufzeit umschaltbar)
- **Inkrementelles Backup** – Nur neue und geänderte Dateien werden kopiert
- **Dry-Run / Vorschau** – Zeigt vor dem Kopieren genau an, was passiert
- **Tägliches Logging** – Pro Tag eine Logdatei, mehrere Sessions werden angehängt
- **Konfigurierbar** – Quellpfade, Ausschlüsse, Vergleichsmethode, Sprache

---

## Schnellstart

### Voraussetzungen

- Python 3.9 oder neuer
- PySide6 (`pip install PySide6`)

### Starten

```bash
cd /pfad/zum/usb-stick
pip install -r requirements.txt
python3 main.py
```

Oder unter **Windows** Doppelklick auf `START_BACKUP.bat`,
unter **macOS** Doppelklick auf `START_BACKUP.command`.

### Erster Schritt

Beim ersten Start sind noch keine Quellordner konfiguriert.
Klicke auf **Einstellungen** → **Ordner hinzufügen** und wähle die Ordner aus, die gesichert werden sollen.

---

## Projektstruktur

```
USB-STICK/
├── main.py                     # Hauptprogramm (Einstiegspunkt)
├── build.py                    # Build-Skript für PyInstaller
├── requirements.txt            # Python-Abhängigkeiten
├── START_BACKUP.bat            # Windows-Starter (Doppelklick)
├── START_BACKUP.command        # macOS-Starter (Doppelklick)
│
├── core/                       # Kernlogik (kein GUI)
│   ├── config_manager.py       # Konfiguration laden / speichern
│   ├── i18n.py                 # Internationalisierung (Sprachen)
│   ├── diff_engine.py          # Dateivergleich (Scan / Vorschau)
│   ├── backup_engine.py        # Kopier-Prozess (QThread-Worker)
│   ├── logger.py               # Tägliche Logdateien
│   └── disk_info.py            # Speicherplatz-Informationen
│
├── gui/
│   └── main_window.py          # Hauptfenster + Einstellungsdialog
│
├── locales/                    # Sprachdateien (JSON)
│   ├── de.json                 # Deutsch
│   ├── en.json                 # Englisch
│   └── pl.json                 # Polnisch
│
├── Config/
│   └── config.json             # Benutzer-Einstellungen (persistent)
│
├── Backups/                    # Zielordner für Sicherungen
│   └── <Computername>/         # Automatisch pro Rechner
│
├── Logs/                       # Logdateien (eine pro Tag)
│   └── YYYY-MM-DD.log
│
└── trigger/                    # Auto-Start-Skripte
    ├── windows/
    │   ├── USB-Backup-Watcher.ps1
    │   └── setup_task_scheduler.ps1
    └── macos/
        ├── com.usb-backup.plist
        └── setup_trigger.sh
```

---

## Konfiguration

Die Datei `Config/config.json` wird beim Start geladen und kann über die GUI bearbeitet werden.

| Einstellung | Typ | Beschreibung |
|---|---|---|
| `language` | `"de"` / `"en"` / `"pl"` | Aktive Sprache |
| `sources` | `string[]` | Zu sichernde Quellordner |
| `target_subfolder` | `string` | Unterordner auf dem Stick (Standard: `"Backups"`) |
| `excludes` | `string[]` | Ausschlussmuster (z.B. `*.tmp`, `node_modules`) |
| `compare_method` | `"timestamp_size"` / `"hash"` | Vergleichsmethode für Änderungserkennung |
| `delete_removed` | `bool` | Spiegel-Modus: gelöschte Quelldateien auch im Ziel löschen (Standard: aus) |
| `auto_preview_on_start` | `bool` | Beim Öffnen automatisch scannen |

### Beispiel

```json
{
  "language": "de",
  "sources": [
    "C:\\Users\\Max\\Dokumente",
    "C:\\Users\\Max\\Desktop\\Projekte"
  ],
  "target_subfolder": "Backups",
  "excludes": ["*.tmp", "node_modules", "__pycache__", ".git"],
  "compare_method": "timestamp_size",
  "delete_removed": false,
  "auto_preview_on_start": true
}
```

---

## Backup-Logik

### Vergleichsmethoden

| Methode | Vergleicht | Geschwindigkeit | Genauigkeit |
|---|---|---|---|
| `timestamp_size` | Dateigröße + Änderungsdatum | Schnell | Gut (Standard) |
| `hash` | SHA-256 Prüfsumme | Langsam | Exakt |

### Datei-Aktionen

| Aktion | Bedeutung |
|---|---|
| **Neu** | Datei existiert nur in der Quelle → wird kopiert |
| **Aktualisiert** | Datei existiert in Quelle und Ziel, hat sich geändert → wird überschrieben |
| **Übersprungen** | Datei ist identisch → nichts passiert |
| **Fehler** | Datei konnte nicht gelesen werden → wird geloggt, Backup läuft weiter |

### Zielstruktur

```
Backups/
└── <Computername>/
    ├── Dokumente/           # Spiegel von Quellordner "Dokumente"
    │   ├── Bericht.pdf
    │   └── Notizen.txt
    └── Projekte/            # Spiegel von Quellordner "Projekte"
        └── app/
            └── main.py
```

---

## Logging

- **Pfad:** `Logs/YYYY-MM-DD.log`
- **Regel:** Pro Tag genau eine Datei. Mehrere Backups werden angehängt.
- **Inhalt:** Start-/Endzeit, Rechnername, Quell-/Zielpfade, jede kopierte Datei, Statistik, Fehler

### Beispiel

```
======================================================================
BACKUP SESSION START
  Timestamp : 2026-01-30T14:30:05.901778
  Computer  : DESKTOP-A1B2C3
  OS        : Windows 10
  Sources   : C:\Users\Max\Dokumente
  Target    : E:\Backups\DESKTOP-A1B2C3
----------------------------------------------------------------------
  [         COPIED] Dokumente/Bericht.pdf  (1.0 MB)
  [         COPIED] Dokumente/Notizen.txt  (2.0 KB)
  [        SKIPPED] Dokumente/alt.docx
----------------------------------------------------------------------
STATISTICS:
  Copied    : 2 files
  Skipped   : 1 files
  Errors    : 0
  Data      : 1.0 MB
  Duration  : 3.7s
BACKUP SESSION END: 2026-01-30T14:30:09.612345
======================================================================
```

---

## Automatischer Start beim Einstecken

### Windows

**Option 1 – WMI-Watcher (empfohlen, kein Admin nötig):**

```powershell
powershell -ExecutionPolicy Bypass -File "E:\trigger\windows\USB-Backup-Watcher.ps1"
```

Das Skript überwacht USB-Laufwerke und startet das Tool automatisch, wenn ein Stick mit `START_BACKUP.bat` erkannt wird.

Für permanenten Auto-Start: Verknüpfung im Windows-Autostart-Ordner anlegen (`shell:startup`).

**Option 2 – Task Scheduler (einmalig Admin nötig):**

```powershell
# Erhöhte PowerShell:
.\trigger\windows\setup_task_scheduler.ps1
```

**Fallback:** Doppelklick auf `START_BACKUP.bat`.

### macOS

**LaunchAgent (einmalig):**

```bash
chmod +x trigger/macos/setup_trigger.sh
./trigger/macos/setup_trigger.sh "MEIN-USB-STICK"
```

Dabei `MEIN-USB-STICK` durch den tatsächlichen Volume-Namen ersetzen (wie er unter `/Volumes/` erscheint).

**Deinstallation:**

```bash
launchctl unload ~/Library/LaunchAgents/com.usb-backup.plist
rm ~/Library/LaunchAgents/com.usb-backup.plist
```

**Fallback:** Doppelklick auf `START_BACKUP.command`.
Beim ersten Mal: Rechtsklick → *Öffnen* (wegen Gatekeeper).

---

## Portable EXE / Binary erstellen

```bash
pip install pyinstaller
python3 build.py
```

Ergebnis: `dist/USB-Backup-Tool.exe` (Windows) bzw. `dist/USB-Backup-Tool` (macOS).
Diese Datei auf den USB-Stick ins Hauptverzeichnis kopieren – fertig.

### Offline-Abhängigkeiten mitliefern

Falls auf dem Zielrechner kein Python installiert ist und kein Build möglich:

```bash
# Auf einem Online-Rechner:
pip download PySide6 -d ./offline_packages

# Auf dem Zielrechner:
pip install --no-index --find-links=./offline_packages PySide6
```

**Empfehlung:** Die PyInstaller-Variante verwenden – dann ist auf dem Zielrechner gar kein Python nötig.

---

## Neue Sprache hinzufügen

1. Datei `locales/xx.json` anlegen (Kopie von `de.json`)
2. Alle Werte übersetzen
3. Fertig – die Sprache erscheint automatisch im Menü

---

## Plattform-Hinweise

| Thema | Details |
|---|---|
| **Windows Autorun** | Seit Windows 7 für USB deaktiviert → WMI-Watcher oder Doppelklick |
| **macOS Gatekeeper** | Unsignierte Apps werden blockiert → Rechtsklick → Öffnen |
| **FAT32** | Max. 4 GB pro Datei, 2s Zeitstempel-Auflösung → exFAT empfohlen |
| **Admin-Rechte** | Für normalen Betrieb nicht nötig; nur Task-Scheduler-Setup braucht Elevation |
| **Execution Policy** | Windows PowerShell: `-ExecutionPolicy Bypass` verwenden |

---

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe [LICENSE](LICENSE).
