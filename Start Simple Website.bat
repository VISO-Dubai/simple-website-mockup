@echo off
title Simple Lighting - local website server
cd /d "%~dp0site"
echo.
echo  Simple Lighting website is running at:  http://localhost:8765
echo  Keep this window open while you browse. Close it to stop the website.
echo.
start "" "http://localhost:8765/index.html"
where python >nul 2>nul && (python -m http.server 8765 --bind 127.0.0.1) || (py -m http.server 8765 --bind 127.0.0.1)
pause
