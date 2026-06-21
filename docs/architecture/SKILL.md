# ============================================================
# CodeArch — Architecture Diagram Skill (Cursor Agent)
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
- `单模块架构图` / `[Module] 模块架构`

**Skip when:**
- User wants a specific class/file location → use search instead
- User wants to fix a bug → analyze locally, no diagram needed
- User wants pure text explanation → respond directly

---

## 2. Inputs

| Input | Default | Description |
|-------|---------|-------------|
| `projectRoot` | Cursor workspace root | Directory to scan |
| `scope` | `full-project` | `full-project` or `module-only` |
| `moduleName` | (none) | Sub-directory name when `scope=module-only` |
| `sourceRoots` | auto-detect | Override auto-detected source root(s) |
| `outputPath` | `docs/architecture/` | Output directory |
| `outputFormat` | `html` | `html` / `json` / `mermaid` / `table` |
| `incremental` | `false` | `true` = diff mode, only changed components |
| `backendBaseUrl` | `http://localhost:8080` | For OpenAPI spec fallback |

### Output Format Guide

| Format | Best for |
|--------|----------|
| `html` | Interactive browsing, presentations |
| `json` | CI pipelines, automation, tooling |
| `mermaid` | Embedded in README or docs |
| `table` | Quick text overview |

---

## 3. Execution — 6 Steps

### Step 0 — Scope Detection

**Before scanning**, detect project structure:

```
1. Detect project type: monorepo or monolith?
   - Look for: pnpm-workspace.yaml, lerna.json, nx.json, Turborepo, maven/gradle multi-module
   - If monorepo: identify workspace packages (backend/, services/, apps/, packages/, etc.)
   - Collect ALL source roots

2. For each source root, detect language pack (see Step 1)
   - One project may have multiple language packs (e.g., backend=java-spring, frontend=vue)

3. Collect source file statistics to set expectations:
   - Count *.java, *.js, *.ts, *.py, *.go files
   - Estimate component count before scanning
   - If estimated > 60 components → prepare aggregation strategy
```

**Monorepo pattern:**
```
workspace/
├── apps/
│   ├── backend/         → java-spring source root
│   └── web/            → vue/react source root
├── services/
│   └── auth/           → nodejs-express source root
├── packages/
│   └── shared/         → shared lib, skip unless explicitly requested
└── docs/architecture/  → outputPath
```

### Step 1 — Detect Language Pack

Read all `LANGUAGES/*.yaml` files. Match by priority (highest first).

Match signals — **any ONE** selects that pack:

| Pack | Signals |
|------|---------|
| `java-spring` | `pom.xml` OR `build.gradle` OR `build.gradle.kts` OR `src/main/java/**/*Controller.java` |
| `nodejs-express` | `package.json` + (`routes/` OR `controllers/` OR `app.js`) |
| `python-fastapi` | `requirements.txt` OR `pyproject.toml` + (`fastapi` OR `starlette` OR `flask` OR `django`) |
| `go-stdlib` | `go.mod` + `*.go` files |

**Multi-pack project**: scan each source root with its own pack, merge into single `systemData` with `domains[]` keyed by source root.

**No match**: use generic regex scan + all `confidence: uncertain`.

### Step 2 — Scan Components

Use matched language pack's directory → layer/type mapping.

**Critical rule — ALWAYS recurse:**
> Do NOT scan only top-level directories. Use `Glob` or `ls` to check every subdirectory.
> Missing subdirectories are the #1 cause of incomplete diagrams.

**Standard exclusions (always skip):**
```
node_modules/  .git/  dist/  build/  target/
__pycache__/  .venv/  venv/  vendor/
coverage/  .nyc_output/  .pytest_cache/
.dll/  .exe/  .jar/  .war/
```

**Component fields to extract:**
- `id`: unique, safe (alphanumeric + underscore)
- `name`: display name (e.g., `ProductsService`)
- `type`: Controller | Service | Repository | Entity | Config | Client | Router | Job | Consumer | Module | Component | View
- `layer`: entry | service | data | infra | external | job | event | frontend
- `file`: relative path from source root
- `package`: namespace / module path
- `domain`: inferred from path (e.g., `order`, `product`, `ai`)
- `routes[]`: HTTP method + path (entry layer only)
- `methods[]`: notable public method names
- `injects[]`: injected dependency names
- `confidence`: explicit | inferred | uncertain

