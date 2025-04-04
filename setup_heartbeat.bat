@echo off
setlocal ENABLEDELAYEDEXPANSION

:: ============================================================================
:: HeartBeat - Setup Script
:: ============================================================================
:: This batch script automates the setup for the HeartBeat user inactivity
:: monitoring system. It:
::
:: 1. Verifies Python exists.
:: 2. Checks if the inactivity service is already installed.
:: 3. If not installed:
::    - Installs the Windows service.
::    - Configures it to auto-start on system boot.
::    - Starts the service.
::    - Deploys a VBS launcher to the Startup folder (for launching the agent).
::    - Schedules an hourly task to monitor the agent.
:: 4. Logs the install time.
::
:: Must be run as Administrator.
:: ============================================================================

:: === CONFIGURATION ===
set BASE_DIR=C:\stuff\source\heartBeat
set PYTHON="C:\stuff\source\.venv\Scripts\pythonw.exe"
set SERVICE_SCRIPT=%BASE_DIR%\core\inactivity_service.py
set CHECK_SCRIPT=%BASE_DIR%\core\check_agents.py
set VBS_SOURCE=%BASE_DIR%\launch_monitor.vbs
set SCHEDULER_BAT=%BASE_DIR%\schedule_agent_checker.bat
set STARTUP_FOLDER=C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup
set SERVICE_NAME=InactivityMonitorService

:: === HEADER ===
echo.
echo ===============================
echo  HeartBeat Setup Initialized
echo ===============================

:: === Validate Python exists ===
if not exist %PYTHON% (
    echo ERROR: Python not found at %PYTHON%
    pause
    exit /b
)

:: === Validate service script ===
if not exist "%SERVICE_SCRIPT%" (
    echo ERROR: Service script not found at %SERVICE_SCRIPT%
    pause
    exit /b
)

:: === Run service check script ===
%PYTHON% "%CHECK_SCRIPT%"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Service and agent already installed. Skipping setup.
    echo Check logs in: %%USERPROFILE%%\InactivityLogs\
    pause
    exit /b
)

:: === Install Service ===
echo.
echo Installing HeartBeat service...
%PYTHON% "%SERVICE_SCRIPT%" install

:: === Set to auto-start on boot ===
echo Configuring service to start automatically...
sc config %SERVICE_NAME% start= auto

:: === Start Service ===
echo Starting service...
%PYTHON% "%SERVICE_SCRIPT%" start
if %ERRORLEVEL% EQU 0 (
    echo Service started successfully.
) else (
    echo ERROR: Failed to start service.
)

:: === Deploy VBS launcher to Startup ===
if exist "%VBS_SOURCE%" (
    echo.
    echo  Deploying launch_monitor.vbs to Startup folder...
    copy /Y "%VBS_SOURCE%" "%STARTUP_FOLDER%"
    echo VBS deployed to: %STARTUP_FOLDER%
) else (
    echo WARNING: VBS launcher not found at %VBS_SOURCE%. Skipping.
)

:: === Schedule agent checker task ===
if exist "%SCHEDULER_BAT%" (
    echo.
    echo Scheduling hourly agent checker task...
    call "%SCHEDULER_BAT%"
) else (
    echo WARNING: schedule_agent_checker.bat not found at %SCHEDULER_BAT%. Skipping.
)

:: === Log install time ===
echo Installed on %DATE% %TIME% >> "%BASE_DIR%\install_log.txt"

:: === Done ===
echo.
echo Setup complete! Logs will be stored in:
echo     %%USERPROFILE%%\InactivityLogs\
echo Service will start automatically at boot.
pause
exit /b
