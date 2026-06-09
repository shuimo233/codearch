# ============================================================
# CodeArch — Reference Manual
# ============================================================
# Language-specific rules, schema definitions, color palette,
# and output format details. Consumed by SKILL.md.
# ============================================================

## systemData Schema — Quick Reference

Full schema in SKILL.md Section 3.

| Field | Values |
|-------|--------|
| `layer` | `entry` \| `service` \| `data` \| `infra` \| `external` \| `job` \| `event` \| `frontend` |
| `type` | `Controller` \| `Service` \| `Repository` \| `Entity` \| `Router` \| `Handler` \| `Config` \| `Client` \| `Job` \| `Consumer` \| `Module` \| `Component` \| `View` |
| `confidence` | `explicit` \| `inferred` \| `uncertain` |
| `dep type` | `calls` \| `injects` \| `uses` \| `queries` \| `stores` \| `subscribes` |

**Rule**: `warnings[]` must be honest. Emit for: partial scans, inferred components, unknown project types.

---

## java-spring

**Signals**: `pom.xml` OR `build.gradle` OR `build.gradle.kts` OR `src/main/java/**/*Controller.java`

### Directory → Layer/Type

| Directory | Type | Layer |
|-----------|------|-------|
| `controller/` | Controller | entry |
| `controller/*/` | Controller | entry |
| `service/` | Service | service |
| `service/*/` | Service | service |
| `service/impl/` | Service | service |
| `repository/` | Repository | data |
| `repository/*/` | Repository | data |
| `entity/` | Entity | data |
| `entity/*/` | Entity | data |
| `model/` | Entity | data |
| `dto/` | Entity | data |
| `config/` | Config | infra |
| `config/*/` | Config | infra |
| `ai/` | Component | service |
| `ai/*/` | (per subdir) | service |
| `kg/` | Service | service |
| `rag/` | Service | service |
| `vector/` | Service | service |
| `payment/` | Component | infra |
| `payment/gateway/` | Client | external |
| `listener/` | Consumer | event |
| `domain/event/` | Consumer | event |
| `task/` | Job | job |

### Dependency Inference

| Pattern | From → To | Confidence |
|---------|-----------|------------|
| `@Autowired` field type | Controller/Service → Service/Repository | explicit |
| Constructor `new X()` | Any → X | explicit |
| `@RequiredArgsConstructor` / `@AllArgsConstructor` | Any → injected type | explicit |
| `implements Interface` | Component → Interface type | explicit |
| `extends BaseClass` | Entity → Base Entity | explicit |
| `MongoRepository<,>` / `JpaRepository<,>` | Service → Repository | explicit |
| Package naming: `XController` → `XService` | Controller → Service | inferred |

### Routes

Extract from: `@GetMapping`, `@PostMapping`, `@PutMapping`, `@DeleteMapping`, `@PatchMapping`, `@RequestMapping`.
Path: `"..."` from `value=` or `path=`.

### Colors

```mermaid
classDef entry   fill:#1a1a2e,stroke:#e94560,color:#fff
classDef service fill:#16213e,stroke:#0f3460,color:#e0e0e0
classDef data    fill:#0f3460,stroke:#53d8fb,color:#fff
classDef infra   fill:#1b1b2f,stroke:#a29bfe,color:#e0e0e0
classDef external fill:#2d2d44,stroke:#ffd93d,color:#fff
classDef job     fill:#1b1b2f,stroke:#6bcb77,color:#fff
classDef event   fill:#1b1b2f,stroke:#ff6b6b,color:#fff
```

---

## nodejs-express

**Signals**: `package.json` + (`routes/` OR `controllers/` OR `app.js`)

### Directory → Layer/Type

| Directory | Type | Layer |
|-----------|------|-------|
| `routes/` | Router | entry |
| `controllers/` | Controller | service |
| `services/` | Service | service |
| `models/` | Entity | data |
| `middlewares/` | Config | infra |
| `config/` | Config | infra |
| `utils/` | Config | infra |
| `clients/` | Client | external |
| `jobs/` | Job | job |
| `workers/` | Job | job |

### Dependency Inference

| Pattern | Confidence |
|---------|------------|
| `require('...')` / `import from` | explicit |
| `router.get/post/put/delete(path, handler)` | explicit (route) |
| `app.use(middleware)` | explicit |
| `XController` → `XService` (naming) | inferred |
| stdlib imports (`fs`, `path`, `crypto`) | skip |

