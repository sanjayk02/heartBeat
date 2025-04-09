@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   Fast Uninstall - Inactivity Monitor
echo ========================================

:: === CONFIG ===
set SERVICE_NAME=InactivityDetectorService
set TASK_NAME=IdleReporter
set LOG_DIR=%USERPROFILE%\InactivityDetector

:: === Stop and delete service ===
echo Stopping and deleting service: %SERVICE_NAME%
sc stop %SERVICE_NAME% >nul 2>&1
sc delete %SERVICE_NAME% >nul 2>&1

:: === Remove scheduled task ===
echo Removing scheduled task: %TASK_NAME%
SCHTASKS /DELETE /TN "%TASK_NAME%" /F >nul 2>&1

:: === Kill background scripts ===
echo Terminating idle_reporter and run_monitor...

powershell -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*idle_reporter.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"
powershell -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*run_monitor.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"

:: === Remove log directory (optional) ===
echo Deleting logs in: %LOG_DIR%
rmdir /S /Q "%LOG_DIR%" >nul 2>&1

:: === Done ===
echo.
echo ========================================
echo Inactivity Monitor Removed Instantly.
echo ========================================
pause
