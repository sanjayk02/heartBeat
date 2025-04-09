@echo off
setlocal

set BASE_DIR=C:\stuff\source\PulseWork\core
set PYTHON="C:\Program Files\Python39\pythonw.exe"
set MONITOR=%BASE_DIR%\run_monitor.py
set REPORTER=%BASE_DIR%\idle_reporter.py

echo Launching idle_reporter.py and run_monitor.py in parallel...

start "" %PYTHON% %REPORTER%
start "" %PYTHON% %MONITOR%

echo.
echo Both scripts started. Check logs in:
echo   %USERPROFILE%\InactivityDetector\
pause
REM End of file