### Routes

Extract from `router.get(path, ...)`, `router.post(path, ...)`, `app.get(path, ...)`.
Path: first string argument.

### Colors

```mermaid
classDef entry   fill:#2d5016,stroke:#6bcb77,color:#fff
classDef service fill:#1a3a0f,stroke:#a8e063,color:#fff
classDef data    fill:#0f2d1f,stroke:#53d8fb,color:#fff
classDef infra   fill:#1a1a2e,stroke:#a29bfe,color:#e0e0e0
classDef external fill:#2d2d44,stroke:#ffd93d,color:#fff
classDef job     fill:#1b1a2e,stroke:#ff9f43,color:#fff
classDef event   fill:#1a1a2e,stroke:#ff6b6b,color:#fff
```

---

## python-fastapi

**Signals**: `requirements.txt` OR `pyproject.toml` + (`fastapi` OR `starlette` OR `flask` OR `django`)

### Directory → Layer/Type

| Directory | Type | Layer |
|-----------|------|-------|
| `routers/` or `routes/` | Router | entry |
| `controllers/` | Controller | service |
| `services/` | Service | service |
| `models/` or `schemas/` | Entity | data |
| `crud/` | Repository | data |
| `core/` or `config/` | Config | infra |
| `utils/` | Config | infra |
| `clients/` or `external/` | Client | external |
| `tasks/` or `jobs/` | Job | job |
| `consumers/` | Consumer | event |

### Dependency Inference

| Pattern | Confidence |
|---------|------------|
| `from x import y` / `import x` | explicit |
| `@router.get/post/put/delete` | explicit |
| `@app.get` (FastAPI app) | explicit |
| `@app.route` (Flask) | explicit |
| `APIRouter()` + include_router | explicit |
| `router` → `service` (naming) | inferred |

### Routes

Extract from `@router.get("/path")`, `@app.post("/path")`, `@router.api_route`.
Method from decorator name. Path from string argument.

### Colors

```mermaid
classDef entry   fill:#1c3144,stroke:#00d9ff,color:#fff
classDef service fill:#0d1b2a,stroke:#3a86ff,color:#fff
classDef data    fill:#1b2d3e,stroke:#53d8fb,color:#fff
classDef infra   fill:#1a1a2e,stroke:#a29bfe,color:#e0e0e0
classDef external fill:#2d2d44,stroke:#ffd93d,color:#fff
classDef job     fill:#1a1a2e,stroke:#6bcb77,color:#fff
classDef event   fill:#1a1a2e,stroke:#ff6b6b,color:#fff
```

---

## go-stdlib

**Signals**: `go.mod` + `*.go` files

### Directory → Layer/Type

| Directory | Type | Layer |
|-----------|------|-------|
| `cmd/` | Handler | entry |
| `internal/` | Service | service |
| `pkg/` | Service | service |
| `handlers/` | Handler | entry |
| `services/` | Service | service |
| `models/` or `types/` | Entity | data |
| `repository/` or `store/` | Repository | data |
| `config/` | Config | infra |
| `middleware/` | Config | infra |
| `client/` | Client | external |
| `jobs/` | Job | job |

### Dependency Inference

| Pattern | Confidence |
|---------|------------|
| `import "package"` | explicit |
| `http.HandleFunc(path, handler)` | explicit |
| `router.Handle(path, handler)` (gorilla/mux) | explicit |
| `chi.Router` patterns | explicit |
| Constructor func returning struct | inferred |
| Interface satisfying via struct field | inferred |

### Routes

Extract from `http.HandleFunc`, `router.Handle`, `router.Method` (chi), `v1.POST` (Gin).
Path from string argument. Method from pattern or default GET.

### Colors

```mermaid
classDef entry   fill:#003d5b,stroke:#00a8e8,color:#fff
classDef service fill:#001d3d,stroke:#0077b6,color:#fff
classDef data    fill:#002855,stroke:#53d8fb,color:#fff
classDef infra   fill:#1a1a2e,stroke:#a29bfe,color:#e0e0e0
classDef external fill:#2d2d44,stroke:#ffd93d,color:#fff
classDef job     fill:#1a1a2e,stroke:#6bcb77,color:#fff
classDef event   fill:#1a1a2e,stroke:#ff6b6b,color:#fff
```

