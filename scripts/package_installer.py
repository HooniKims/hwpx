"""Build the downloadable ZIP from version-controlled source, preserving Mac launch permissions."""
import hashlib
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parent.parent


def main():
    output = ROOT / 'dist/hwpx-setup.zip'
    output.parent.mkdir(exist_ok=True)
    files = subprocess.check_output(
        ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT
    ).decode().split('\0')
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(set(filter(None, files))):
            path = ROOT / name
            if path.is_file() and not name.startswith(('.github/', 'dist/')):
                info = zipfile.ZipInfo('hwpx/' + name)
                info.create_system = 3
                mode = 0o100755 if name.endswith('.command') else 0o100644
                info.external_attr = mode << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                data = path.read_bytes()
                if name.endswith('.cmd'):
                    data = data.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
                archive.writestr(info, data)
    checksum = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix('.zip.sha256').write_text(checksum + '  hwpx-setup.zip\n')
    print(output)


if __name__ == '__main__':
    main()
