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

## 3. Execution — 8 Steps

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

### Step 7 — Generate Onboarding Data (NEW)

From the scan results, generate human-readable onboarding narrative. Add to `system-data.json` as `onboarding` field.

#### 7.1 Project Summary

```
IF project has ≤ 5 domains:
  summary = "{projectName} 是一个 {framework} 项目，包含 {domain_count} 个业务域：{domain_list}。
            核心入口是 {top_entry_point}（{route_count} 个端点）。
            依赖 {external_service_list}。"
ELSE:
  summary = "{projectName} 是一个 {framework} 大型项目，包含 {domain_count} 个业务域。
            主要入口分布在 {top_3_entry_points}。
            外部依赖：{external_service_list}。"
```

#### 7.2 Where to Start

For all entry-layer components, weighted sort:
```
priority = routes.length * 3 + inbound_deps * 2 + methods.length * 1
```
Take Top 5, assign priority 3 (top-2) / 2 (next-2) / 1 (rest). For each, write **why** in one sentence (what it does, why read it first).

#### 7.3 Modules (per domain)

For each domain:
- **purpose**: infer from entity/service names (e.g., "订单生命周期管理：创建、支付、发货、取消、退款")
- **entry_points**: collect all routes from this domain's controllers/routers
- **key_classes**: top 5 components sorted by inbound deps
- **depends_on**: other domains this domain's components call into
- **complexity**: `low` (≤10 nodes) / `medium` (11-30) / `high` (>30)

#### 7.4 Key Flows

For each high-priority entry method:
1. Start from entry method (Controller route handler)
2. BFS along dependency edges through service → data layer
3. Collect all steps, deduplicate, order by call sequence
4. Generate sequence flow description
5. **Only keep flows with depth ≥ 3** (too shallow = no value)

#### 7.5 Code Conventions

Infer from annotation/framework patterns found during scan:
- Example: "所有 Service 接口必须有对应的 ServiceImpl" (if `implements` pattern detected)
- Example: "异常统一使用 @RestControllerAdvice 处理" (if detected)
- Example: "API 路径前缀：/api/v1/" (from route patterns)
- Limit to 5-8 conventions. Only emit what was actually observed.

#### 7.6 Gotchas

Convert `metrics.architectureSmells` + `warnings` into human-readable notes:
- `error` severity → red flag, must-read
- `warning` severity → important to know
- `info` severity → nice to know

Examples:
- "OrderService ↔ InventoryService 存在循环依赖"
- "PaymentGateway 超时配置在 yml 中而非代码常量"
- "LegacyUtil.deprecatedMethod() 无调用者"

### Step 8 — Three-Output Rendering (NEW)

Produce all three output files from the same `system-data.json`:

#### 8.1 architecture.html

1. Read `TEMPLATES/architecture.html` → contains `{{SYSTEM_DATA}}` placeholder
2. Read the generated `system-data.json`
3. Replace `{{SYSTEM_DATA}}` with the actual JSON string
4. Write to `docs/architecture/architecture.html`

#### 8.2 graph.json (AI-optimized)

Transform `system-data.json` into compact format:

```json
{
  "_v": 2,
  "_project": "<projectName>",
  "_lang": "<languagePack>",
  "_brief": "<nodeCount> nodes, <edgeCount> edges, <domainCount> domains. search_graph / trace_path to explore.",

  "n": [
    { "i":"<id>", "l":"<type>", "n":"<name>", "f":"<file>",
      "e":["<route>"], "d":"<domain>" }
  ],

  "e": [
    { "f":"<from_id>", "t":"<to_id>", "y":"<type>" }
  ],

  "d": [
    { "n":"<domain_name>", "c":["<component_ids>"], "x":["<dep_domains>"] }
  ],

  "x": [
    { "n":"<service_name>", "t":"<type>", "k":"<configKey>" }
  ],

  "h": [
    { "f":"<component_id>", "in":<count>, "out":<count>, "risk":"<high|medium>", "reason":"..." }
  ],

  "z": [
    { "n":"<name>", "f":"<file>", "reason":"zero callers / deprecated" }
  ]
}
```

**Key compression rules:**
- Node keys: `i` (id), `l` (label/type), `n` (name), `f` (file), `e` (exports/routes), `c` (calls), `d` (domain), `p` (params), `r` (returns)
- Edge keys: `f` (from), `t` (to), `y` (type)
- Domain keys: `n` (name), `c` (components), `x` (depends_on domains)
- External keys: `n` (name), `t` (type), `k` (configKey)
- Hotspot keys: `f` (component), `in` (inbound), `out` (outbound), `risk`
- Dead code: `z` array with `n` (name), `f` (file), `reason`
- Omit fields with null/empty values entirely
- Only include `h` (hotspots) and `z` (dead_code) if found

