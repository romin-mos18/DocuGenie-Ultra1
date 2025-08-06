@echo off
echo Starting DocuGenie Ultra Backend...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set environment variables
set HOST=127.0.0.1
set PORT=8001

echo Running on http://%HOST%:%PORT%
echo.

REM Run the server
python -m uvicorn simple_app:app --host %HOST% --port %PORT% --log-level info

pause
