#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SITE_REPO="$(cd "$SCRIPT_DIR/.." && pwd)"
SPIDER_DIR="/Users/zhaobingkun/dev/Python/spider"
PYTHON_BIN="/Library/Frameworks/Python.framework/Versions/3.13/bin/python3"
PUBLISH_REMOTE="${CLUESBYSAM_GIT_REMOTE:-origin}"
PUBLISH_BRANCH="${CLUESBYSAM_GIT_BRANCH:-main}"

timestamp() {
  date "+%Y-%m-%d %H:%M:%S"
}

fail_if_site_repo_dirty() {
  local status
  status="$(git -C "$SITE_REPO" status --porcelain --untracked-files=all)"
  if [[ -n "$status" ]]; then
    printf '[%s] Site repo has uncommitted changes; refusing to overwrite or auto-commit them:\n%s\n' \
      "$(timestamp)" "$status" >&2
    exit 1
  fi
}

publish_site_repo() {
  local branch
  branch="$(git -C "$SITE_REPO" branch --show-current)"
  if [[ "$branch" != "$PUBLISH_BRANCH" ]]; then
    printf '[%s] Expected site repo branch %s, found %s; refusing to publish.\n' \
      "$(timestamp)" "$PUBLISH_BRANCH" "$branch" >&2
    exit 1
  fi

  git -C "$SITE_REPO" add --all
  if git -C "$SITE_REPO" diff --cached --quiet; then
    printf '[%s] No site changes to commit.\n' "$(timestamp)"
  else
    git -C "$SITE_REPO" commit -m "chore: sync daily Clues by Sam guides ($(date +%Y-%m-%d))"
    printf '[%s] Committed daily site sync.\n' "$(timestamp)"
  fi

  git -C "$SITE_REPO" push "$PUBLISH_REMOTE" "$PUBLISH_BRANCH"
  printf '[%s] Published site via %s/%s; Vercel will deploy the pushed commit.\n' \
    "$(timestamp)" "$PUBLISH_REMOTE" "$PUBLISH_BRANCH"
}

printf '\n[%s] Starting Clues by Sam daily sync and publish\n' "$(timestamp)"

if [[ ! -x "$PYTHON_BIN" ]]; then
  printf '[%s] Python binary not found or not executable: %s\n' "$(timestamp)" "$PYTHON_BIN" >&2
  exit 1
fi

if [[ ! -f "$SPIDER_DIR/cluesbysam.py" ]]; then
  printf '[%s] Spider script not found: %s\n' "$(timestamp)" "$SPIDER_DIR/cluesbysam.py" >&2
  exit 1
fi

fail_if_site_repo_dirty

if [[ -f "$SPIDER_DIR/cluesbysam.env" ]]; then
  set -a
  . "$SPIDER_DIR/cluesbysam.env"
  set +a
fi

cd "$SPIDER_DIR"
"$PYTHON_BIN" -u "$SPIDER_DIR/cluesbysam.py" "$@"

publish_site_repo
