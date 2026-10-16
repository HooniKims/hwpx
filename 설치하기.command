#!/bin/bash
cd "$(dirname "$0")" || exit 1
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
if ! python3 -c 'import sys; assert sys.version_info >= (3,10)' >/dev/null 2>&1; then
  echo 'Python을 먼저 설치해 주세요. 설치 후 이 파일을 다시 열어 주세요.'
  open 'https://www.python.org/downloads/macos/'
elif ! node -e "if(Number(process.versions.node.split('.')[0])<22)process.exit(1)" >/dev/null 2>&1; then
  echo 'Node.js LTS를 설치한 뒤 이 파일을 다시 열어 주세요.'
  open 'https://nodejs.org/en/download/'
else
  python3 scripts/install_helper.py --install
fi
read -r -p 'Enter 키를 누르면 닫힙니다. '