---

## Vue 3 Frontend (cross-framework)

**Signals**: `frontend/` + `package.json` containing `vue` + `src/`

### Directory → Layer/Type

| Directory | Type | Layer |
|-----------|------|-------|
| `src/views/` | View | frontend |
| `src/components/` | Component | frontend |
| `src/components/*/` | Component | frontend |
| `src/services/` | Config | frontend |
| `src/stores/` | Config | frontend |
| `src/router/` | Router | frontend |
| `src/composables/` | Config | frontend |
| `src/main.js` | Config | frontend |

### Rules
- Scan `router/index.js` for `path` + `component` (imported from `../views/`)
- Every `.vue` file in `views/` → one component entry (type: `View`, layer: `frontend`)
- Every notable `.vue` in `components/` → one component entry (type: `Component`, layer: `frontend`)
- `domain` inferred from path: `views/OrderHistoryView.vue` → `order`
- Pinia stores → treat as infrastructure components for frontend layer
- Colors: same as `frontend` layer for the backend language pack

---

## External Service Detection Table

| Service Type | Config Keys / Import Patterns |
|-------------|-------------------------------|
| MySQL | `spring.datasource.url`, `mysql://`, `jdbc:mysql` |
| PostgreSQL | `spring.datasource.url`, `postgresql://`, `jdbc:postgresql` |
| Redis | `spring.data.redis.host`, `REDIS_URL`, `ioredis`, `redis-js` |
| MongoDB | `spring.data.mongodb.uri`, `MONGODB_URI`, `mongodb://`, `mongoose` |
| Neo4j | `spring.neo4j.uri`, `NEO4J_URL`, `org.neo4j` |
| Elasticsearch | `elasticsearch.url`, `ELASTICSEARCH_URL`, `elasticsearch` package |
| Qdrant (vector) | `ai.rag.vector-store.host`, `QDRANT_HOST`, `qdrant-client` |
| Kafka | `spring.kafka.bootstrap-servers`, `KAFKA_BROKERS`, `kafkajs`, `spring-kafka` |
| RabbitMQ | `spring.rabbitmq`, `RABBITMQ_URL`, `amqplib` |
| S3/Object Storage | `aws.s3`, `MINIO_ENDPOINT`, `boto3`, `@aws-sdk/client-s3` |
| DeepSeek API | `ai.deepseek.api-key`, `DEEPSEEK_API_KEY` |
| OpenAI / GPT | `OPENAI_API_KEY`, `openai` package |
| 通义千问 | `ai.qianwen.api-key`, `QIANWEN_API_KEY` |
| 支付宝 | `alipay.app-id`, `ALIPAY_*` env vars |
| Stripe | `STRIPE_API_KEY`, `stripe` package |
| Auth0 | `AUTH0_DOMAIN`, `AUTH0_*` |
| SMTP / Email | `spring.mail`, `SMTP_*`, `nodemailer` |
| Ollama | `ai.ollama.url`, `OLLAMA_HOST` |

---

## Aggregation Rules

### When to Aggregate
- Overview > 25 nodes → aggregate by domain
- Single module > 15 nodes → aggregate by layer
- Very large codebase → overview + per-domain + per-layer diagrams

### Target Node Counts
| Diagram Type | Target | Max |
|-------------|--------|-----|
| Overview (full project) | 15–25 | 30 |
| Per-domain | 8–15 | 20 |
| Per-layer | 5–10 | 15 |

---

## Quality Anti-Patterns

### Do NOT
- ❌ Emit a dependency without evidence
- ❌ Set `confidence: explicit` for naming convention only
- ❌ Include every file as a node (results in class diagram, not architecture)
- ❌ Omit `warnings` when scan was partial or project type was uncertain
- ❌ Use OpenAPI as a substitute for source scanning
- ❌ Output only an image — always include `system-data.json`
- ❌ Guess `implements`/`extends` relationships without source verification

### DO
- ✅ Group `Repository` as `R_*` (data access)
- ✅ Group `Config` and `middleware` as `infra` layer
- ✅ Label `inferred` for structural pattern matches
- ✅ Label `uncertain` when multiple interpretations exist
- ✅ Emit `warnings` for: partial scans, inferred components, missing templates
