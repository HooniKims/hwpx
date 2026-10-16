#!/bin/bash
cd "$(dirname "$0")" || exit 1
export PATH="$PWD/.venv/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
if [[ ! -f .venv/bin/python || ! -f editor/studio-dist/index.html ]]; then
  echo '먼저 설치하기.command를 실행해 주세요.'
else
  node editor/cli.mjs start --browser
fi
read -r -p 'Enter 키를 누르면 닫힙니다. '
