@echo off
chcp 65001 >nul
cd /d "%~dp0"
title ETS 2 (1.61) DualSense Full Support Suite

echo [1/4] Проверка и установка зависимостей Python...
pip install -r requirements.txt --quiet --no-warn-script-location

echo.
echo [2/4] Генерация UI-мода и калибровка controls.sii...
python config_patcher.py

echo.
echo [3/4] Поиск и запуск Euro Truck Simulator 2...

:: Проверяем, не запущен ли уже процесс игры
tasklist /FI "IMAGENAME eq eurotrucks2.exe" 2>NUL | find /I /N "eurotrucks2.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [*] Игра уже запущена. Пропускаем автозапуск.
    goto RUN_PYTHON_CORE
)

:: Пытаемся найти путь к игре через файл конфигурации, если он ранее сохранялся
set "ETS2_PATH="
if exist "ets2_path.cfg" (
    set /p ETS2_PATH=<ets2_path.cfg
)

:: Если путь не найден, ищем через стандартный путь Steam на диске C:, D: или E:
if not defined ETS2_PATH (
    for %%d in (C D E F G) do (
        if exist "%%d:\Steam\steamapps\common\Euro Truck Simulator 2\bin\win_x64\eurotrucks2.exe" (
            set "ETS2_PATH=%%d:\Steam\steamapps\common\Euro Truck Simulator 2\bin\win_x64\eurotrucks2.exe"
            goto SAVE_PATH
        )
    )
)

:: Если игра установлена в нестандартном месте (как у тебя на D:\GAMES\...), ищем её в реестре Steam
if not defined ETS2_PATH (
    for /f "tokens=2*" %%a in ('reg query "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Valve\Steam" /v InstallPath 2^>NUL') do set "STEAM_REG=%%b"
    if defined STEAM_REG (
        if exist "!STEAM_REG!\steamapps\common\Euro Truck Simulator 2\bin\win_x64\eurotrucks2.exe" (
            set "ETS2_PATH=!STEAM_REG!\steamapps\common\Euro Truck Simulator 2\bin\win_x64\eurotrucks2.exe"
            goto SAVE_PATH
        )
    )
)

:: Если игра всё еще не найдена автоматически, запрашиваем у пользователя вручную один раз
if not defined ETS2_PATH (
    echo [!] Автоматически найти eurotrucks2.exe не удалось.
    set /p "ETS2_PATH=Укажите полный путь к eurotrucks2.exe (или перетащите файл сюда): "
    set "ETS2_PATH=%ETS2_PATH:"=%"
)

:SAVE_PATH
:: Сохраняем найденный путь в конфиг, чтобы больше не спрашивать
if defined ETS2_PATH (
    if exist "%ETS2_PATH%" (
        echo %ETS2_PATH%> ets2_path.cfg
        start "" "%ETS2_PATH%"
        echo [+] Игра успешно запущена!
    ) else (
        echo [!] Указанный путь не найден: %ETS2_PATH%
        echo [!] Пропускаем запуск игры, запустите её вручную.
    )
)

:RUN_PYTHON_CORE
echo.
echo [4/4] Запуск ядра адаптивных курков, вибрации и гироскопа...
python dualsense_ets2.py
pause