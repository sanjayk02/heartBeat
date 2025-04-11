@echo off
setlocal

set SERVICE_NAME=InactivityDetectorService
set TASK_NAME=IdleReporter
set LOG_DIR=%USERPROFILE%\InactivityDetector

echo 🔄 Uninstalling Inactivity Monitor components...

:: === Stop and remove the Windows Service ===
echo ❌ Stopping and deleting service: %SERVICE_NAME%
sc stop %SERVICE_NAME% >nul 2>&1
sc delete %SERVICE_NAME% >nul 2>&1

:: === Remove scheduled task ===
echo ❌ Removing scheduled task: %TASK_NAME%
SCHTASKS /DELETE /TN "%TASK_NAME%" /F >nul 2>&1

:: === Optionally remove user logs ===
echo 🗑️ Deleting logs and status from: %LOG_DIR%
rmdir /S /Q "%LOG_DIR%" >nul 2>&1

echo.
echo ✅ Uninstallation complete.
pause
REM End of file