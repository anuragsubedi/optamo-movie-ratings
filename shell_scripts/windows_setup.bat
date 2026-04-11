@echo off
setlocal

REM Change context to the project root directory regardless of where script is run
cd /d "%~dp0\.."

echo ==============================================
echo Optamo Setup Script for Windows
echo ==============================================

echo.
echo [1/2] Setting up Python backend...
cd backend
python -m venv .venv
call .venv\Scripts\activate.bat
pip install -r requirements.txt
echo Running data migration (this may take ~60 seconds)...
python migrate.py
cd ..

echo.
echo [2/2] Setting up Angular frontend...
cd frontend
call npm install
cd ..

echo.
echo Setup complete! You can now start the application by running: shell_scripts\windows_run.bat
pause
