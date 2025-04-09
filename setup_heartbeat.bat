@echo off
setlocal ENABLEDELAYEDEXPANSION

:: ============================================================================
:: HeartBeat - Setup Script (Fixed Version)
:: ============================================================================

:: === CONFIGURATION ===
set BASE_DIR=C:\stuff\source\heartBeat
set SERVICE_SCRIPT=%BASE_DIR%\core\inactivity_service.py
set CHECK_SCRIPT=%BASE_DIR%\core\check_agents.py
set VBS_SOURCE=%BASE_DIR%\launch_monitor.vbs
set SCHEDULER_BAT=%BASE_DIR%\schedule_agent_checker.bat
set STARTUP_FOLDER=C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup
set SERVICE_NAME=InactivityMonitorService

:: === Python detection (local + network fallback) ===
set PYTHON_PATH_1=C:\stuff\source\.venv\Scripts\python.exe
set PYTHON_PATH_2=Z:\_Function\dev\users\sanjay\source\.venv\Scripts\python.exe
REM You can use UNC path instead of Z: if needed:
REM set PYTHON_PATH_2=\\YourServer\YourShare\_Function\dev\users\sanjay\source\.venv\Scripts\python.exe

set RETRY_COUNT=5
set PYTHON=

:find_python
if exist "%PYTHON_PATH_1%" (
    set "PYTHON=%PYTHON_PATH_1%"
) else if exist "%PYTHON_PATH_2%" (
    set "PYTHON=%PYTHON_PATH_2%"
) else (
    echo Waiting for Python path to become available...
    timeout /t 3 >nul
    set /A RETRY_COUNT-=1
    if !RETRY_COUNT! GTR 0 goto find_python

    echo ERROR: Python not found at either:
    echo     %PYTHON_PATH_1%
    echo     %PYTHON_PATH_2%
    pause
    exit /b
)

:: === HEADER ===
echo.
echo ===============================
echo  HeartBeat Setup Initialized
echo ===============================

:: === Validate service script ===
if not exist "%SERVICE_SCRIPT%" (
    echo ERROR: Service script not found at %SERVICE_SCRIPT%
    pause
    exit /b
)

:: === Run service check script ===
"%PYTHON%" "%CHECK_SCRIPT%"
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
"%PYTHON%" "%SERVICE_SCRIPT%" install

:: === Set to auto-start on boot ===
echo Configuring service to start automatically...
sc config %SERVICE_NAME% start= auto

:: === Start Service ===
echo Starting service...
"%PYTHON%" "%SERVICE_SCRIPT%" start
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
