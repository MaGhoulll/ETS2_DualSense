@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"
title ETS 2 (1.61) DualSense Telemetry Suite

echo [1/4] Checking Python dependencies...
pip install -r requirements.txt --quiet --no-warn-script-location

echo.
echo [2/4] Running configuration patcher...
python config_patcher.py

echo.
echo [3/4] Checking Euro Truck Simulator 2 process...
tasklist /FI "IMAGENAME eq eurotrucks2.exe" 2>NUL | find /I /N "eurotrucks2.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [*] Game is already running.
    goto RUN_CORE
)

set "ETS2_PATH="
if exist "ets2_path.cfg" (
    set /p ETS2_PATH=<ets2_path.cfg
)

if not defined ETS2_PATH (
    for %%d in (C D E F G) do (
        if exist "%%d:\Steam\steamapps\common\Euro Truck Simulator 2\bin\win_x64\eurotrucks2.exe" (
            set "ETS2_PATH=%%d:\Steam\steamapps\common\Euro Truck Simulator 2\bin\win_x64\eurotrucks2.exe"
            goto LAUNCH_GAME
        )
    )
)

if not defined ETS2_PATH (
    for /f "tokens=2*" %%a in ('reg query "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Valve\Steam" /v InstallPath 2^>NUL') do set "STEAM_REG=%%b"
    if defined STEAM_REG (
        if exist "!STEAM_REG!\steamapps\common\Euro Truck Simulator 2\bin\win_x64\eurotrucks2.exe" (
            set "ETS2_PATH=!STEAM_REG!\steamapps\common\Euro Truck Simulator 2\bin\win_x64\eurotrucks2.exe"
            goto LAUNCH_GAME
        )
    )
)

if not defined ETS2_PATH (
    echo [!] Could not locate eurotrucks2.exe automatically.
    set /p "ETS2_PATH=Enter full path to eurotrucks2.exe (Without quotation marks): "
    set "ETS2_PATH=!ETS2_PATH:"=!"
)

:LAUNCH_GAME
if defined ETS2_PATH (
    if exist "!ETS2_PATH!" (
        echo !ETS2_PATH!> ets2_path.cfg
        start "" "!ETS2_PATH!"
        echo [+] Launching Euro Truck Simulator 2...
    ) else (
        echo [!] Path not found: !ETS2_PATH!
        echo [!] Please start the game manually.
    )
)

:RUN_CORE
echo.
echo [4/4] Starting DualSense telemetry core...
python dualsense_ets2.py
pause