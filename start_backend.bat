@echo off
title DocuGenie Backend Server (Port 8007)
cd /d "%~dp0backend"
echo Starting DocuGenie Backend Server on port 8007...
python main.py
pause
