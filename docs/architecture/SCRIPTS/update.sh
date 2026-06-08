#!/usr/bin/env bash
# CodeArch update script — pulls latest language packs

set -euo pipefail

SKILL_DIR="${HOME}/.cursor/skills/CodeArch"

if [[ ! -d "${SKILL_DIR}" ]]; then
    echo "CodeArch not installed. Run install.sh first." >&2
    exit 1
fi

echo "Updating CodeArch language packs..."

# Detect repo root (two levels up from SCRIPTS/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

if [[ -d "${REPO_DIR}/.git" ]]; then
    (cd "${REPO_DIR}" && git pull --ff-only 2>/dev/null) || true
fi

# Update language packs
if [[ -d "${REPO_DIR}/docs/architecture/LANGUAGES" ]]; then
    cp -f "${REPO_DIR}/docs/architecture/LANGUAGES"/*.yaml "${SKILL_DIR}/LANGUAGES/" 2>/dev/null || true
fi

echo "✅ Language packs: $(ls "${SKILL_DIR}/LANGUAGES"/*.yaml 2>/dev/null | wc -l)"
