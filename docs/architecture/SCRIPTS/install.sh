#!/usr/bin/env bash
# CodeArch install script — installs the skill to ~/.cursor/skills/CodeArch

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="${HOME}/.cursor/skills/CodeArch"

echo "Installing CodeArch to ${SKILL_DIR}..."

mkdir -p "${SKILL_DIR}"

# Copy core files
cp "${SCRIPT_DIR}/../SKILL.md"      "${SKILL_DIR}/"
cp "${SCRIPT_DIR}/../REFERENCE.md"  "${SKILL_DIR}/"

# Copy language packs
if [[ -d "${SCRIPT_DIR}/../LANGUAGES" ]]; then
    cp -r "${SCRIPT_DIR}/../LANGUAGES" "${SKILL_DIR}/"
fi

# Copy templates
if [[ -d "${SCRIPT_DIR}/../TEMPLATES" ]]; then
    cp -r "${SCRIPT_DIR}/../TEMPLATES" "${SKILL_DIR}/"
fi

# Copy scripts
cp "${SCRIPT_DIR}/install.sh" "${SKILL_DIR}/"
if [[ -f "${SCRIPT_DIR}/update.sh" ]]; then
    cp "${SCRIPT_DIR}/update.sh" "${SKILL_DIR}/"
fi

# Validate
errors=0
for f in SKILL.md REFERENCE.md; do
    if [[ ! -f "${SKILL_DIR}/${f}" ]]; then
        echo "ERROR: Missing ${f}" >&2
        errors=$((errors + 1))
    fi
done

if [[ -d "${SKILL_DIR}/LANGUAGES" ]]; then
    count=$(ls "${SKILL_DIR}/LANGUAGES"/*.yaml 2>/dev/null | wc -l)
    echo "  Language packs : ${count}"
fi

if [[ -d "${SKILL_DIR}/TEMPLATES" ]]; then
    echo "  Templates      : $(ls "${SKILL_DIR}/TEMPLATES" 2>/dev/null | tr '\n' ' ')"
fi

if [[ ${errors} -eq 0 ]]; then
    echo "✅ CodeArch installed"
else
    echo "❌ ${errors} error(s)" >&2
    exit 1
fi
