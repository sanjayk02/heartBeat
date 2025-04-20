@echo off
setlocal

:: === CONFIGURATION ===
set SERVICE_NAME=InactivityDetectorService
set DISPLAY_NAME="Inactivity Detector Service"
set BASE_DIR=C:\stuff\source\PluseWork\heartBeat\core
set PYTHON="C:\python\python310\python.exe"
set PYTHONW_PATH="C:\python\python310\pythonw.exe"
set NSSM=C:\stuff\source\PluseWork\heartBeat\app\nssm-2.24\win64\nssm.exe
set REPORTER=%BASE_DIR%\idle_reporter.py
set MONITOR=%BASE_DIR%\run_monitor.py
set SERVICE_SCRIPT=%BASE_DIR%\inactivity_service.py
set SERVICE_LOG_DIR=C:\PulseProxy

:: === STEP 0: Verify NSSM is available ===
if not exist "%NSSM%" (
    echo ERROR: NSSM not found at %NSSM%
    pause
    exit /b 1
)

:: === STEP 1: Ensure folders exist ===
if not exist "%BASE_DIR%" mkdir "%BASE_DIR%"
if not exist "%SERVICE_LOG_DIR%" mkdir "%SERVICE_LOG_DIR%"

:: === STEP 2: Uninstall previous instance if exists ===
echo Checking if existing service exists...
sc query "%SERVICE_NAME%" >nul 2>&1
IF %ERRORLEVEL%==0 (
    echo Removing existing service...
    net stop "%SERVICE_NAME%" >nul 2>&1
    %NSSM% remove "%SERVICE_NAME%" confirm
    timeout /t 2 >nul
)

:: === STEP 3: Install service with NSSM ===
echo Installing new NSSM service...
%NSSM% install "%SERVICE_NAME%" "%PYTHONW_PATH%" "%SERVICE_SCRIPT%"
%NSSM% set "%SERVICE_NAME%" DisplayName %DISPLAY_NAME%
%NSSM% set "%SERVICE_NAME%" AppDirectory "%BASE_DIR%"
%NSSM% set "%SERVICE_NAME%" AppStdout "%SERVICE_LOG_DIR%\service_out.log"
%NSSM% set "%SERVICE_NAME%" AppStderr "%SERVICE_LOG_DIR%\service_err.log"
%NSSM% set "%SERVICE_NAME%" Start SERVICE_AUTO_START
echo Service "%SERVICE_NAME%" installed successfully.

:: === STEP 4: Start service ===
echo Starting service...
net start "%SERVICE_NAME%"

:: === STEP 5: Register scheduled tasks ===
echo Checking for existing scheduled task "IdleReporter"...
SCHTASKS /Query /TN "IdleReporter" >nul 2>&1
IF %ERRORLEVEL%==0 (
    echo Scheduled task "IdleReporter" already exists. Skipping.
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

echo Checking for existing scheduled task "RunMonitor"...
SCHTASKS /Query /TN "RunMonitor" >nul 2>&1
IF %ERRORLEVEL%==0 (
    echo Scheduled task "RunMonitor" already exists. Skipping.
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

:: === STEP 6: Start scripts if not already running ===
echo Checking if idle_reporter.py is running...
wmic process where "name='pythonw.exe'" get CommandLine | findstr /I /C:"%REPORTER%" >nul
IF %ERRORLEVEL%==0 (
    echo idle_reporter.py already running.
) ELSE (
    echo Launching idle_reporter.py...
    start "" "%PYTHONW_PATH%" "%REPORTER%"
)

echo Checking if run_monitor.py is running...
wmic process where "name='pythonw.exe'" get CommandLine | findstr /I /C:"%MONITOR%" >nul
IF %ERRORLEVEL%==0 (
    echo run_monitor.py already running.
) ELSE (
    echo Launching run_monitor.py...
    start "" "%PYTHONW_PATH%" "%MONITOR%"
)

echo.
echo Inactivity Monitor Setup Completed for %USERNAME%.
pause
