# USB-Backup-Watcher.ps1
# ---------------------------------------------------------------
# Watches for USB removable-drive insertion via WMI events.
# When a drive with START_BACKUP.bat is detected, launches the tool.
#
# Usage (run once, keeps running in background):
#   powershell -ExecutionPolicy Bypass -File USB-Backup-Watcher.ps1
#
# To auto-start at login, create a shortcut in:
#   shell:startup  →  target: powershell -WindowStyle Hidden -ExecutionPolicy Bypass -File "<path>\USB-Backup-Watcher.ps1"
# ---------------------------------------------------------------

$query = @"
SELECT * FROM __InstanceCreationEvent WITHIN 3
WHERE TargetInstance ISA 'Win32_LogicalDisk'
  AND TargetInstance.DriveType = 2
"@

Write-Host "USB Backup Watcher active. Waiting for removable drives..."

Register-WmiEvent -Query $query -Action {
    $drive = $Event.SourceEventArgs.NewEvent.TargetInstance.DeviceID
    $batPath = Join-Path $drive "START_BACKUP.bat"
    if (Test-Path $batPath) {
        Write-Host "[$(Get-Date)] Backup stick detected on $drive – launching..."
        Start-Process -FilePath $batPath -WorkingDirectory $drive
    }
} | Out-Null

# Keep script alive
try {
    while ($true) { Start-Sleep -Seconds 60 }
} finally {
    Get-EventSubscriber | Unregister-Event
}
