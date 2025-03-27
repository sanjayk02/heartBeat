@echo off
setlocal

:: === CONFIGURATION ===
set BASE_DIR=C:\stuff\source\heartBeat
set PYTHON=C:\Program Files\Python39\python.exe
set PYTHONW=C:\Program Files\Python39\pythonw.exe
set REPORTER=%BASE_DIR%\idle_reporter.py
set MONITOR=%BASE_DIR%\run_monitor.py

echo 🔄 Launching idle_reporter.py and run_monitor.py in background...

:: === Check if Python exists ===
if not exist "%PYTHON%" (
    echo ❌ ERROR: Python not found at %PYTHON%
    exit /b
)

:: === Check if PythonW exists ===
if not exist "%PYTHONW%" (
    echo ❌ ERROR: pythonw.exe not found at %PYTHONW%
    exit /b
)

:: === Check if scripts exist ===
if not exist "%REPORTER%" (
    echo ❌ ERROR: idle_reporter.py not found in %BASE_DIR%
    exit /b
)

if not exist "%MONITOR%" (
    echo ❌ ERROR: run_monitor.py not found in %BASE_DIR%
    exit /b
)

:: === Launch idle_reporter silently ===
start "" "%PYTHONW%" "%REPORTER%"

:: === Wait for status.txt to be generated ===
timeout /t 5 >nul

:: === Launch run_monitor silently ===
start "" "%PYTHONW%" "%MONITOR%"

echo ✅ Both scripts launched silently using pythonw.exe
exit /b
