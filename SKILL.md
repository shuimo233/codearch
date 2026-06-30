# ============================================================
# CodeArch — Architecture Diagram Skill
# ============================================================
# Generates interactive architecture diagrams from source code.
# Supports: Java Spring Boot, Node.js/Express, Python/FastAPI, Go
#
# Quick trigger: "生成架构图" | "architecture diagram"
# ============================================================

## 1. When to Use

**Activate when user says:**
- `生成架构图` / `architecture diagram` / `map the APIs`
- `visualize this project` / `show me the structure`
- `单模块架构` / `show me [module] module`

**Skip when:**
- User wants a specific class/file location → use search instead
- User wants to fix a bug → analyze locally
- User wants pure text explanation → respond directly

## 2. Inputs

| Input | Default | Description |
|-------|---------|-------------|
| `projectRoot` | Workspace root | Directory to scan |
| `scope` | `full-project` | `full-project` or `module-only` |
| `moduleName` | (none) | Sub-directory name when `scope=module-only` |
| `outputPath` | `docs/architecture/` | Output directory |
| `outputFormat` | `html` | `html` / `json` / `mermaid` / `table` |
| `incremental` | `false` | `true` = diff mode, only changed components |

## 3. Execution

**Full execution flow** → read `docs/architecture/SKILL.md` (8 steps: Scope → Language → Scan → Dependencies → External Services → Aggregate → Onboarding → Three-Output)

**Quick summary of the 8 steps:**

1. **Scope Detection** — Monorepo? Monolith? Identify all source roots
2. **Language Detection** — Match language pack (java-spring / nodejs-express / python-fastapi / go-stdlib)
3. **Component Scanning** — Extract Controller/Service/Repository/Entity per directory rules
4. **Dependency Inference** — From imports, annotations, naming conventions
5. **External Service Detection** — MySQL/Redis/Kafka/etc from config files and imports
6. **Aggregation** — If >25 nodes, group by domain
7. **Onboarding Generation** — Project summary, where-to-start, key flows, gotchas
8. **Three-Output Rendering** — Produce 4 output files

## 4. Output Files

| File | For | Description |
|------|-----|-------------|
| `architecture.html` | Humans | Interactive diagram (zero-dependency pure HTML/CSS) |
| `README.onboard.md` | Humans | Narrative architecture guide |
| `graph.json` | AI Agents | Compact knowledge graph (~1200 tokens) |
| `system-data.json` | Tools | Unified data source with onboarding/impact data |

## 5. Reference Files

| File | Purpose |
|------|---------|
| `docs/architecture/SKILL.md` | Full 8-step execution flow with detailed rules |
| `docs/architecture/REFERENCE.md` | Schema definitions, language rules, color palette |
| `docs/architecture/LANGUAGES/*.yaml` | Per-framework detection + mapping rules |
| `docs/architecture/LANGUAGES/README.md` | Language pack extension guide |
| `docs/architecture/TEMPLATES/architecture.html` | HTML viewer template (`{{SYSTEM_DATA}}` placeholder) |
| `docs/architecture/TEMPLATES/system-data.json` | JSON data schema template (V2) |
| `docs/architecture/TEMPLATES/README.onboard.md` | Onboarding markdown template |

## 6. Key Rules

- **Evidence > Inference** — Only mark deps `explicit` if code proves it
- **Aggregation > Density** — Overview ≤ 25 nodes
- **Honest Uncertainty** — Label `uncertain` instead of guessing
- **Graceful Fallback** — Always produce at least a text summary
- **Zero Dependencies** — Generated HTML is pure HTML/CSS, no CDN needed

## 7. Anti-Patterns

- ❌ Hardcoding project-specific paths
- ❌ Scanning only top-level directories — always recurse
- ❌ Emitting without validation — `meta.nodeCount` must equal `components.length`
- ❌ Silent omission — if component exists but not in diagram, add to `warnings[]`
- ❌ Embedding project data in template files — use `{{SYSTEM_DATA}}` placeholder
