#!/usr/bin/env bash
# ==============================================================================
# Question 10: Git Forensics - Recover Leaked Staging Token
# ==============================================================================

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR/repo"

# 1. Rebuild git repository from fast-import dump
rm -rf "$REPO_DIR"
mkdir -p "$REPO_DIR"
cd "$REPO_DIR"

git init -q
git fast-import --quiet < "$DIR/history.fastimport"
git checkout -f main

# 2. Extract commit subject and token
COMMIT_SUBJECT=$(git log -S 'STAGING_TOKEN=' --oneline -- config/app.env | head -n 1 | cut -d' ' -f2-)
TOKEN=$(git log -p -- config/app.env | grep -E '^\+STAGING_TOKEN=stg_' | head -n 1 | cut -d'=' -f2)

echo "--- Recovered Forensics Data ---"
echo "Commit Subject: $COMMIT_SUBJECT"
echo "Recovered Token: $TOKEN"

echo -e "\n--- JSON Submission ---"
cat "$DIR/solution.json"
