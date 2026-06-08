# ============================================================
# CodeArch — Architecture Diagram Skill (Cursor Agent)
# ============================================================
# Generates interactive architecture diagrams from source code.
# Supports: Java Spring Boot, Node.js/Express, Python/FastAPI, Go
#
# Quick trigger: "生成架构图" | "architecture diagram"
# ============================================================

## 1. When to Use

Use when user says:
- `生成架构图` / `architecture diagram` / `map the APIs`
- `visualize this project` / `show me the structure`
- `单模块架构` / `show me [module] module`
- `单模块架构图` / `[Module] 模块架构`

Skip when:
- User wants a specific class/file location → use search instead
- User wants to fix a bug → analyze locally, no diagram needed
- User wants pure text explanation → respond directly

## 2. Inputs (defaults if not specified)

| Input | Default |
|-------|---------|
| `projectRoot` | Cursor workspace root |
| `scope` | `full-project` |
| `moduleName` | (none — full project) |
| `outputPath` | `docs/architecture/` |
| `outputFormat` | `html` |
| `backendBaseUrl` | `http://localhost:8080` (for OpenAPI) |

Output formats: `html` (default), `mermaid`, `json`, `table`

## 3. Execution — 5 Steps

### Step 1 — Detect Language Pack

Read `LANGUAGES/*.yaml` files from the skill directory. Match by priority (highest first).

Priority signals per language pack — match any ONE to select that pack:
- **java-spring**: `pom.xml` OR `build.gradle` OR `src/main/java` + Spring annotations
- **nodejs-express**: `package.json` + `node_modules/` + Express patterns
- **python-fastapi**: `requirements.txt` or `pyproject.toml` + FastAPI/Starlette patterns
- **go-stdlib**: `go.mod` + `*.go` files

If no pack matches → use generic regex scan + `confidence: uncertain`.

### Step 2 — Scan Components

Use the matched language pack to extract:
- Component name, type, layer, file path, package/namespace
- Public methods / handlers
- Routes (HTTP paths + methods)
- Injected dependencies (field names)
- Domain / module归属

Exclude by default: `node_modules/`, `.git/`, `dist/`, `build/`, `target/`, `__pycache__/`, `vendor/`, `coverage/`, test files.

### Step 3 — Infer Dependencies

Use the matched language pack's dependency patterns:
- `explicit`: direct declaration in code (import, require, @Autowired, etc.)
- `inferred`: structural pattern match (e.g., controller naming convention → service)
- `uncertain`: multiple possible interpretations

Only emit dependencies with supporting evidence. Do NOT fabricate relationships.

### Step 4 — Detect External Services

Scan for: config files, environment variables, SDK imports, connection strings.

Detectable: SQL databases, Redis, MongoDB, Neo4j, Kafka, Elasticsearch, vector stores, S3, third-party APIs (LLM providers, payment, email, auth), message queues.

Emit `confidence` (explicit/inferred) and `configKey` (the config key or env var that identified it).

### Step 5 — Aggregate & Render

**Before aggregating**, verify completeness:

1. Count `@RestController` classes in source → compare with `components[].type==Controller` count
2. Count `@Service` classes in source → compare with `components[].type==Service` count
3. Count `@Component` classes in source → compare with `components[].type==Component` count
4. Count `.vue` files in `frontend/src/views/` → compare with `components[].type==View` count
5. If any count is lower than source → **scan was incomplete**: add to `warnings[]` and fix the scan

**Then aggregate**:

- If `nodeCount ≤ 25` → no aggregation needed
- If `nodeCount > 25` → group by domain OR by layer, produce overview + domain diagrams
- **Never** silently omit components without listing them in `warnings`

Render using `TEMPLATES/` from skill directory. Fallback chain:

```
html → mermaid-flowchart.md → system-data.json → text summary
```

Always produce at least one output. Never return empty-handed.

## 4. systemData Schema

The core data structure. Output as JSON.

