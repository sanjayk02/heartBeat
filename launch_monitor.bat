@echo off
setlocal

:: ============================================================================
:: HeartBeat - Agent + Tray Silent Launcher
:: ============================================================================
:: This script silently launches the InactivityTracker.py agent and TrayApp.py
:: system tray GUI using pythonw.exe (no visible command prompt window).
::
:: Must be run with access to the correct Python environment.
:: ============================================================================

:: === CONFIGURATION ===
set BASE_DIR=C:\stuff\source\heartBeat
set PYTHONW="C:\stuff\source\.venv\Scripts\pythonw.exe"
set AGENT=%BASE_DIR%\core\InactivityTracker.py
set TRAY=%BASE_DIR%\core\TrayApp.py

echo.
echo Starting HeartBeat agent and tray...

:: === Validate pythonw.exe exists ===
if not exist %PYTHONW% (
    echo ERROR: pythonw.exe not found at %PYTHONW%
    pause
    exit /b
)

:: === Check if agent script exists ===
if not exist "%AGENT%" (
    echo ERROR: InactivityTracker.py not found at %AGENT%
    pause
    exit /b
)

:: === Check if tray script exists ===
if not exist "%TRAY%" (
    echo ERROR: TrayApp.py not found at %TRAY%
    pause
    exit /b
)

:: === Launch agent silently ===
start "" %PYTHONW% "%AGENT%"

:: === Launch tray app silently ===
start "" %PYTHONW% "%TRAY%"

echo  Both scripts launched silently using pythonw.exe
exit /b
