@echo off
setlocal

REM Change context to the project root directory regardless of where script is run
cd /d "%~dp0\.."

echo ==============================================
echo Starting Optamo Movie Ratings Platform...
echo ==============================================

echo.
echo Starting Flask backend on port 5001 in a new window...
cd backend
start "Optamo Backend" cmd /c "call .venv\Scripts\activate.bat && python app.py"
cd ..

echo.
echo Starting Angular frontend on port 4200 in a new window...
cd frontend
start "Optamo Frontend" cmd /c "call npm run start"
cd ..

echo.
echo Application is starting! 
echo Keep the new command prompt windows open to run the servers.
echo Close those windows manually to stop the servers.
echo.
echo Frontend: http://localhost:4200
echo Backend : http://localhost:5001
echo API Docs: http://localhost:5001/apidocs/
echo.
pause
