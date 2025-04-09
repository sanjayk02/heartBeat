@echo off
setlocal enabledelayedexpansion

:: ============================
::   Inactivity Monitor Setup
:: ============================
echo ========================================
echo    Inactivity Monitor Setup Script
echo ========================================

:: === CONFIGURATION ===
set BASE_DIR=C:\stuff\source\PulseWork\core
set BAT_FILE=C:\stuff\source\PulseWork\setup
set SERVICE_SCRIPT=%BASE_DIR%\inactivity_service.py
set REPORTER=%BASE_DIR%\idle_reporter.py
set MONITOR=%BASE_DIR%\run_monitor.py
set SERVICE_NAME=InactivityDetectorService
set TASK_NAME=IdleReporter
set LOG_DIR=%USERPROFILE%\InactivityDetector
set PYTHON="C:\Program Files\Python39\python.exe"
set PYTHONW="C:\Program Files\Python39\pythonw.exe"

:: === STEP 1: Ensure script folder exists ===
if not exist "%BASE_DIR%" (
    mkdir "%BASE_DIR%"
    echo Created script folder: %BASE_DIR%
)

:: === STEP 2: Install service if not already installed ===
echo Installing Windows service (if not already installed)...
%PYTHON% %SERVICE_SCRIPT% status >nul 2>&1
if errorlevel 1 (
    echo Service not found. Installing...

    :retry_install
    %PYTHON% %SERVICE_SCRIPT% install
    if errorlevel 1 (
        echo Waiting for previous deletion to complete...
        timeout /t 5 >nul
        goto retry_install
    )
) else (
    echo Windows service already installed.
)

:: === STEP 3: Ensure service is set to start automatically ===
echo Configuring service to start automatically...
sc config %SERVICE_NAME% start= auto >nul 2>&1

:: === STEP 4: Check if service is running ===
echo Checking service status...
for /f "tokens=3 delims=: " %%H in ('sc query %SERVICE_NAME% ^| findstr "STATE"') do (
    set STATE=%%H
)
if /i "!STATE!"=="RUNNING" (
    echo Service is already running. Skipping start.
) else (
    echo Service is installed but not running. Starting now...
    net start %SERVICE_NAME%
)

:: === STEP 5: Register scheduled task for idle_reporter.py ===
echo Creating scheduled task for idle_reporter...
SCHTASKS /CREATE ^
 /SC ONLOGON ^
 /RL HIGHEST ^
 /TN "%TASK_NAME%" ^
 /TR "\"%PYTHONW%\" \"%REPORTER%\"" ^
 /F >nul 2>&1

if errorlevel 1 (
    echo Failed to create scheduled task. Double-check paths and quotes.
) else (
    echo Scheduled task created successfully.
)

:: === STEP 6: Launch idle_reporter.py and run_monitor.py ===
echo Launching idle_reporter.py and run_monitor.py in parallel...
start "" %PYTHONW% %REPORTER%
start "" %PYTHONW% %MONITOR%

echo.
echo ========================================
echo Inactivity Monitor Setup Completed.
echo Check logs in: %LOG_DIR%
echo ========================================
pause
