# === CONFIGURATION ===
$BaseDir = "C:\stuff\source\PulseWork\core"
$BatDir = "C:\stuff\source\PulseWork\setup"
$Python = "C:\Program Files\Python310\python.exe"
$PythonW = "C:\Program Files\Python310\pythonw.exe"
$Reporter = Join-Path $BaseDir "idle_reporter.py"
$ServiceScript = Join-Path $BaseDir "inactivity_service.py"

# === STEP 1: Ensure script folder exists ===
if (-Not (Test-Path $BaseDir)) {
    New-Item -Path $BaseDir -ItemType Directory | Out-Null
    Write-Output "Created script folder: $BaseDir"
}

# === STEP 2: Install and start the service ===
Write-Output "Installing and starting Windows service..."
& $Python $ServiceScript install
& $Python $ServiceScript start

# === STEP 3: Register scheduled task for idle_reporter.py ===
Write-Output "Creating scheduled task for idle_reporter..."
$taskName = "IdleReporter"
$taskPath = "`"$PythonW`" `"$Reporter`""

# Delete task if it exists
if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

Register-ScheduledTask `
    -Action (New-ScheduledTaskAction -Execute $PythonW -Argument "`"$Reporter`"") `
    -Trigger (New-ScheduledTaskTrigger -AtLogOn) `
    -Principal (New-ScheduledTaskPrincipal -UserId "SYSTEM" -RunLevel Highest) `
    -TaskName $taskName `
    -Description "Runs idle_reporter.py at logon" `
    -Force

# === STEP 4: Launch test script ===
$TestScript = Join-Path $BatDir "test_idle_reporter.bat"
if (Test-Path $TestScript) {
    Write-Output "Launching test script..."
    & $TestScript
} else {
    Write-Output "Test script not found: $TestScript"
}

Write-Output "`nInactivity Monitor Setup Completed."
Pause
