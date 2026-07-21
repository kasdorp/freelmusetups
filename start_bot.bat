@echo off
rem === LMU Setup Bot launcher ===
cd /d "%~dp0"

if not exist ".env" (
    echo [!] Файл .env не найден. Скопируйте .env.example в .env и вставьте BOT_TOKEN.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo [*] Первый запуск: создаю виртуальное окружение и ставлю зависимости...
    py -m venv .venv
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
)

echo [*] Запускаю бота... (Ctrl+C — остановить)
".venv\Scripts\python.exe" bot.py
pause
