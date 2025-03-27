@echo off
setlocal

:: === CONFIGURATION ===
set BASE_DIR=C:\stuff\source\heartBeat
set PYTHON="C:\Program Files\Python39\python.exe"
set CHECK_SCRIPT=%BASE_DIR%\check_setup.py
set SERVICE_SCRIPT=%BASE_DIR%\inactivity_service.py
set LAUNCHER_BAT=%BASE_DIR%\launch_monitor.bat
set SERVICE_NAME=InactivityMonitorService
set TASK_NAME=InactivityMonitorLauncher
set VBS_SOURCE=%BASE_DIR%\launch_monitor.vbs
set STARTUP_FOLDER=C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup

echo.
echo 🔍 Checking if service and task are already installed...

:: === Run the check using Python script ===
%PYTHON% "%CHECK_SCRIPT%"
if %ERRORLEVEL% NEQ 0 (
    echo ✅ Service and scheduled task already exist. Skipping installation.
    echo 📂 You can still check logs in: %%USERPROFILE%%\InactivityLogs\
    pause
    exit /b
)

echo.
echo 🛠 Installing and starting the Inactivity Monitor Windows Service...

:: === Check if Python exists ===
if not exist %PYTHON% (
    echo ❌ ERROR: Python not found at %PYTHON%
    pause
    exit /b
)

:: === Check if service script exists ===
if not exist "%SERVICE_SCRIPT%" (
    echo ❌ ERROR: Service script not found at %SERVICE_SCRIPT%
    pause
    exit /b
)

:: === Install the service ===
echo 🔧 Installing service...
%PYTHON% "%SERVICE_SCRIPT%" install

:: === Start the service ===
echo ▶️ Starting service...
%PYTHON% "%SERVICE_SCRIPT%" start

:: === Register launch_monitor.bat for current user ===
if exist "%LAUNCHER_BAT%" (
    echo 🧠 Registering launcher in Task Scheduler...
    SCHTASKS /CREATE /TN "%TASK_NAME%" ^
    /SC ONLOGON ^
    /TR "\"%LAUNCHER_BAT%\"" ^
    /RL HIGHEST ^
    /F
    echo ✅ Launcher registered successfully.
) else (
    echo ⚠️ Launcher not found at %LAUNCHER_BAT%
)

:: === Deploy VBS to Global Startup Folder for All Users ===
if exist "%VBS_SOURCE%" (
    echo 🚀 Copying launch_monitor.vbs to global Startup folder...
    copy /Y "%VBS_SOURCE%" "%STARTUP_FOLDER%"
    echo ✅ VBS launcher copied to: %STARTUP_FOLDER%
) else (
    echo ⚠️ VBS launcher not found at %VBS_SOURCE%. Skipping startup deployment.
)

echo.
echo ✅ All setup completed!
echo 📁 Logs will appear in: %%USERPROFILE%%\InactivityLogs\
pause
exit /b
