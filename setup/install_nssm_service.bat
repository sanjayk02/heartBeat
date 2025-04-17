@echo off
setlocal

:: === CONFIGURATION ===
set SERVICE_NAME=InactivityDetectorService
set NSSM_EXE=C:\stuff\source\PluseWork\heartBeat\app\nssm-2.24\win64\nssm.exe
set PYTHON_EXE="C:\Program Files\Python310\pythonw.exe"
set SCRIPT_PATH=C:\stuff\source\PluseWork\heartBeat\core\inactivity_service.py
set WORKING_DIR=C:\stuff\source\heartBeat\core
set LOG_DIR=C:\PulseProxy

:: === STEP 1: Validate NSSM exists ===
if not exist %NSSM_EXE% (
    echo ❌ ERROR: NSSM not found at %NSSM_EXE%
    echo Please install NSSM or update the path in this script.
    pause
    exit /b 1
)

:: === STEP 2: Create log directory if it doesn't exist ===
if not exist %LOG_DIR% (
    mkdir %LOG_DIR%
)

:: === STEP 3: Install the service via NSSM ===
echo 🛠 Installing service %SERVICE_NAME%...

%NSSM_EXE% install %SERVICE_NAME% %PYTHON_EXE% %SCRIPT_PATH%
%NSSM_EXE% set %SERVICE_NAME% AppDirectory %WORKING_DIR%
%NSSM_EXE% set %SERVICE_NAME% AppStdout %LOG_DIR%\service_out.log
%NSSM_EXE% set %SERVICE_NAME% AppStderr %LOG_DIR%\service_err.log
%NSSM_EXE% set %SERVICE_NAME% Start SERVICE_AUTO_START

echo ✅ Service %SERVICE_NAME% installed successfully.

:: === STEP 4: Start the service ===
echo ▶️ Starting the service...
net start %SERVICE_NAME%

echo.
echo ✅ Inactivity Detector Service installed and started successfully.
pause