### Step 2.5 — Scan Frontend (if detected)

If language pack has `frontendScan.enabled: true` AND `frontend/**/package.json` exists:
1. Scan `frontend/src/views/` → one `View` component per `.vue` file
2. Scan `frontend/src/components/` recursively → one `Component` per notable `.vue` file
3. Scan `frontend/src/router/` → extract `path` + `component` pairs
4. Infer domain from path: `views/OrderView.vue` → domain=`order`
5. Add frontend layer components to `components[]`

### Step 3 — Infer Dependencies

Use language pack's `dependencyPatterns`:

| Confidence | When to use |
|------------|-------------|
| `explicit` | Direct declaration in code (import, @Autowired, require, from x import y) |
| `inferred` | Structural pattern match (naming convention, directory co-location) |
| `uncertain` | Multiple possible interpretations — use sparingly |

**Rule**: Only emit dependencies with supporting evidence. Never fabricate relationships.
If you cannot find evidence for a likely relationship, either skip it or mark `uncertain`.

### Step 4 — Detect External Services

Scan for: config files, environment variables, SDK imports, connection strings.

**Standard detection patterns (use configKey + regex):**

|| Service | Config Keys | Import Patterns |
|---------|-------------|-----------------|
| MySQL | `spring.datasource.url`, `mysql://` | `mysql-connector-java` |
| PostgreSQL | `spring.datasource.url`, `postgresql://` | `postgresql` driver |
| MongoDB | `spring.data.mongodb.uri` | `mongodb` driver |
| Redis | `spring.data.redis.host` | `spring-boot-starter-data-redis` |
| Neo4j | `spring.neo4j.uri` | `neo4j` driver |
| Elasticsearch | `elasticsearch.url`, `opensearch` | `elasticsearch` client |
| Qdrant | `qdrant.*`, `QDRANT_HOST` | `qdrant-client` |
| Weaviate | `WEAVIATE_*` | `weaviate-client` |
| Kafka | `spring.kafka.bootstrap-servers` | `spring-kafka` |
| RabbitMQ | `spring.rabbitmq.*` | `amqplib` |
| S3/MinIO | `aws.s3.*`, `minio.*` | `@aws-sdk/client-s3` |
| DeepSeek | `DEEPSEEK_API_KEY` | `openai` package |
| 通义千问 | `DASHSCOPE_API_KEY` | `dashscope` package |
| 支付宝 | `ALIPAY_*` | `alipay` SDK |
| Stripe | `STRIPE_API_KEY` | `stripe` package |
| SMTP | `spring.mail.*` | `spring-boot-starter-mail` |
| JWT/Auth | `jwt.*`, `security.*` | `jjwt`, `spring-security` |

**Important rules:**
1. External service `name` should use standard names: `MySQL`, `Redis`, `MongoDB`, `Neo4j`, `Qdrant`, `S3`, `DeepSeek`, `通义千问`
2. **Never use non-standard names** like "本地文件存储" — use `S3`, `MinIO`, or `LocalStorage`
3. Always emit `configKey` and `confidence`
4. For detected but unconfirmed services, use `confidence: inferred`

### Step 5 — Aggregate (if needed)

**Threshold-based:**
- `nodeCount ≤ 25` → no aggregation
- `nodeCount > 25` → group by domain, produce overview + per-domain diagrams
- `nodeCount > 80` → two-level: overview + domain + layer diagrams

**Aggregation signals:**
1. Package prefix (e.g., `com.project.service.*` → `S_SERVICE_GROUP`)
2. Domain in path (e.g., `...order.*` → `order` domain)
3. Naming convention (e.g., `XController.java` → `order` domain)
4. Framework convention (all `*Repository.java` → data layer)

**Target node counts:**
| Diagram | Target | Max |
|---------|--------|-----|
| Overview | 15–25 | 30 |
| Per-domain | 8–15 | 20 |
| Per-layer | 5–10 | 15 |

**Rule**: Never silently omit components. If aggregating, document the summary node in `domains[]` and add to `warnings[]`.

### Step 6 — Validate & Render

**Pre-render validation** (must pass before writing output):
1. `nodeCount` in meta equals `components.length`
2. `@RestController`/`@Service`/`@Component` counts in code ≤ component array length
3. Every `routes[].componentId` exists in `components[]`
4. Every `domains[].componentIds[]` exists in `components[]`
5. `system-data.json` is valid JSON
6. `warnings[]` exists — add any incompleteness

