@echo off
chcp 65001 >nul
cd /d "%~dp0"
title ETS 2 (1.61) DualSense Full Support Suite

echo [1/4] Проверка и установка зависимостей Python...
pip install -r requirements.txt --quiet

echo.
echo [2/4] Генерация UI-мода и калибровка controls.sii...
python config_patcher.py

echo.
echo [3/4] Запуск Euro Truck Simulator 2...
tasklist /FI "IMAGENAME eq eurotrucks2.exe" 2>NUL | find /I /N "eurotrucks2.exe">NUL
if "%ERRORLEVEL%"=="1" (
    start "" "D:\....\Euro Truck Simulator 2\bin\win_x64\eurotrucks2.exe"
    echo [+] Игра запускается...
) else (
    echo [*] Игра уже запущена.
)

echo.
echo [4/4] Запуск ядра адаптивных курков, вибрации и гироскопа...
python dualsense_ets2.py
pause