```json
{
  "meta": {
    "projectType": "java-spring | nodejs | python | go | multi-stack",
    "projectName": "string",
    "generatedAt": "ISO 8601",
    "sourceRoots": ["path"],
    "scope": "full-project | module-only",
    "moduleName": "string | null",
    "languagePack": "string",
    "outputFormat": "html | mermaid | json | table",
    "nodeCount": "number"
  },
  "components": [{
    "id": "unique-node-id",
    "name": "display-name",
    "type": "Controller|Service|Repository|Entity|Config|Client|...",
    "layer": "entry|service|data|infra|external|job|event",
    "package": "namespace",
    "file": "relative-path",
    "domain": "domain-name",
    "routes": [{ "method": "GET", "path": "/api/...", "desc": "..." }],
    "methods": ["methodName"],
    "injects": ["dependencyName"],
    "confidence": "explicit | inferred | uncertain",
    "warnings": []
  }],
  "routes": [{
    "method": "GET|POST|PUT|DELETE|PATCH",
    "path": "/api/...",
    "componentId": "...",
    "desc": "...",
    "source": "static-scan | openapi | inferred"
  }],
  "dependencies": [{
    "from": "component-id",
    "to": "component-id | external-service-name",
    "type": "calls | injects | uses | queries | stores",
    "confidence": "explicit | inferred | uncertain",
    "evidence": "brief evidence"
  }],
  "externalServices": [{
    "name": "MySQL",
    "type": "database | cache | queue | graph | vector | object-storage | api",
    "configKey": "spring.datasource.url",
    "confidence": "explicit | inferred"
  }],
  "domains": [{
    "name": "order",
    "componentIds": ["E_ORDER", "S_ORDER", "R_ORDER"]
  }],
  "entryPoints": [{
    "name": "Product HTTP API",
    "type": "http | cli | job | event | scheduled",
    "componentId": "E_PRODUCT"
  }],
  "warnings": ["string — honest limitations"]
}
```

## 5. Output Files

| Format | File | Description |
|--------|------|-------------|
| `html` | `docs/architecture/architecture.html` | Interactive Mermaid diagram |
| `mermaid` | `docs/architecture/mermaid-flowchart.md` | Pure Mermaid text |
| `json` | `docs/architecture/system-data.json` | Structured JSON |
| `table` | `docs/architecture/component-table.md` | Markdown table |

Always output `system-data.json` alongside the primary format.

## 6. Validation Checklist

### Pre-Execution — Scope Verification (MUST verify before scanning)

Before scanning, confirm these paths exist:

- [ ] `backend/src/main/java/com/project/web/onlineshopping/controller/` (exists → check subdirs)
- [ ] `backend/src/main/java/com/project/web/onlineshopping/controller/ai/` — List files
- [ ] `backend/src/main/java/com/project/web/onlineshopping/controller/buyer/` — List files
- [ ] `backend/src/main/java/com/project/web/onlineshopping/controller/logistics/` — List files
- [ ] `backend/src/main/java/com/project/web/onlineshopping/controller/order/` — List files
- [ ] `backend/src/main/java/com/project/web/onlineshopping/controller/product/` — List files
- [ ] `backend/src/main/java/com/project/web/onlineshopping/controller/promotion/` — List files
- [ ] `backend/src/main/java/com/project/web/onlineshopping/controller/seller/` — List files
- [ ] `backend/src/main/java/com/project/web/onlineshopping/controller/system/` — List files
- [ ] `backend/src/main/java/com/project/web/onlineshopping/service/` — Check subdirs recursively
- [ ] `backend/src/main/java/com/project/web/onlineshopping/ai/` — List files (agents, providers, metrics, nlp, resilience)
- [ ] `backend/src/main/java/com/project/web/onlineshopping/kg/` — List files
- [ ] `backend/src/main/java/com/project/web/onlineshopping/rag/` — List files
- [ ] `backend/src/main/java/com/project/web/onlineshopping/config/` — List files
- [ ] `backend/src/main/java/com/project/web/onlineshopping/listener/` — List files
- [ ] `backend/src/main/java/com/project/web/onlineshopping/domain/event/` — List files
- [ ] `backend/src/main/java/com/project/web/onlineshopping/task/` — List files
- [ ] `backend/src/main/java/com/project/web/onlineshopping/vector/` — List files
- [ ] `backend/src/main/java/com/project/web/onlineshopping/payment/` — List files
- [ ] `frontend/vue-onlineshopping/src/views/` — List all .vue files
- [ ] `frontend/vue-onlineshopping/src/components/` — List all .vue files
- [ ] `frontend/vue-onlineshopping/src/router/` — Check router/index.js

