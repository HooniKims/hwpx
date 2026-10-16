@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "PATH=%CD%\.venv\Scripts;%PATH%"
if not exist ".venv\Scripts\python.exe" goto missing
if not exist "editor\studio-dist\index.html" goto missing
node editor\cli.mjs start --browser
pause
exit /b
:missing
echo 먼저 설치하기.cmd를 실행해 주세요.
pause
