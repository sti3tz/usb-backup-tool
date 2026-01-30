# Benutzerhandbuch – USB Backup Tool

Dieses Handbuch erklärt Schritt für Schritt, wie das USB Backup Tool verwendet wird.

---

## Inhaltsverzeichnis

1. [Erste Schritte](#1-erste-schritte)
2. [Die Benutzeroberfläche](#2-die-benutzeroberfläche)
3. [Einstellungen konfigurieren](#3-einstellungen-konfigurieren)
4. [Ein Backup durchführen](#4-ein-backup-durchführen)
5. [Automatischer Start beim Einstecken](#5-automatischer-start-beim-einstecken)
6. [Logs einsehen](#6-logs-einsehen)
7. [Portable EXE erstellen](#7-portable-exe-erstellen)
8. [Fehlerbehebung](#8-fehlerbehebung)
9. [Häufige Fragen (FAQ)](#9-häufige-fragen-faq)

---

## 1. Erste Schritte

### Was ist das USB Backup Tool?

Ein portables Programm, das auf einem USB-Stick lebt und ausgewählte Ordner
von jedem Rechner auf den Stick sichert. Es läuft unter Windows und macOS,
braucht keine Installation und keine Administrator-Rechte.

### Programm starten

**Windows:**
- USB-Stick einstecken
- Im Explorer den Stick öffnen
- Doppelklick auf `START_BACKUP.bat`
- Falls eine kompilierte Version vorhanden ist: `USB-Backup-Tool.exe`

**macOS:**
- USB-Stick einstecken
- Im Finder den Stick öffnen
- Doppelklick auf `START_BACKUP.command`
- Beim ersten Mal fragt macOS nach Erlaubnis → **Rechtsklick → Öffnen** wählen

**Aus dem Terminal (beide Plattformen):**

```bash
cd /pfad/zum/usb-stick
python3 main.py
```

### Erster Start – Quellordner einrichten

Beim allerersten Start sind noch keine Quellordner konfiguriert.
Das Programm zeigt einen Hinweis: *„Keine Quellordner konfiguriert"*.

So richtest du die Ordner ein:

1. Klicke auf **Einstellungen** (im oberen Bereich oder über das Menü)
2. Im Abschnitt **Quellordner** klicke auf **Ordner hinzufügen…**
3. Wähle den Ordner aus, den du sichern möchtest (z.B. `Dokumente`)
4. Wiederhole das für weitere Ordner
5. Klicke auf **OK**

Die Einstellungen werden automatisch auf dem Stick gespeichert.

---

## 2. Die Benutzeroberfläche

Das Hauptfenster ist in drei Bereiche aufgeteilt:

```
┌──────────────────────────────────────────────────────────┐
│  [Sprache ▼]                            [Einstellungen]  │
├──────────────┬───────────────────────────────────────────┤
│              │  [Quellen scannen]  [Einstellungen]       │
│  STICK-      │                                           │
│  STATUS      │  Backup-Vorschau                          │
│              │  ┌────────┬──────────────┬───────┬──────┐ │
│  Letztes     │  │ Aktion │ Dateipfad    │ Größe │ Dat. │ │
│  Backup:     │  ├────────┼──────────────┼───────┼──────┤ │
│  2026-01-30  │  │ Neu    │ Dok/neu.pdf  │ 2 MB  │ ...  │ │
│              │  │ Aktual. │ Dok/alt.doc │ 500KB │ ...  │ │
│  Zielordner: │  │ Übersp. │ Dok/ok.txt  │ 1 KB  │ ...  │ │
│  /Backups/PC │  └────────┴──────────────┴───────┴──────┘ │
│              │                                           │
│  Speicher:   │  Neu: 1 | Aktualisiert: 1 | Übersp.: 1   │
│  [████████░] │                                           │
│  3.2 GB frei │           [Abbrechen] [Backup starten]    │
│              │                                           │
│  Letztes Log:│  datei.pdf                                │
│  2026-01-30  │  [████████████████░░░░]  12 / 25 | 5MB/s │
├──────────────┴───────────────────────────────────────────┤
│  Bereit                                                  │
└──────────────────────────────────────────────────────────┘
```

### Linkes Panel – Stick-Status

- **Letztes Backup:** Datum und Ergebnis des letzten Backups
- **Zielordner:** Wohin die Dateien auf dem Stick gespeichert werden
- **Speicherplatz:** Fortschrittsbalken + Frei/Belegt/Gesamt
- **Letztes Log:** Name der letzten Logdatei

### Rechter Bereich – Vorschau und Aktionen

- **Quellen scannen:** Vergleicht Quelldateien mit dem Stick (Vorschau/Dry-Run)
- **Backup-Vorschau-Tabelle:** Zeigt für jede Datei, was passieren wird
- **Zusammenfassung:** Anzahl neuer, aktualisierter, übersprungener Dateien + Datenmenge
- **Backup starten:** Beginnt das Kopieren
- **Abbrechen:** Stoppt ein laufendes Backup
- **Fortschrittsbereich:** Aktueller Dateiname, Fortschrittsbalken, Geschwindigkeit

### Menüleiste

- **Sprache:** Zwischen Deutsch, Englisch und Polnisch wechseln
- **Einstellungen:** Öffnet den Einstellungsdialog

---

## 3. Einstellungen konfigurieren

Über **Einstellungen** (Button oder Menü) öffnet sich der Konfigurationsdialog.

### Quellordner

Liste der Ordner, die gesichert werden sollen.

- **Ordner hinzufügen…** – Öffnet einen Ordnerauswahl-Dialog
- **Entfernen** – Löscht den markierten Ordner aus der Liste

Du kannst beliebig viele Ordner hinzufügen. Jeder Ordner wird als eigener
Unterordner auf dem Stick gesichert:

```
Quellordner:  C:\Users\Max\Dokumente
              C:\Users\Max\Projekte

Ergebnis auf dem Stick:
  Backups/RECHNERNAME/Dokumente/…
  Backups/RECHNERNAME/Projekte/…
```

### Ausschlussmuster

Kommagetrennte Glob-Muster für Dateien und Ordner, die NICHT gesichert werden:

```
*.tmp, *.temp, Thumbs.db, .DS_Store, node_modules, __pycache__, .git
```

Die Muster werden geprüft gegen:
- Den Dateinamen (z.B. `*.tmp` trifft auf `notizen.tmp`)
- Den relativen Pfad (z.B. `logs/*.log`)
- Jede Verzeichnisebene (z.B. `node_modules` schließt den ganzen Ordner aus)

### Vergleichsmethode

| Methode | Beschreibung |
|---|---|
| **Zeitstempel + Größe** (Standard) | Schneller Vergleich über Dateigröße und Änderungsdatum. Gut für die meisten Fälle. |
| **SHA-256 Hash** | Berechnet eine Prüfsumme für jede Datei. Langsamer, aber erkennt auch Änderungen bei gleichem Datum/gleicher Größe. |

### Spiegel-Modus (Mirror Mode)

Wenn aktiviert, werden Dateien auf dem Stick gelöscht, die in der Quelle
nicht mehr existieren.

**Standardmäßig deaktiviert.** Nur aktivieren, wenn du ein exaktes Abbild willst.

### Automatisch scannen

Wenn aktiviert, startet die App beim Öffnen automatisch einen Scan und zeigt
die Vorschau an. Deaktiviere dies, wenn du zuerst die Einstellungen prüfen möchtest.

---

## 4. Ein Backup durchführen

### Schritt 1: Vorschau (Dry-Run)

1. Klicke auf **Quellen scannen**
2. Das Tool vergleicht alle Quelldateien mit dem Stick
3. Die Vorschau-Tabelle zeigt für jede Datei:

| Farbe | Aktion | Bedeutung |
|---|---|---|
| Grün | **Neu** | Datei existiert nur in der Quelle – wird kopiert |
| Orange | **Aktualisiert** | Datei hat sich geändert – wird überschrieben |
| Grau | **Übersprungen** | Datei ist identisch – nichts passiert |
| Rot | **Fehler** | Datei konnte nicht gelesen werden |

4. Unter der Tabelle steht eine Zusammenfassung:
   `Neu: 5 | Aktualisiert: 3 | Übersprungen: 120 | Daten: 45.2 MB`

### Schritt 2: Backup starten

1. Prüfe die Vorschau – alles in Ordnung?
2. Klicke auf **Backup starten**
3. Ein Bestätigungsdialog erscheint: *„X Dateien (Y MB) auf den USB-Stick kopieren?"*
4. Bestätige mit **Ja**

### Schritt 3: Fortschritt beobachten

Während des Backups siehst du:
- **Aktueller Dateiname** – welche Datei gerade kopiert wird
- **Fortschrittsbalken** – visueller Fortschritt
- **Zähler** – z.B. `12 / 45`
- **Geschwindigkeit** – z.B. `5.2 MB/s`

Du kannst jederzeit auf **Abbrechen** klicken. Bereits kopierte Dateien bleiben erhalten.

### Schritt 4: Ergebnis

Nach Abschluss erscheint ein Dialog mit:
- Anzahl kopierter Dateien
- Anzahl übersprungener Dateien
- Anzahl Fehler
- Gesamte Datenmenge
- Dauer

Wenn Fehler aufgetreten sind, findest du Details in der Logdatei.

---

## 5. Automatischer Start beim Einstecken

Das Tool kann sich automatisch öffnen, wenn der USB-Stick eingesteckt wird.

### Windows

#### Variante A: WMI-Watcher (empfohlen)

Ein PowerShell-Skript überwacht USB-Anschlüsse im Hintergrund:

```powershell
powershell -ExecutionPolicy Bypass -File "E:\trigger\windows\USB-Backup-Watcher.ps1"
```

**Dauerhaft einrichten:** Verknüpfung erstellen und in den Autostart-Ordner legen:
1. `Win+R` → `shell:startup` → Enter
2. Rechtsklick → Neue Verknüpfung
3. Ziel: `powershell -WindowStyle Hidden -ExecutionPolicy Bypass -File "E:\trigger\windows\USB-Backup-Watcher.ps1"`

> Kein Admin nötig.

#### Variante B: Task Scheduler

Einmalig in einer **erhöhten PowerShell** ausführen:

```powershell
.\trigger\windows\setup_task_scheduler.ps1
```

> Erfordert einmalig Admin-Rechte.

#### Fallback

Einfach `START_BACKUP.bat` per Doppelklick starten.

### macOS

#### LaunchAgent

Einmalig im Terminal ausführen:

```bash
cd /Volumes/MEIN-USB-STICK
chmod +x trigger/macos/setup_trigger.sh
./trigger/macos/setup_trigger.sh "MEIN-USB-STICK"
```

Ersetze `MEIN-USB-STICK` durch den tatsächlichen Namen des Sticks
(wie er im Finder / unter `/Volumes/` angezeigt wird).

**Deinstallieren:**

```bash
launchctl unload ~/Library/LaunchAgents/com.usb-backup.plist
rm ~/Library/LaunchAgents/com.usb-backup.plist
```

#### Fallback

`START_BACKUP.command` per Doppelklick starten.
Beim ersten Mal: Rechtsklick → **Öffnen** (Gatekeeper-Bestätigung).

---

## 6. Logs einsehen

### Wo liegen die Logs?

Im Ordner `Logs/` auf dem USB-Stick. Pro Tag gibt es eine Datei:

```
Logs/
├── 2026-01-28.log
├── 2026-01-29.log
└── 2026-01-30.log
```

### Was steht drin?

Jede Logdatei enthält eine oder mehrere **Sessions** (wenn am gleichen Tag
mehrere Backups liefen). Jede Session enthält:

- Start-Zeitpunkt, Rechnername, Betriebssystem
- Quell- und Zielpfade
- Liste aller kopierten / übersprungenen / fehlerhaften Dateien
- Statistik: Anzahl, Datenmenge, Dauer
- Fehlerdetails (falls vorhanden)

### Logs öffnen

Die Logdateien sind einfache Textdateien. Öffne sie mit:
- **Windows:** Notepad, Notepad++
- **macOS:** TextEdit, Terminal (`cat Logs/2026-01-30.log`)

---

## 7. Portable EXE erstellen

Damit das Tool **ohne Python** auf jedem Rechner läuft, kann eine
eigenständige Datei erstellt werden.

### Voraussetzungen

```bash
pip install pyinstaller
```

### Bauen

```bash
cd /pfad/zum/usb-stick
python3 build.py
```

### Ergebnis

- **Windows:** `dist/USB-Backup-Tool.exe`
- **macOS:** `dist/USB-Backup-Tool`

Die Datei ins Hauptverzeichnis des Sticks kopieren.
Ab jetzt braucht der Zielrechner kein Python mehr.

---

## 8. Fehlerbehebung

### „Python not found" beim Starten

Python 3.9+ ist nicht installiert oder nicht im PATH.
- **Lösung:** Python installieren oder die kompilierte EXE verwenden.

### „Keine Quellordner konfiguriert"

Es wurden noch keine Ordner zum Sichern ausgewählt.
- **Lösung:** Einstellungen öffnen → Ordner hinzufügen.

### „Nicht genügend Speicherplatz"

Die zu kopierenden Dateien passen nicht auf den Stick.
- **Lösung:** Stick aufräumen, größeren Stick verwenden, oder Quellordner einschränken.

### Dateien werden als „Fehler" angezeigt

Mögliche Ursachen:
- **Zugriff verweigert:** Die Datei ist gesperrt oder du hast keine Leserechte.
- **Pfad zu lang:** Besonders unter Windows bei tief verschachtelten Ordnern.
- **Datei wurde während des Scans verändert.**

→ Die Fehlerdateien werden übersprungen, das Backup läuft weiter. Details stehen im Log.

### macOS: „kann nicht geöffnet werden, da der Entwickler nicht verifiziert werden kann"

- **Lösung:** Rechtsklick auf die Datei → **Öffnen** → **Öffnen** bestätigen.
- Alternativ: `xattr -cr /Volumes/STICK/USB-Backup-Tool` im Terminal.

### Windows: PowerShell-Skript wird blockiert

- **Lösung:** Skript mit `-ExecutionPolicy Bypass` starten:
  ```powershell
  powershell -ExecutionPolicy Bypass -File "E:\trigger\windows\USB-Backup-Watcher.ps1"
  ```

---

## 9. Häufige Fragen (FAQ)

### Werden Dateien auf meinem Rechner verändert?

**Nein.** Das Tool liest nur von der Quelle und schreibt nur auf den Stick.
Am Rechner wird nichts verändert oder gelöscht.

### Werden Dateien auf dem Stick gelöscht?

**Standardmäßig nein.** Nur wenn der Spiegel-Modus in den Einstellungen
aktiviert wird, werden Dateien entfernt, die in der Quelle nicht mehr existieren.

### Kann ich den Stick an verschiedenen Rechnern verwenden?

**Ja.** Jeder Rechner bekommt automatisch einen eigenen Unterordner
(`Backups/<Computername>/`). Die Backups verschiedener Rechner stören sich nicht.

### Werden nur geänderte Dateien kopiert?

**Ja.** Das Tool vergleicht Quelle und Ziel. Identische Dateien werden
übersprungen. Nur neue und geänderte Dateien werden kopiert.

### Welches Dateisystem soll der Stick haben?

- **exFAT** (empfohlen): Funktioniert unter Windows und macOS, keine 4-GB-Grenze.
- **FAT32:** Kompatibel, aber max. 4 GB pro Datei und geringere Zeitstempel-Auflösung.
- **NTFS:** Nur unter Windows nativ beschreibbar; macOS kann nur lesen.
- **APFS/HFS+:** Nur unter macOS.

### Kann ich eine neue Sprache hinzufügen?

**Ja.** Kopiere eine vorhandene Datei (z.B. `locales/de.json`), benenne sie
um (z.B. `locales/fr.json`), übersetze alle Werte, und starte die App neu.
Die neue Sprache erscheint automatisch im Menü.

### Brauche ich Admin-Rechte?

**Nein** – für den normalen Betrieb nicht. Nur das Einrichten des
Windows Task Schedulers benötigt einmalig erhöhte Rechte.

### Was passiert bei einem Stromausfall / Abbruch?

Bereits vollständig kopierte Dateien bleiben auf dem Stick.
Eine halb kopierte Datei kann beschädigt sein – beim nächsten Backup
wird sie als „geändert" erkannt und erneut kopiert.
