@echo off
title DocuGenie Frontend Server (Port 3006)
cd /d "%~dp0frontend"
echo Starting DocuGenie Frontend Server on port 3006...
npm run dev -- --port 3006
pause
