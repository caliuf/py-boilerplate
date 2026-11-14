#!/usr/bin/env bash
# finish-task.sh — chiude il loop: commit → push → PR.
#
# Gli hook in .githooks/ eseguono già `just precommit` al commit e
# `just prepush` al push: non vengono duplicati qui. Se un gate fallisce,
# l'hook interrompe commit/push e questo script si ferma.
#
# Usage:
#   tools/scripts/finish-task.sh                 commit staged, push, open PR
#   tools/scripts/finish-task.sh --all           stage everything first (git add -A)
#   tools/scripts/finish-task.sh -m "msg"        use this message instead of tmp/commit-message.md
set -euo pipefail

stage_all=0
message=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --all) stage_all=1; shift ;;
    -m|--message) message="${2:?missing message}"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

branch=$(git branch --show-current)
if [ -z "$branch" ]; then
  echo "Error: detached HEAD — check out a branch first." >&2
  exit 1
fi
if [ "$branch" = "main" ]; then
  echo "Error: on main. The default flow is one task = one branch = one PR." >&2
  echo "Create a branch first (see docs/development/WORKFLOWS.md)." >&2
  exit 1
fi

hooks_path=$(git config --get core.hooksPath || true)
if [ "$hooks_path" != ".githooks" ] || [ ! -x .githooks/pre-commit ] || [ ! -x .githooks/pre-push ]; then
  echo "Error: versioned git hooks are not active — run 'just setup' before finish-task.sh." >&2
  exit 1
fi

if [ "$stage_all" -eq 1 ]; then
  git add -A
fi

if ! git diff --cached --quiet; then
  if [ -z "$message" ]; then
    if [ -f tmp/commit-message.md ]; then
      message=$(cat tmp/commit-message.md)
    else
      echo "Error: nothing staged message-wise." >&2
      echo "Write tmp/commit-message.md or pass -m \"type: summary\"." >&2
      exit 1
    fi
  fi
  git commit -m "$message"
else
  echo "No staged changes — skipping commit."
fi

git push -u origin "$branch"

if ! command -v gh >/dev/null 2>&1; then
  echo "gh not found — branch pushed, but the task is not complete until the PR is created manually:" >&2
  echo "  gh pr create --fill"
  exit 1
fi

existing=$(gh pr list --head "$branch" --state open --json number --template '{{range .}}{{.number}}{{"\n"}}{{end}}' 2>/dev/null || true)
if [ -n "$existing" ]; then
  echo "PR already open for branch '$branch': #$existing — skipping creation."
  gh pr view "$existing" --json url --template '{{.url}}{{"\n"}}' || true
  exit 0
fi

title=$(printf '%s\n' "$message" | head -1)
if [ -z "$title" ]; then
  title=$(git --no-pager log -1 --pretty=%s)
fi

gh pr create --title "$title" --fill
