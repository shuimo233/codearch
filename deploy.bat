@echo off
cd /d D:\Projects\codearch
git add -A
git commit -m "Optimize SKILL.md: remove hardcoded paths, add incremental mode, error recovery, monorepo support"
git push origin main
