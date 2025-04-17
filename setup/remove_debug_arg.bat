@echo off
setlocal enabledelayedexpansion

:: === CONFIGURATION ===
set SERVICE_NAME=InactivityDetectorService
set NSSM_EXE=C:\stuff\source\PluseWork\heartBeat\app\nssm-2.24\win64\nssm.exe
set PYTHON_EXE="C:\Program Files\Python310\pythonw.exe"
set SCRIPT_PATH=C:\stuff\source\heartBeat\core\inactivity_service.py

:: === STEP 1: Validate NSSM path ===
if not exist %NSSM_EXE% (
    echo ❌ ERROR: NSSM not found at:
    echo     %NSSM_EXE%
    echo Please check the path or place nssm.exe there.
    pause
    exit /b 1
)

:: === STEP 2: Stop the service ===
echo 🛑 Stopping service "%SERVICE_NAME%"...
net stop "%SERVICE_NAME%" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Service was not running or could not be stopped.
) else (
    echo ✅ Service stopped.
)

:: === STEP 3: Update NSSM arguments (remove debug) ===
echo 🔧 Updating NSSM AppParameters...
%NSSM_EXE% set "%SERVICE_NAME%" Application %PYTHON_EXE%
%NSSM_EXE% set "%SERVICE_NAME%" AppParameters "%SCRIPT_PATH%"
echo ✅ Service parameters updated.

:: === STEP 4: Start the service again ===
echo ▶️  Starting service "%SERVICE_NAME%"...
net start "%SERVICE_NAME%"
if %ERRORLEVEL% EQU 0 (
    echo ✅ Service started successfully.
) else (
    echo ❌ Failed to start the service. Please check logs.
)

echo.
echo 🎯 NSSM service cleaned and restarted without 'debug' argument.
pause
