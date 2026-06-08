# CodeArch

> Generate architecture diagrams from source code — as a Cursor Agent skill.

## What It Does

Scans a software project, extracts components/routes/dependencies/external services, and produces:
- **Interactive HTML diagram** — Mermaid-powered, zoomable, filterable by domain
- **Structured JSON** (`system-data.json`) — machine-readable, CI-friendly
- **Pure Mermaid** (`mermaid-flowchart.md`) — embeddable in README/docs

## Supported Languages

| Pack | Framework | Status |
|------|-----------|--------|
| `java-spring.yaml` | Spring Boot | ✅ Full |
| `nodejs-express.yaml` | Node.js / Express | ✅ Full |
| `python-fastapi.yaml` | Python / FastAPI | ✅ Full |
| `go-stdlib.yaml` | Go / stdlib / chi / Gin | ✅ Full |

More language packs (NestJS, Django, Rust, C#, PHP, Ruby) → see roadmap.

## Quick Start

### 1. Install

```bash
# Clone / copy the docs/architecture/ directory to your skill path
./SCRIPTS/install.sh
# Installs to ~/.cursor/skills/CodeArch/
```

### 2. Use

Say to Cursor agent:

```
"生成架构图"
"architecture diagram"
"map the APIs"
"visualize this project"
```

## File Structure

```
docs/architecture/
├── SKILL.md                    ← Skill entry point (5 steps)
├── REFERENCE.md                ← Schema + language rules
├── LANGUAGES/                  ← Language pack registry
│   ├── java-spring.yaml        # Java / Spring Boot
│   ├── nodejs-express.yaml    # Node.js / Express
│   ├── python-fastapi.yaml     # Python / FastAPI
│   └── go-stdlib.yaml         # Go / stdlib
├── TEMPLATES/                  ← Output templates
│   ├── architecture.html       # Interactive HTML viewer
│   ├── mermaid-flowchart.md   # Pure Mermaid
│   └── system-data.json        # Structured JSON schema
└── SCRIPTS/
    ├── install.sh             # One-command install
    └── update.sh              # Pull latest language packs
```

## Output Format

Each run produces:

| File | Format | Use Case |
|------|--------|---------|
| `architecture.html` | Interactive HTML | Browser viewing, presentations |
| `system-data.json` | JSON | CI pipelines, automation, further analysis |
| `mermaid-flowchart.md` | Mermaid text | Embedded docs, GitHub Markdown |

## Quality Rules

- **Evidence > inference** — only mark deps explicit if code proves it
- **Aggregation > density** — overview ≤ 25 nodes
- **Honest uncertainty** — label `uncertain` instead of guessing
- **Graceful fallback** — always produce at least text summary

## Degradation Chain

```
HTML template available → architecture.html
  ↓ template missing
Mermaid available → mermaid-flowchart.md + system-data.json
  ↓ mermaid fails
JSON only → system-data.json
  ↓ scan fails
Text summary (always succeeds)
```

## Adding a New Language Pack

Create `LANGUAGES/<framework>.yaml` with:

```yaml
id: my-framework
name: My Framework
priority: 40           # Higher = matched first
projectType: mylang

signals:
  - glob: "*.myext"    # One match selects this pack
  - pattern: '"my-framework"' in package.json

directories:
  src/controllers/:    { type: Controller, layer: entry }
  src/services/:      { type: Service, layer: service }
  src/models/:        { type: Entity, layer: data }

dependencyPatterns:
  - pattern: "DIKE_\\w+"
    fromType: "*"
    toType: "resolved type"
    confidence: explicit

routePatterns:
  - pattern: '@route\\(["\']([^"\']+)["\']'
    method: "ROUTE"
    pathExtract: "$1"

mermaidTheme:
  entry:     { fill: "#1a1a2e", stroke: "#e94560", color: "#fff" }
  service:   { fill: "#16213e", stroke: "#0f3460", color: "#e0e0e0" }
```

## Roadmap (Planned)

- [ ] NestJS language pack
- [ ] Django language pack
- [ ] Rust / Axum language pack
- [ ] C# / .NET language pack
- [ ] PHP / Laravel language pack
- [ ] Ruby / Rails language pack
- [ ] Monorepo workspace detection (Nx, Turborepo, pnpm workspaces)
- [ ] Incremental update (diff mode — only changed components)
- [ ] Architecture drift detection (compare two versions of system-data.json)
- [ ] LLM auto-description (generate one-line description per node)
- [ ] Multi-format export (PlantUML, DOT/Graphviz, CSV table)
- [ ] GitHub Action for CI integration
- [ ] VS Code extension for quick diagram viewing

## License

MIT
