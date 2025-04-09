@echo off
setlocal

:: ============================================================================
:: HeartBeat - Uninstall Script
:: ============================================================================
:: This script stops and removes the Inactivity Monitor Windows Service and
:: deletes any related scheduled tasks (e.g., IdleReporter).
::
:: Must be run as Administrator.
:: ============================================================================

:: === CONFIGURATION ===
set BASE_DIR=C:\stuff\source\heartBeat
set PYTHON="C:\stuff\source\.venv\Scripts\python.exe"
set SERVICE_SCRIPT=%BASE_DIR%\core\inactivity_service.py
set SERVICE_NAME=InactivityMonitorService

echo.
echo ================================
echo Uninstalling HeartBeat Service...
echo ================================

:: === Check if Python exists ===
if not exist %PYTHON% (
    echo ERROR: Python not found at %PYTHON%
    pause
    exit /b
)

:: === Check if service script exists ===
if not exist "%SERVICE_SCRIPT%" (
    echo ERROR: Service script not found at %SERVICE_SCRIPT%
    pause
    exit /b
)

:: === Stop the service ===
echo Stopping service (if running)...
%PYTHON% "%SERVICE_SCRIPT%" stop

:: === Remove the service ===
echo Removing service...
%PYTHON% "%SERVICE_SCRIPT%" remove

:: === Remove from Task Scheduler (if registered there) ===
echo Removing scheduled task (if exists)...
SCHTASKS /DELETE /TN "IdleReporter" /F >NUL 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✓ Task 'IdleReporter' removed.
) else (
    echo No scheduled task named 'IdleReporter' found.
)

:: === Remove VBS launcher from Startup (optional) ===
set STARTUP_FOLDER=C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup
set VBS_FILE=%STARTUP_FOLDER%\launch_monitor.vbs

if exist "%VBS_FILE%" (
    del "%VBS_FILE%"
    echo ✓ Removed VBS launcher from Startup folder.
) else (
    echo No VBS launcher found in Startup folder.
)

:: === Done ===
echo.
echo  Uninstallation complete.
pause
exit /b