**Render**: produce output files per format. See Section 5.

---

## 4. Incremental Update Mode (`incremental: true`)

When user wants to update an existing diagram without full rescan:

```
1. Load existing system-data.json
2. Get file modification times from last scan
3. Only rescan files modified since last run
4. Diff: added / removed / changed components
5. Update system-data.json, rebuild HTML
6. Report: "X added, Y removed, Z updated"
```

**When to auto-trigger**: User says "更新架构图" / "refresh diagram" / "增量更新".

---

## 5. Output Files

### Primary Outputs (always produce)

| Format | File | When |
|--------|------|------|
| `json` | `docs/architecture/system-data.json` | Always (machine-readable source of truth) |
| `html` | `docs/architecture/architecture.html` | Default |

### Template Files (skill resources — DO NOT put project data here)

| File | Purpose |
|------|---------|
| `TEMPLATES/architecture.html` | HTML viewer template. **Must contain `{{SYSTEM_DATA}}` placeholder. DO NOT fill with project data.** |
| `TEMPLATES/system-data.json` | JSON data schema template |

**Build step — how to generate output HTML:**
1. Read `TEMPLATES/architecture.html` → contains `{{SYSTEM_DATA}}` placeholder
2. Read `system-data.json` → contains actual component data
3. Replace `{{SYSTEM_DATA}}` in template with the actual JSON string
4. Save result as `docs/architecture/architecture.html`
5. `TEMPLATES/architecture.html` remains unchanged for the next project

### Fallback Chain

If a template is missing:
```
HTML template exists → architecture.html (interactive)
  ↓ template missing
JSON only → system-data.json
  ↓ scan fails entirely
Text summary (always succeeds)
```

---

## 6. Validation Checklist

### Pre-Execution — Scope Verification

**MUST verify before scanning any directory:**

- [ ] Identify project type: monorepo? → list all workspace packages
- [ ] Identify source root(s): one or multiple? → scan each
- [ ] For each source root: which language pack matches?
- [ ] List ALL subdirectories (not just top-level) before assuming structure
- [ ] Check for frontend directory (Vue/React) — scan if present
- [ ] Estimate total component count → decide on aggregation strategy

**Rule**: List files in EVERY subdirectory. Do NOT assume a directory is empty or structured a certain way.

### Post-Execution — Completeness Check

**MUST verify before responding:**

- [ ] `meta.nodeCount` equals `components.length`
- [ ] `@RestController` class count in code ≤ `components.length` (all found)
- [ ] `@Service` class count in code ≤ `components.length` (all found)
- [ ] `@Component` class count in code ≤ `components.length` (all found)
- [ ] `@Repository` class count in code ≤ `components.length` (all found)
- [ ] `@Configuration` class count in code ≤ `components.length` (all found)
- [ ] All `.vue`/`.tsx` files in `views/` represented in `components` (layer: frontend)
- [ ] `router/index.js` routes reflected in `routes[]` or `entryPoints[]`
- [ ] Every `routes[].componentId` exists in `components[]` (no dangling refs)
- [ ] Every `domains[].componentIds[]` exists in `components[]` (no dangling refs)
- [ ] `system-data.json` is valid, parseable JSON
- [ ] `warnings[]` field exists — emit if scan was partial or any count didn't match
- [ ] At least one output file written

### Post-Execution — HTML Integrity Check

- [ ] `systemData` placeholder in `TEMPLATES/architecture.html` replaced with actual JSON
- [ ] `mermaidContainer` div has dynamic code injection (not hardcoded Mermaid text)
- [ ] Tab switch calls `mermaid.run()` on the hidden container when switching
- [ ] `buildMermaidCode()` uses correct JS syntax (no regex `[^...` errors, no variable shadowing)

---

## 7. Quality Rules

### Evidence > Inference
Only mark deps `explicit` if code proves it. Use `inferred` for naming conventions. Use `uncertain` for ambiguous cases.

### Aggregation > Density
Overview diagram ≤ 25 nodes. If more, aggregate by domain and produce per-domain views.

### Honest Uncertainty
Label `uncertain` instead of guessing. If you cannot verify a relationship, skip it.

