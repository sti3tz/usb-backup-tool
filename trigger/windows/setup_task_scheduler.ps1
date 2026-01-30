# setup_task_scheduler.ps1
# ---------------------------------------------------------------
# Alternative: create a Task Scheduler entry that runs the watcher
# at user logon.  Requires elevated (Admin) shell for initial setup.
# ---------------------------------------------------------------

param(
    [string]$WatcherPath = (Join-Path $PSScriptRoot "USB-Backup-Watcher.ps1")
)

$TaskName = "USB-Backup-Watcher"

# Remove old version if it exists
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

$action  = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$WatcherPath`""

$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Watches for USB Backup stick and launches the backup tool."

Write-Host ""
Write-Host "Task '$TaskName' registered.  It will start the watcher at every logon."
Write-Host "To remove:  Unregister-ScheduledTask -TaskName '$TaskName'"
