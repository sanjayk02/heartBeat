@echo off
setlocal

:: === CONFIGURATION ===
set SERVICE_NAME=Inactivity Detector Service
set BASE_DIR=C:\stuff\source\PulseWork\core
set PYTHON="C:\Program Files\Python310\python.exe"
set PYTHONW_PATH=C:\Program Files\Python310\pythonw.exe
set REPORTER=%BASE_DIR%\idle_reporter.py
set MONITOR=%BASE_DIR%\run_monitor.py
set SERVICE_SCRIPT=%BASE_DIR%\inactivity_service.py

:: === STEP 1: Ensure script folder exists ===
if not exist "%BASE_DIR%" (
    mkdir "%BASE_DIR%"
    echo Created script folder: %BASE_DIR%
)

:: === STEP 2: Install and start the service (auto startup) ===
echo.
echo Installing Windows service (auto startup)...
%PYTHON% %SERVICE_SCRIPT% --startup auto install

echo Starting Windows service...
%PYTHON% %SERVICE_SCRIPT% start

:: === STEP 3: Register scheduled task for idle_reporter.py ===
echo.
echo Checking for existing scheduled task "IdleReporter"...
SCHTASKS /Query /TN "IdleReporter" >nul 2>&1
IF %ERRORLEVEL%==0 (
    echo Scheduled task "IdleReporter" already exists. Skipping creation.
) ELSE (
    echo Creating scheduled task "IdleReporter"...
    SCHTASKS /CREATE ^
     /SC ONLOGON ^
     /RL HIGHEST ^
     /TN "IdleReporter" ^
     /TR "\"%PYTHONW_PATH%\" \"%REPORTER%\"" ^
     /RU "INTERACTIVE" ^
     /F
)

:: === STEP 4: Register scheduled task for run_monitor.py ===
echo.
echo Checking for existing scheduled task "RunMonitor"...
SCHTASKS /Query /TN "RunMonitor" >nul 2>&1
IF %ERRORLEVEL%==0 (
    echo Scheduled task "RunMonitor" already exists. Skipping creation.
) ELSE (
    echo Creating scheduled task "RunMonitor"...
    SCHTASKS /CREATE ^
     /SC ONLOGON ^
     /RL HIGHEST ^
     /TN "RunMonitor" ^
     /TR "\"%PYTHONW_PATH%\" \"%MONITOR%\"" ^
     /RU "INTERACTIVE" ^
     /F
)

:: === STEP 5: Check and run idle_reporter.py if not already running ===
echo.
echo Checking if idle_reporter.py is already running...
wmic process where "name='pythonw.exe'" get CommandLine | findstr /I /C:"%REPORTER%" >nul
if %ERRORLEVEL%==0 (
    echo idle_reporter.py is already running. Skipping launch.
) else (
    echo Starting idle_reporter.py...
    start "" "%PYTHONW_PATH%" "%REPORTER%"
)

:: === STEP 6: Check and run run_monitor.py if not already running ===
echo.
echo Checking if run_monitor.py is already running...
wmic process where "name='pythonw.exe'" get CommandLine | findstr /I /C:"%MONITOR%" >nul
if %ERRORLEVEL%==0 (
    echo run_monitor.py is already running. Skipping launch.
) else (
    echo Starting run_monitor.py...
    start "" "%PYTHONW_PATH%" "%MONITOR%"
)

echo.
echo Inactivity Monitor Setup Completed for %USERNAME%.
pause
