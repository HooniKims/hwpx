"""hwpx 스킬의 새 버전이 GitHub 에 올라왔는지 확인해 알린다.

    python3 scripts/check_update.py          # 하루에 한 번만 원격을 조회한다
    python3 scripts/check_update.py --force  # 캐시를 무시하고 지금 조회한다

새 버전이 없거나, git 으로 받은 스킬이 아니거나, 네트워크가 안 되면 아무것도 출력하지 않는다.
스킬을 직접 갱신하지는 않는다(pull 여부는 사용자가 정한다).
"""

import json
import subprocess
import sys
import time
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
CACHE = Path.home() / ".cache" / "hwpx-skill" / "update-check.json"
DAY = 24 * 3600


def git(*args, timeout=10):
    r = subprocess.run(
        ["git", "-C", str(SKILL), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout,
    )
    return r.stdout.strip() if r.returncode == 0 else None


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if not (SKILL / ".git").exists():
        return
    head = git("rev-parse", "HEAD")
    upstream = git("rev-parse", "--abbrev-ref", "@{u}") or "origin/main"
    remote, _, branch = upstream.partition("/")
    if not head or not branch:
        return

    try:
        cache = json.loads(CACHE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        cache = {}
    fresh = time.time() - cache.get("checked", 0) < DAY and cache.get("head") == head
    if fresh and "--force" not in sys.argv:
        behind = cache.get("behind", [])
    else:
        line = git("ls-remote", remote, f"refs/heads/{branch}", timeout=8)
        if not line:
            return
        remote_sha = line.split()[0]
        behind = []
        if (
            remote_sha != head
            and git("fetch", "--quiet", remote, branch, timeout=60) is not None
        ):
            log = git("log", "--format=%s", f"{head}..FETCH_HEAD") or ""
            behind = [s for s in log.splitlines() if s]
            editor = git(
                "diff", "--quiet", head, "FETCH_HEAD", "--", "editor/prebuilt.json"
            )
            cache["editor"] = (
                editor is None
            )  # 차이가 있으면 git diff --quiet 가 1 을 돌려 None
        cache.update(checked=time.time(), head=head, behind=behind)
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")

    if not behind:
        return
    print(f"[hwpx 스킬 업데이트] 새 변경 {len(behind)}건이 GitHub 에 있다.")
    for s in behind[:8]:
        print(f"  - {s}")
    if len(behind) > 8:
        print(f"  … 외 {len(behind) - 8}건")
    print(f'받기: git -C "{SKILL}" pull')
    if cache.get("editor"):
        print(f'에디터도 바뀌었다. 받은 뒤: node "{SKILL / "editor" / "setup.mjs"}"')


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # 확인 실패가 문서 작업을 막으면 안 된다