**Rule: List files in EVERY subdirectory. Do NOT assume a directory is empty.**

### Post-Execution — Completeness Check (MUST verify before responding)

- [ ] `nodeCount` in meta equals actual components array length
- [ ] `@RestController` class count in code ≤ components array length (scan was complete)
- [ ] `@Service` class count in code ≤ components array length (scan was complete)
- [ ] `@Component` class count in code ≤ components array length (scan was complete)
- [ ] `@Repository` class count in code ≤ components array length (scan was complete)
- [ ] `@Configuration` class count in code ≤ components array length (scan was complete)
- [ ] All `.vue` files in `views/` are represented in components array (layer: frontend)
- [ ] `router/index.js` routes are reflected in the components or entryPoints
- [ ] Every component in `domains[].componentIds` exists in `components[]` (no dangling refs)
- [ ] Every `routes[].componentId` exists in `components[]` (no dangling refs)
- [ ] `system-data.json` is valid JSON (parseable)
- [ ] `{{SYSTEM_DATA}}` replaced in HTML template
- [ ] `{{MERMAID_CODE}}` replaced in HTML template (if using HTML)
- [ ] `warnings` field exists — if scan was partial or directories were missing, warn explicitly
- [ ] At least one output file written

### Post-Execution — Mermaid HTML Integrity Check

- [ ] Every `subgraph NAME[...]` has a matching `end` on its own line
- [ ] Two diagrams use separate `<div class="mermaid" id="...">` containers
- [ ] Tab switch function calls `mermaid.run()` on the hidden container when switching
- [ ] No `</div>` accidentally closes the mermaid container before the second diagram starts

## 7. Quality Rules

- **Evidence > inference**: explicit deps only if code proves it
- **Aggregation > density**: overview diagram ≤ 25 nodes
- **Honest uncertainty**: label `uncertain` instead of guessing
- **Graceful fallback**: never return empty, always produce something
- **Separate concerns**: SKILL.md = flow; REFERENCE.md = details; LANGUAGES/ = per-language rules

### Anti-Patterns (MUST avoid)

- ❌ **Incomplete directory scan**: Only scanning top-level `controller/` files while `controller/ai/`, `controller/buyer/` etc. exist. **Fix: Always `Glob` or `ls` every subdirectory recursively.**
- ❌ **Missing sub-modules**: Ignoring `ai/`, `kg/`, `rag/`, `config/`, `listener/`, `task/`, `vector/` directories. **Fix: Check all non-standard directories.**
- ❌ **Missing frontend**: Scanning backend only and omitting Vue `views/`, `components/`, `router/`. **Fix: Always scan `frontend/` when it exists.**
- ❌ **Emitting without verification**: Outputting `system-data.json` without counting components. **Fix: `nodeCount` must equal `components.length`.**
- ❌ **Silent omission**: A component exists in code but is absent from the diagram without any `warning`. **Fix: If scan was partial, emit a warning.**
- ❌ **Dangling references**: `routes[].componentId` or `domains[].componentIds[]` references a component not in `components[]`. **Fix: Cross-check all IDs.**
- ❌ **Aggregating without consent**: Grouping components into a summary node without user request. **Fix: Only aggregate when `nodeCount > 25`.**

## 8. Reference Files

- `LANGUAGES/java-spring.yaml` — Java Spring Boot rules
- `LANGUAGES/nodejs-express.yaml` — Node.js Express rules
- `LANGUAGES/python-fastapi.yaml` — Python FastAPI rules
- `LANGUAGES/go-stdlib.yaml` — Go stdlib rules
- `REFERENCE.md` — schema definitions, color palette, examples
- `TEMPLATES/architecture.html` — interactive HTML viewer
