@echo off
setlocal

:: === CONFIGURATION ===
set BASE_DIR=C:\stuff\source\heartBeat
set PYTHON="C:\Program Files\Python39\python.exe"
set SERVICE_SCRIPT=%BASE_DIR%\inactivity_service.py
set TASK_NAME=InactivityMonitorLauncher
set STARTUP_FOLDER=C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup
set VBS_FILE=launch_monitor.vbs

echo 🧹 Uninstalling Inactivity Monitor and cleaning up...

:: === Check if Python exists ===
if not exist %PYTHON% (
    echo ❌ ERROR: Python not found at %PYTHON%
    pause
    exit /b
)

:: === Stop and remove the service ===
echo ⏹ Stopping service (if running)...
%PYTHON% "%SERVICE_SCRIPT%" stop

echo ❌ Removing service...
%PYTHON% "%SERVICE_SCRIPT%" remove

:: === Remove Task Scheduler entry ===
echo ⏱ Removing scheduled task "%TASK_NAME%"...
SCHTASKS /DELETE /TN "%TASK_NAME%" /F >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Task "%TASK_NAME%" removed.
) else (
    echo ⚠️ No task named "%TASK_NAME%" found or already removed.
)

:: === Remove VBS launcher from Startup ===
echo 🧹 Removing VBS launcher from Startup folder...
if exist "%STARTUP_FOLDER%\%VBS_FILE%" (
    del "%STARTUP_FOLDER%\%VBS_FILE%"
    echo ✅ VBS launcher removed from Startup.
) else (
    echo ⚠️ VBS launcher not found in Startup folder.
)

echo.
echo ✅ Uninstallation complete.
pause
exit /b
