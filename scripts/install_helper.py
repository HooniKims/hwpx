"""Read-only readiness check and explicit installation into this skill's .venv."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
VENV = ROOT / '.venv'
PYTHON = VENV / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
DOWNLOAD = 'https://github.com/HooniKims/hwpx/releases/download/installer-v1/hwpx-setup.zip'


def probe(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=20)
        return result.stdout.strip() if result.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def status():
    python = str(PYTHON) if PYTHON.exists() else sys.executable
    packages = probe([python, '-c', 'import lxml.etree, PIL, hwpx; print("ok")']) == 'ok'
    version = probe(['node', '--version']) or ''
    try:
        node = int(version.lstrip('v').split('.')[0]) >= 22
    except ValueError:
        node = False
    editor = (ROOT / 'editor/studio-dist/index.html').is_file() and (ROOT / 'editor/sdk').is_dir()
    return {'scope': 'execution_environment_only', 'python': python,
            'python_supported': sys.version_info >= (3, 10), 'packages': packages,
            'node22': node, 'editor': editor,
            'documents_ready': sys.version_info >= (3, 10) and packages and node,
            'editor_ready': sys.version_info >= (3, 10) and packages and node and editor,
            'download_url': DOWNLOAD}


def run(command, log):
    log.write('\n$ ' + ' '.join(map(str, command)) + '\n')
    log.flush()
    result = subprocess.run(list(map(str, command)), cwd=ROOT, stdout=log, stderr=log)
    if result.returncode:
        raise RuntimeError('설치 명령이 완료되지 않았습니다. install.log를 확인해 주세요.')


def install():
    if sys.version_info < (3, 10):
        raise RuntimeError('Python 3.10 이상이 필요합니다: https://www.python.org/downloads/')
    if not status()['node22']:
        raise RuntimeError('Node.js 22 이상을 설치한 뒤 설치하기를 다시 실행해 주세요: https://nodejs.org/en/download/')
    with (ROOT / 'install.log').open('a', encoding='utf-8') as log:
        print('[1/3] 문서 작업에 필요한 패키지를 준비합니다.', flush=True)
        if not PYTHON.exists():
            run([sys.executable, '-m', 'venv', VENV], log)
        if probe([str(PYTHON), '-c', 'import lxml.etree, PIL, hwpx; print("ok")']) != 'ok':
            run([PYTHON, '-m', 'pip', 'install', '--disable-pip-version-check',
                 '--timeout', '30', '--retries', '2', 'lxml', 'Pillow', 'python-hwpx'], log)
        print('[2/3] 에디터를 준비합니다. 인터넷 속도에 따라 몇 분 걸릴 수 있습니다.', flush=True)
        run([shutil.which('node'), ROOT / 'editor/setup.mjs'], log)
        print('[3/3] 설치 결과를 확인합니다.', flush=True)
        if not status()['editor_ready']:
            raise RuntimeError('필수 파일이 누락되었습니다. 설치하기를 다시 실행해 주세요.')
    print('설치 완료! 압축을 푼 폴더의 시작하기 파일을 열어 주세요.')
    print('채팅에 전달할 Python 경로: ' + str(PYTHON))
    print('이 설치는 채팅 앱에 스킬을 자동 등록하지 않습니다. installer/사용안내.md를 확인해 주세요.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.install:
        try:
            install()
        except (OSError, RuntimeError) as error:
            print('설치를 마치지 못했습니다: ' + str(error), file=sys.stderr)
            print('인터넷 연결과 안내를 확인한 뒤 다시 실행하면 준비된 항목은 재사용합니다.', file=sys.stderr)
            return 1
    else:
        print(json.dumps(status(), ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    sys.exit(main())
