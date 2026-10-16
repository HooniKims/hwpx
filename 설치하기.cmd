@echo off
chcp 65001 >nul
cd /d "%~dp0"
node -e "if(Number(process.versions.node.split('.')[0])<22)process.exit(1)" >nul 2>nul
if errorlevel 1 (
  echo Node.js LTS를 설치한 뒤 이 파일을 다시 실행해 주세요.
  start "" "https://nodejs.org/en/download/"
  goto done
)
py -3 -c "import sys; assert sys.version_info >= (3,10)" >nul 2>nul
if not errorlevel 1 (
  py -3 scripts\install_helper.py --install
  goto done
)
python -c "import sys; assert sys.version_info >= (3,10)" >nul 2>nul
if not errorlevel 1 (
  python scripts\install_helper.py --install
  goto done
)
echo Python을 먼저 설치한 뒤 이 파일을 다시 실행해 주세요.
start "" "https://www.python.org/downloads/windows/"
:done
pause
