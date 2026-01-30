"""
Hauptfenster der Anwendung – gesamte grafische Oberfläche.

Enthält das ``MainWindow`` (QMainWindow) mit:
    - Menüleiste (Sprache, Einstellungen)
    - Linkes Status-Panel (letztes Backup, Zielordner, Speicherplatz, Log)
    - Rechter Inhaltsbereich (Vorschau-Tabelle, Aktionsbuttons, Fortschritt)
    - Statusleiste

Sowie den ``SettingsDialog`` (QDialog) zum Bearbeiten der Konfiguration.
"""

from __future__ import annotations

import platform
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QActionGroup, QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.backup_engine import BackupWorker, ScanWorker
from core.config_manager import ConfigManager
from core.diff_engine import DiffEngine, FileAction
from core.disk_info import DiskUsage, get_disk_usage
from core.i18n import I18n
from core.logger import BackupLogger


# ======================================================================
#  Hauptfenster
# ======================================================================
class MainWindow(QMainWindow):
    """Hauptfenster der Backup-Anwendung.

    Verwaltet die gesamte Benutzeroberfläche sowie die Interaktion
    mit den Kern-Komponenten (Config, i18n, Logger, DiffEngine, Workers).
    """

    def __init__(self, app_root: Path):
        super().__init__()
        self.app_root = app_root

        # Kern-Komponenten initialisieren
        self.config = ConfigManager(app_root / "Config" / "config.json")
        self.i18n = I18n(app_root / "locales", self.config.get("language", "de"))
        self.logger = BackupLogger(app_root / "Logs")

        # Zustand
        self.entries: list = []
        self.backup_worker: BackupWorker | None = None
        self.scan_worker: ScanWorker | None = None

        self.setMinimumSize(800, 600)
        self.resize(
            self.config.get("window_width", 1000),
            self.config.get("window_height", 700),
        )

        self._build_ui()
        self._retranslate()
        self._update_status_panel()

        # Auto-scan on start if configured
        if self.config.get("auto_preview_on_start") and self.config.get("sources"):
            self._on_scan()

    # ------------------------------------------------------------------
    #  Oberfläche aufbauen
    # ------------------------------------------------------------------
    def _build_ui(self):
        """Gesamte Benutzeroberfläche aufbauen."""
        self._build_menu()

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(10)

        self._build_status_panel()
        root.addWidget(self.status_panel, 0)

        self._build_content_area()
        root.addWidget(self.content_widget, 1)

        self.status_label = QLabel()
        self.statusBar().addWidget(self.status_label, 1)

    # --- Menüleiste ---------------------------------------------------
    def _build_menu(self):
        """Menüleiste mit Sprachauswahl und Einstellungen erstellen."""
        menubar = self.menuBar()
        self.lang_menu = menubar.addMenu("")
        self.lang_group = QActionGroup(self)
        self.lang_group.setExclusive(True)

        for code, name in self.i18n.available_languages():
            act = QAction(name, self)
            act.setCheckable(True)
            act.setData(code)
            if code == self.i18n.language:
                act.setChecked(True)
            act.triggered.connect(lambda _checked, c=code: self._change_language(c))
            self.lang_group.addAction(act)
            self.lang_menu.addAction(act)

        self.settings_action = menubar.addAction("")
        self.settings_action.triggered.connect(self._open_settings)

    # --- Linke Seitenleiste -------------------------------------------
    def _build_status_panel(self):
        """Status-Panel (links): letztes Backup, Ziel, Speicher, Log."""
        self.status_panel = QGroupBox()
        self.status_panel.setFixedWidth(260)
        vl = QVBoxLayout(self.status_panel)

        self.lbl_last_backup_h = QLabel()
        self.lbl_last_backup_h.setStyleSheet("font-weight:bold")
        self.lbl_last_backup_v = QLabel()
        self.lbl_last_backup_v.setWordWrap(True)
        vl.addWidget(self.lbl_last_backup_h)
        vl.addWidget(self.lbl_last_backup_v)
        vl.addSpacing(12)

        self.lbl_target_h = QLabel()
        self.lbl_target_h.setStyleSheet("font-weight:bold")
        self.lbl_target_v = QLabel()
        self.lbl_target_v.setWordWrap(True)
        vl.addWidget(self.lbl_target_h)
        vl.addWidget(self.lbl_target_v)
        vl.addSpacing(12)

        self.lbl_disk_h = QLabel()
        self.lbl_disk_h.setStyleSheet("font-weight:bold")
        self.disk_bar = QProgressBar()
        self.disk_bar.setTextVisible(True)
        self.lbl_disk_detail = QLabel()
        self.lbl_disk_detail.setWordWrap(True)
        vl.addWidget(self.lbl_disk_h)
        vl.addWidget(self.disk_bar)
        vl.addWidget(self.lbl_disk_detail)
        vl.addSpacing(12)

        self.lbl_log_h = QLabel()
        self.lbl_log_h.setStyleSheet("font-weight:bold")
        self.lbl_log_v = QLabel()
        self.lbl_log_v.setWordWrap(True)
        vl.addWidget(self.lbl_log_h)
        vl.addWidget(self.lbl_log_v)

        vl.addStretch()

    # --- Rechter Inhaltsbereich ---------------------------------------
    def _build_content_area(self):
        """Inhaltsbereich (rechts): Buttons, Vorschau-Tabelle, Fortschritt."""
        self.content_widget = QWidget()
        vl = QVBoxLayout(self.content_widget)
        vl.setContentsMargins(0, 0, 0, 0)

        # Toolbar row
        hl = QHBoxLayout()
        self.btn_scan = QPushButton()
        self.btn_scan.clicked.connect(self._on_scan)
        self.btn_settings = QPushButton()
        self.btn_settings.clicked.connect(self._open_settings)
        hl.addWidget(self.btn_scan)
        hl.addWidget(self.btn_settings)
        hl.addStretch()
        vl.addLayout(hl)

        # Preview heading
        self.lbl_preview = QLabel()
        self.lbl_preview.setStyleSheet("font-weight:bold; font-size:14px")
        vl.addWidget(self.lbl_preview)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setAlternatingRowColors(True)
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        vl.addWidget(self.table, 1)

        # Summary label
        self.lbl_summary = QLabel()
        vl.addWidget(self.lbl_summary)

        # Action buttons
        hl2 = QHBoxLayout()
        hl2.addStretch()
        self.btn_cancel = QPushButton()
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self._on_cancel)
        self.btn_backup = QPushButton()
        self.btn_backup.setEnabled(False)
        self.btn_backup.clicked.connect(self._on_start_backup)
        self.btn_backup.setStyleSheet("font-weight:bold; padding:8px 20px")
        hl2.addWidget(self.btn_cancel)
        hl2.addWidget(self.btn_backup)
        vl.addLayout(hl2)

        # Progress section
        self.lbl_progress_file = QLabel()
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.lbl_progress_stats = QLabel()
        vl.addWidget(self.lbl_progress_file)
        vl.addWidget(self.progress_bar)
        vl.addWidget(self.lbl_progress_stats)

    # ------------------------------------------------------------------
    #  Sprachumschaltung
    # ------------------------------------------------------------------
    def _retranslate(self):
        """Alle UI-Texte mit der aktuellen Sprache aktualisieren."""
        t = self.i18n.t
        self.setWindowTitle(t("app_title"))
        self.lang_menu.setTitle(t("menu_language"))
        self.settings_action.setText(t("menu_settings"))
        self.status_panel.setTitle(t("status_panel_title"))
        self.lbl_last_backup_h.setText(t("last_backup"))
        self.lbl_target_h.setText(t("target_folder"))
        self.lbl_disk_h.setText(t("disk_space"))
        self.lbl_log_h.setText(t("last_log"))
        self.btn_scan.setText(t("btn_scan"))
        self.btn_settings.setText(t("btn_settings"))
        self.lbl_preview.setText(t("preview_title"))
        self.table.setHorizontalHeaderLabels(
            [t("col_action"), t("col_path"), t("col_size"), t("col_modified")]
        )
        self.btn_backup.setText(t("btn_start_backup"))
        self.btn_cancel.setText(t("btn_cancel"))
        self.status_label.setText(t("statusbar_ready"))

    def _change_language(self, lang_code: str):
        """Sprache wechseln, Config speichern und UI aktualisieren."""
        self.i18n.load(lang_code)
        self.config.set("language", lang_code)
        self.config.save()
        self._retranslate()
        self._update_status_panel()
        if self.entries:
            self._populate_table()

    # ------------------------------------------------------------------
    #  Status-Panel aktualisieren
    # ------------------------------------------------------------------
    def _get_target_path(self) -> Path:
        """Zielpfad auf dem Stick: Backups/<Computername>/."""
        return (
            self.app_root
            / self.config.get("target_subfolder", "Backups")
            / platform.node()
        )

    def _update_status_panel(self):
        """Daten im linken Status-Panel aktualisieren."""
        t = self.i18n.t

        info = self.logger.get_last_session_info()
        if info:
            parts = [info.get("date", "-")]
            if info.get("timestamp"):
                parts.append(info["timestamp"][:19])
            if info.get("copied"):
                parts.append(f"{t('result_copied')}: {info['copied']}")
            self.lbl_last_backup_v.setText("\n".join(parts))
        else:
            self.lbl_last_backup_v.setText(t("last_backup_none"))

        self.lbl_target_v.setText(str(self._get_target_path()))

        usage = get_disk_usage(self.app_root)
        self.disk_bar.setMaximum(100)
        self.disk_bar.setValue(int(usage.used_percent))
        self.disk_bar.setFormat(f"{usage.used_percent:.1f}%")
        self.lbl_disk_detail.setText(
            f"{t('disk_free')}: {DiskUsage.format_size(usage.free)}\n"
            f"{t('disk_used')}: {DiskUsage.format_size(usage.used)}\n"
            f"{t('disk_total')}: {DiskUsage.format_size(usage.total)}"
        )

        self.lbl_log_v.setText(info.get("log_file", "-") if info else "-")

    # ------------------------------------------------------------------
    #  Scan (Vorschau / Dry-Run)
    # ------------------------------------------------------------------
    def _on_scan(self):
        """Quellordner scannen und Vorschau-Tabelle befüllen."""
        sources = self.config.get("sources", [])
        if not sources:
            QMessageBox.warning(
                self, self.i18n.t("app_title"), self.i18n.t("error_no_sources")
            )
            return

        self.btn_scan.setEnabled(False)
        self.btn_backup.setEnabled(False)
        self.table.setRowCount(0)
        self.lbl_summary.setText("")
        self.status_label.setText(self.i18n.t("statusbar_scanning"))

        diff = DiffEngine(
            compare_method=self.config.get("compare_method", "timestamp_size"),
            excludes=self.config.get("excludes", []),
        )

        self.scan_worker = ScanWorker(diff, sources, self._get_target_path())
        self.scan_worker.progress.connect(
            lambda f: self.lbl_progress_file.setText(f)
        )
        self.scan_worker.finished_scan.connect(self._on_scan_finished)
        self.scan_worker.error.connect(
            lambda e: QMessageBox.critical(self, "Error", e)
        )
        self.scan_worker.start()

    def _on_scan_finished(self, entries: list):
        """Scan abgeschlossen – Tabelle befüllen, Backup-Button aktivieren."""
        self.entries = entries
        self._populate_table()
        self.btn_scan.setEnabled(True)

        actionable = [
            e for e in entries if e.action in (FileAction.NEW, FileAction.UPDATED)
        ]
        self.btn_backup.setEnabled(len(actionable) > 0)
        self.lbl_progress_file.setText("")
        self.status_label.setText(self.i18n.t("statusbar_ready"))

    # ------------------------------------------------------------------
    #  Vorschau-Tabelle befüllen
    # ------------------------------------------------------------------
    def _populate_table(self):
        """Vorschau-Tabelle mit den Scan-Ergebnissen befüllen."""
        t = self.i18n.t
        names = {
            FileAction.NEW: t("action_new"),
            FileAction.UPDATED: t("action_updated"),
            FileAction.SKIPPED: t("action_skipped"),
            FileAction.ERROR: t("action_error"),
        }
        colors = {
            FileAction.NEW: QColor(0, 140, 0),
            FileAction.UPDATED: QColor(190, 140, 0),
            FileAction.SKIPPED: QColor(140, 140, 140),
            FileAction.ERROR: QColor(200, 0, 0),
        }

        self.table.setRowCount(len(self.entries))
        counts = {a: 0 for a in FileAction}
        total_copy_size = 0

        for i, entry in enumerate(self.entries):
            # Action
            item = QTableWidgetItem(names.get(entry.action, "?"))
            item.setForeground(colors.get(entry.action, QColor(0, 0, 0)))
            self.table.setItem(i, 0, item)
            # Path
            self.table.setItem(i, 1, QTableWidgetItem(str(entry.relative_path)))
            # Size
            sz = DiskUsage.format_size(entry.source_size) if entry.source_size else "-"
            self.table.setItem(i, 2, QTableWidgetItem(sz))
            # Modified
            if entry.source_mtime > 0:
                mt = datetime.fromtimestamp(entry.source_mtime).strftime(
                    "%Y-%m-%d %H:%M"
                )
            else:
                mt = "-"
            self.table.setItem(i, 3, QTableWidgetItem(mt))

            counts[entry.action] = counts.get(entry.action, 0) + 1
            if entry.action in (FileAction.NEW, FileAction.UPDATED):
                total_copy_size += entry.source_size

        parts = [
            f"{names[FileAction.NEW]}: {counts[FileAction.NEW]}",
            f"{names[FileAction.UPDATED]}: {counts[FileAction.UPDATED]}",
            f"{names[FileAction.SKIPPED]}: {counts[FileAction.SKIPPED]}",
        ]
        if counts[FileAction.ERROR]:
            parts.append(f"{names[FileAction.ERROR]}: {counts[FileAction.ERROR]}")
        parts.append(f"{t('result_data')}: {DiskUsage.format_size(total_copy_size)}")
        self.lbl_summary.setText("  |  ".join(parts))

    # ------------------------------------------------------------------
    #  Backup durchführen
    # ------------------------------------------------------------------
    def _on_start_backup(self):
        """Backup starten: Speicherplatz prüfen, bestätigen, Worker starten."""
        t = self.i18n.t
        actionable = [
            e for e in self.entries
            if e.action in (FileAction.NEW, FileAction.UPDATED)
        ]
        if not actionable:
            return

        total_size = sum(e.source_size for e in actionable)
        usage = get_disk_usage(self.app_root)
        if total_size > usage.free:
            QMessageBox.warning(
                self, t("app_title"), t("error_insufficient_space")
            )
            return

        reply = QMessageBox.question(
            self,
            t("confirm_backup"),
            t(
                "confirm_backup_msg",
                count=len(actionable),
                size=DiskUsage.format_size(total_size),
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        # Lock UI
        self.btn_scan.setEnabled(False)
        self.btn_backup.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(actionable))
        self.progress_bar.setValue(0)
        self.status_label.setText(t("statusbar_backing_up"))

        self.logger.start_session(
            self.config.get("sources", []), str(self._get_target_path())
        )

        self.backup_worker = BackupWorker(self.entries)
        self.backup_worker.progress.connect(self._on_backup_progress)
        self.backup_worker.file_done.connect(self._on_file_done)
        self.backup_worker.speed_update.connect(self._on_speed_update)
        self.backup_worker.finished_backup.connect(self._on_backup_finished)
        self.backup_worker.start()

    def _on_backup_progress(self, current: int, total: int, filename: str):
        """Fortschrittsbalken und Dateiname aktualisieren."""
        self.progress_bar.setValue(current)
        self.lbl_progress_file.setText(filename)
        self.lbl_progress_stats.setText(f"{current} / {total}")

    def _on_file_done(self, filename: str, status: str, size: int):
        """Einzelne Datei-Aktion ins Log schreiben."""
        action_str = "COPIED" if status == "OK" else status
        self.logger.log_file(filename, action_str, size)

    def _on_speed_update(self, bps: float):
        """Geschwindigkeitsanzeige aktualisieren."""
        speed = DiskUsage.format_size(int(bps)) + "/s"
        base = self.lbl_progress_stats.text().split(" | ")[0]
        self.lbl_progress_stats.setText(f"{base} | {speed}")

    def _on_cancel(self):
        """Laufendes Backup abbrechen."""
        if self.backup_worker and self.backup_worker.isRunning():
            self.backup_worker.cancel()

    def _on_backup_finished(self, stats: dict):
        """Backup abgeschlossen – Ergebnis-Dialog anzeigen, Log abschließen."""
        t = self.i18n.t
        self.logger.end_session(stats)

        # Unlock UI
        self.btn_scan.setEnabled(True)
        self.btn_backup.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.lbl_progress_file.setText("")
        self.lbl_progress_stats.setText("")
        self.status_label.setText(t("statusbar_done"))
        self._update_status_panel()

        # Result dialog
        title = (
            t("result_success")
            if stats.get("errors", 0) == 0
            else t("result_with_errors")
        )
        msg = (
            f"{t('result_copied')}: {stats.get('copied', 0)}\n"
            f"{t('result_skipped')}: {stats.get('skipped', 0)}\n"
            f"{t('result_errors')}: {stats.get('errors', 0)}\n"
            f"{t('result_data')}: {DiskUsage.format_size(stats.get('bytes_copied', 0))}\n"
            f"{t('result_duration')}: {stats.get('duration', 0):.1f}s"
        )
        if stats.get("cancelled"):
            msg += f"\n\n{t('backup_cancelled')}"
        QMessageBox.information(self, title, msg)

    # ------------------------------------------------------------------
    #  Einstellungsdialog
    # ------------------------------------------------------------------
    def _open_settings(self):
        """Einstellungsdialog öffnen und bei OK die Config speichern."""
        dlg = SettingsDialog(self.config, self.i18n, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.config.save()
            self._retranslate()
            self._update_status_panel()

    # ------------------------------------------------------------------
    #  Fenster-Lebenszyklus
    # ------------------------------------------------------------------
    def closeEvent(self, event):
        """Beim Schließen: Fenstergröße speichern, laufendes Backup abbrechen."""
        self.config.set("window_width", self.width())
        self.config.set("window_height", self.height())
        self.config.save()
        if self.backup_worker and self.backup_worker.isRunning():
            self.backup_worker.cancel()
            self.backup_worker.wait(5000)
        event.accept()


# ======================================================================
#  Einstellungsdialog
# ======================================================================
class SettingsDialog(QDialog):
    """Dialog zum Bearbeiten der Backup-Einstellungen.

    Ermöglicht das Hinzufügen/Entfernen von Quellordnern,
    Ausschlussmuster, Vergleichsmethode und weitere Optionen.
    """

    def __init__(self, config: ConfigManager, i18n: I18n, parent=None):
        super().__init__(parent)
        self.config = config
        self.i18n = i18n
        t = i18n.t

        self.setWindowTitle(t("settings_title"))
        self.setMinimumWidth(520)
        layout = QVBoxLayout(self)

        # -- Source folders --
        layout.addWidget(QLabel(f"<b>{t('settings_sources')}</b>"))
        src_row = QHBoxLayout()
        self.source_list = QListWidget()
        for s in config.get("sources", []):
            self.source_list.addItem(s)
        src_row.addWidget(self.source_list)

        src_btns = QVBoxLayout()
        btn_add = QPushButton(t("settings_add_source"))
        btn_add.clicked.connect(self._add_source)
        btn_rm = QPushButton(t("settings_remove_source"))
        btn_rm.clicked.connect(self._remove_source)
        src_btns.addWidget(btn_add)
        src_btns.addWidget(btn_rm)
        src_btns.addStretch()
        src_row.addLayout(src_btns)
        layout.addLayout(src_row)

        # -- Excludes --
        layout.addWidget(QLabel(f"<b>{t('settings_excludes')}</b>"))
        self.excludes_edit = QLineEdit()
        self.excludes_edit.setText(", ".join(config.get("excludes", [])))
        self.excludes_edit.setPlaceholderText("*.tmp, node_modules, .git")
        layout.addWidget(self.excludes_edit)

        # -- Options --
        form = QFormLayout()
        self.compare_combo = QComboBox()
        self.compare_combo.addItem(t("settings_compare_ts"), "timestamp_size")
        self.compare_combo.addItem(t("settings_compare_hash"), "hash")
        idx = self.compare_combo.findData(
            config.get("compare_method", "timestamp_size")
        )
        if idx >= 0:
            self.compare_combo.setCurrentIndex(idx)
        form.addRow(t("settings_compare_method"), self.compare_combo)

        self.chk_delete = QCheckBox(t("settings_delete_removed"))
        self.chk_delete.setChecked(config.get("delete_removed", False))
        form.addRow("", self.chk_delete)

        self.chk_auto = QCheckBox(t("settings_auto_preview"))
        self.chk_auto.setChecked(config.get("auto_preview_on_start", True))
        form.addRow("", self.chk_auto)

        layout.addLayout(form)

        # -- Buttons --
        bbox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        bbox.accepted.connect(self._save_and_accept)
        bbox.rejected.connect(self.reject)
        layout.addWidget(bbox)

    def _add_source(self):
        """Ordnerauswahl-Dialog öffnen und Quellpfad hinzufügen."""
        path = QFileDialog.getExistingDirectory(
            self, self.i18n.t("settings_add_source")
        )
        if path:
            self.source_list.addItem(path)

    def _remove_source(self):
        """Markierten Quellpfad aus der Liste entfernen."""
        row = self.source_list.currentRow()
        if row >= 0:
            self.source_list.takeItem(row)

    def _save_and_accept(self):
        """Alle Einstellungen in die Config übernehmen und Dialog schließen."""
        sources = [
            self.source_list.item(i).text()
            for i in range(self.source_list.count())
        ]
        self.config.set("sources", sources)
        excludes = [
            e.strip() for e in self.excludes_edit.text().split(",") if e.strip()
        ]
        self.config.set("excludes", excludes)
        self.config.set("compare_method", self.compare_combo.currentData())
        self.config.set("delete_removed", self.chk_delete.isChecked())
        self.config.set("auto_preview_on_start", self.chk_auto.isChecked())
        self.accept()
