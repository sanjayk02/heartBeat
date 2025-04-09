@echo off
setlocal

:: === CONFIGURATION ===
set BASE_DIR=C:\stuff\source\pulse
set PYTHON="C:\Program Files\Python39\python.exe"
set REPORTER=%BASE_DIR%\idle_reporter.py
set SERVICE_SCRIPT=%BASE_DIR%\inactivity_service.py

:: === STEP 1: Ensure script folder exists ===
if not exist "%BASE_DIR%" (
    mkdir "%BASE_DIR%"
    echo Created script folder: %BASE_DIR%
)

:: === STEP 2: Install and start the service ===
echo Installing and starting Windows service...
%PYTHON% %SERVICE_SCRIPT% install
%PYTHON% %SERVICE_SCRIPT% start

:: === STEP 3: Register scheduled task for idle_reporter.py ===
echo Creating scheduled task for idle_reporter...
SCHTASKS /CREATE ^
 /SC ONLOGON ^
 /RL HIGHEST ^
 /TN "IdleReporter" ^
 /TR "\"C:\Program Files\Python39\pythonw.exe\" \"%REPORTER%\"" ^
 /F

:: === STEP 4: Launch test script ===
echo Launching test to verify status.txt and logging...
call "%BASE_DIR%\test_idle_reporter.bat"

echo.
echo Inactivity Monitor Setup Completed.
pause