**Token target**: < 2,000 tokens for a 50-component project.

#### 8.3 README.onboard.md

1. Read `TEMPLATES/README.onboard.md`
2. Fill placeholders using `system-data.json`:
   - `{{PROJECT_NAME}}` → `meta.projectName`
   - `{{GENERATED_AT}}` → `meta.generatedAt`
   - `{{NODE_COUNT}}` → `meta.nodeCount`
   - `{{DOMAIN_COUNT}}` → `domains.length`
   - `{{ROUTE_COUNT}}` → count all routes across all components
   - `{{PROJECT_SUMMARY}}` → generated summary from Step 7.1
   - `{{TECH_STACK}}` → inferred stack, comma-separated
   - `{{WHERE_TO_START}}` → Top-5 table rows from Step 7.2
   - `{{MODULES}}` → domain descriptions from Step 7.3
   - `{{KEY_FLOWS}}` → sequence diagrams from Step 7.4
   - `{{GOTCHAS}}` → from Step 7.6 + `metrics.architectureSmells`
   - `{{CONVENTIONS}}` → from Step 7.5
   - Empty sections: use `{{#NO_*}}` fallback blocks
3. Write to `docs/architecture/README.onboard.md`

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
| `html` | `docs/architecture/architecture.html` | Default (human interactive view) |
| `json` | `docs/architecture/graph.json` | Always (AI-optimized compact graph) |
| `markdown` | `docs/architecture/README.onboard.md` | Always (human onboarding narrative) |

### Template Files (skill resources — DO NOT put project data here)

| File | Purpose |
|------|---------|
| `TEMPLATES/architecture.html` | HTML viewer template. **Must contain `{{SYSTEM_DATA}}` placeholder. DO NOT fill with project data.** |
| `TEMPLATES/system-data.json` | JSON data schema template |
| `TEMPLATES/README.onboard.md` | Onboarding markdown template. **Must contain `{{PLACEHOLDER}}` markers. DO NOT fill with project data.** |

**Build step — how to generate output files:**

1. Scan project → produce `system-data.json` (Steps 1-7)
2. **architecture.html**: Read template → replace `{{SYSTEM_DATA}}` with actual JSON → save (zero dependencies, pure HTML/CSS)
3. **graph.json**: Transform `system-data.json` using compression rules in Step 8.2 → save
4. **README.onboard.md**: Read template → fill all placeholders from onboarding data in `system-data.json` → save

### Fallback Chain

If a template is missing:
```
HTML template exists → architecture.html (interactive)
  ↓ template missing
JSON + graph.json + README.onboard.md (all require system-data.json)
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
- [ ] `graph.json` is valid JSON with `_v`, `n`, `e` fields
- [ ] `graph.json` token count ≤ 3,000 (for ≤ 80 component projects)
- [ ] `README.onboard.md` written with actual project data (not template placeholders)
- [ ] `onboarding.project_summary` is non-empty
- [ ] `onboarding.where_to_start` has ≥ 1 entry (or warning emitted)
- [ ] `warnings[]` field exists — emit if scan was partial or any count didn't match
- [ ] At least 2 output files written (system-data.json + one other)

### Post-Execution — HTML Integrity Check

- [ ] `systemData` placeholder in `TEMPLATES/architecture.html` replaced with actual JSON
- [ ] `layerView` div populated with arch-node elements (not empty)
- [ ] `connectionsSVG` contains path elements for each dependency edge
- [ ] Tab switch calls `renderFlowView()` on first use and `drawConnections()` on each switch
- [ ] Theme toggle works without page reload (CSS variables only)

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
| JSON parse error in template | Fall back to JSON + text summary |
| HTML render error | Fall back to JSON + text summary |
| Component count mismatch | Add to `warnings[]`, note which type under-counted |
| Network/external service detection | Mark as `inferred`, list the pattern that suggested it |
| Monorepo detection uncertain | Scan all potential roots, emit `warnings[]` |
| graph.json > 3,000 tokens | Truncate `n` array to top-50 by inbound deps, emit warning |
| README.onboard.md template missing | Fall back: write a plain text summary using same onboarding data |
| Onboarding data incomplete | Emit partial sections with `{{#NO_*}}` fallback blocks, add to `warnings[]` |

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
| `TEMPLATES/system-data.json` | JSON data schema template (includes V2 `onboarding` / `impact_map` / `index_meta` fields) |
| `TEMPLATES/README.onboard.md` | Onboarding markdown template (human-readable architecture guide) |