### Graceful Fallback
Never return empty. Always produce at least a text summary.

### Separate Concerns
| File | Content |
|------|---------|
| `SKILL.md` | Flow, triggers, validation |
| `REFERENCE.md` | Language rules, schema, color palette |
| `LANGUAGES/*.yaml` | Per-framework detection + mapping rules |
| `TEMPLATES/` | Output templates (data-agnostic) |

---

## 8. Anti-Patterns (MUST Avoid)

- ❌ **Hardcoded paths**: Never put project-specific paths in SKILL.md. All paths must be dynamically detected or parameterized.
- ❌ **Incomplete directory scan**: Scanning only top-level `controller/` while subdirs exist. **Fix: Always Glob/ls every subdirectory recursively.**
- ❌ **Missing sub-modules**: Ignoring `ai/`, `kg/`, `rag/`, `config/`, `listener/`, `task/`, `vector/`, `domain/event/` directories. **Fix: Check all non-standard directories.**
- ❌ **Missing frontend**: Scanning backend only. **Fix: Always scan `frontend/` when it exists — check `src/views/` AND `src/components/` recursively.**
- ❌ **Emitting without verification**: Outputting JSON without counting components. **Fix: `meta.nodeCount` must equal `components.length`.**
- ❌ **Silent omission**: Component exists but absent from diagram without `warning`. **Fix: Emit warning if scan was partial.**
- ❌ **Dangling references**: `routes[].componentId` references non-existent component. **Fix: Cross-check all IDs.**
- ❌ **Aggregating without consent**: Grouping without user request. **Fix: Only aggregate when `nodeCount > 25`.**
- ❌ **Embedding project data in template**: `TEMPLATES/architecture.html` must use `{{SYSTEM_DATA}}` placeholder, never project-specific `systemData`. **Fix: Keep template generic, build output by replacement.**

---

## 9. Error Recovery

| Failure | Recovery |
|---------|----------|
| Language pack not found | Fall back to generic regex scan with `confidence: uncertain` |
| Directory does not exist | Skip gracefully, add to `warnings[]` |
| Template file missing | Fall back to next format in chain (Section 5) |
| JSON parse error in template | Emit mermaid-only output |
| Mermaid render error | Fall back to JSON + text summary |
| Component count mismatch | Add to `warnings[]`, note which type under-counted |
| Network/external service detection | Mark as `inferred`, list the pattern that suggested it |
| Monorepo detection uncertain | Scan all potential roots, emit `warnings[]` |

---

## 9.1 Architecture Smells Detection (Advanced)

**Detect and warn about these common architecture issues:**

| Smell Type | Detection | Severity |
|------------|-----------|----------|
| **Controller directly accessing Repository** | `@RestController` uses `@Autowired Repository` | warning |
| **Circular dependency** | A → B → C → A in dependencies | error |
| **God Component** | Single component with > 20 methods or > 500 lines | warning |
| **Missing abstraction** | Service contains no interfaces | info |
| **Data access in entry layer** | Controller/Handler directly queries database | warning |
| **Hardcoded configuration** | No `@ConfigurationProperties` or external config | info |
| **Synchronous external calls** | No async/future pattern for external APIs | info |

**Emit in `metrics.architectureSmells`:**

```json
{
  "metrics": {
    "architectureSmells": [
      {
        "type": "controller-direct-repo-access",
        "severity": "warning",
        "description": "ProductAdminController directly injects ProductsRepository",
        "components": ["C_PRODUCT_ADMIN", "R_PRODUCT"]
      }
    ]
  }
}
```

---

## 10. Reference Files

| File | Purpose |
|------|---------|
| `LANGUAGES/java-spring.yaml` | Java Spring Boot detection + rules (includes `frontendScan` for Vue) |
| `LANGUAGES/nodejs-express.yaml` | Node.js Express detection + rules |
| `LANGUAGES/python-fastapi.yaml` | Python FastAPI detection + rules |
| `LANGUAGES/go-stdlib.yaml` | Go stdlib/chi/Gin detection + rules |
| `REFERENCE.md` | Schema definitions, color palette, aggregation rules, external service table |
| `TEMPLATES/architecture.html` | HTML viewer template (`{{SYSTEM_DATA}}` placeholder — generic, no project data) |
| `TEMPLATES/system-data.json` | JSON data schema template |
