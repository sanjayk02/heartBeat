@echo off
setlocal ENABLEDELAYEDEXPANSION

:: ============================================================================
:: HeartBeat - Agent Checker Scheduler
:: ============================================================================
:: This script registers a Windows Scheduled Task to run check_agents.py
:: every hour for the currently logged-in user. It uses pythonw.exe to avoid
:: showing a terminal window.
::
:: Can be called manually or by setup_heartbeat.bat
:: ============================================================================

:: === CONFIGURATION ===
set BASE_DIR=C:\stuff\source\heartBeat
set SCRIPT_PATH=%BASE_DIR%\core\check_agents.py
set PYTHONW="C:\stuff\source\.venv\Scripts\pythonw.exe"
set TASK_NAME=Check_Heartbeat_Agent

echo.
echo Setting up agent checker task...

:: === Check if pythonw.exe exists ===
if not exist %PYTHONW% (
    echo ERROR: pythonw.exe not found at %PYTHONW%
    pause
    exit /b
)

:: === Check if checker script exists ===
if not exist "%SCRIPT_PATH%" (
    echo ERROR: check_agents.py not found at %SCRIPT_PATH%
    pause
    exit /b
)

:: === Register Scheduled Task ===
SCHTASKS /Create ^
 /TN "%TASK_NAME%" ^
 /TR "%PYTHONW% \"%SCRIPT_PATH%\"" ^
 /SC HOURLY ^
 /RL LIMITED ^
 /F >nul 2>&1

if %ERRORLEVEL% EQU 0 (
    echo Scheduled task '%TASK_NAME%' created successfully.
) else (
    echo Task '%TASK_NAME%' may already exist or failed to create.
)

:: === Done ===
exit /b
