@echo off
setlocal

:: === CONFIGURATION ===
set SERVICE_NAME=InactivityDetectorService
set TASK_NAME=IdleReporter
set TASK_NAME_2=RunMonitor
set NSSM=C:\stuff\source\PluseWork\heartBeat\app\nssm-2.24\win64\nssm.exe
set LOG_DIR=C:\Users\Public\InactivityService

echo.
echo Uninstalling Inactivity Monitor Components...

:: === Stop and Remove NSSM Service ===
sc query "%SERVICE_NAME%" >nul 2>&1
if %ERRORLEVEL%==0 (
    echo Stopping service: %SERVICE_NAME%
    net stop "%SERVICE_NAME%" >nul 2>&1
    echo Removing service with NSSM...
    "%NSSM%" remove "%SERVICE_NAME%" confirm
) else (
    echo Service not found. Skipping removal.
)

:: === Remove scheduled tasks ===
echo Removing scheduled task: %TASK_NAME%
SCHTASKS /DELETE /TN "%TASK_NAME%" /F >nul 2>&1

echo Removing scheduled task: %TASK_NAME_2%
SCHTASKS /DELETE /TN "%TASK_NAME_2%" /F >nul 2>&1

:: === Kill background scripts ===
echo Terminating idle_reporter and run_monitor...

powershell -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*idle_reporter.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"
powershell -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*run_monitor.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"

:: === Optional: Delete log directory ===
echo Deleting logs at: %LOG_DIR%
rmdir /S /Q "%LOG_DIR%" >nul 2>&1

:: === Done ===
echo.
echo ========================================
echo Inactivity Monitor Removed Instantly.
echo ========================================
pause
