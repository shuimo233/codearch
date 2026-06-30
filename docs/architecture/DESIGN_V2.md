# CodeArch V2 设计文档：同源双态架构

> ⚠️ **状态说明 (2026-06-30)**：
> - ✅ Phase 1（三态产出）：已实现，SKILL.md 中的 Step 7-8 + TEMPLATES/README.onboard.md
> - ⏸️ Phase 2（tree-sitter AST）：推迟，当前聚焦做好 Phase 1 体验
> - ❌ Phase 3（MCP Server / 持久化）：已决定不做，避免与 codebase-memory-mcp 重复定位
>
> 本文档保留为设计参考。实际执行流程以 SKILL.md 为准。

> 从 "Agent Skill 生成架构图" 演进到 "一次分析，三态产出" 的代码智能平台。
> 
> 人类需要可视化浏览 + 叙事文档来理解项目；AI Agent 需要紧凑知识图谱来做查询推理。
> 二者从同一数据源生成，保证一致性。

---

## 目录

- [1. 动机：人类与 AI 的认知鸿沟](#1-动机人类与-ai-的认知鸿沟)
- [2. 现有项目对标分析](#2-现有项目对标分析)
- [3. 同源双态设计](#3-同源双态设计)
- [4. 统一数据模型：system-data.json v2](#4-统一数据模型system-datajson-v2)
- [5. 三态产出设计](#5-三态产出设计)
- [6. SKILL.md 执行流程变更](#6-skillmd-执行流程变更)
- [7. 语言包扩展：从目录正则到 AST 查询](#7-语言包扩展从目录正则到-ast-查询)
- [8. 落地路线图](#8-落地路线图)
- [9. 与兄弟项目的协同](#9-与兄弟项目的协同)

---

## 1. 动机：人类与 AI 的认知鸿沟

### 1.1 当前 CodeArch 的能力边界

CodeArch V1 能做什么：

- ✅ 扫描 4 种语言的项目源码（Java Spring / Node.js Express / Python FastAPI / Go）
- ✅ 按目录约定推断组件类型（Controller / Service / Repository / Entity）
- ✅ 生成交互式架构图（HTML，支持缩放/过滤/搜索/API 测试）
- ✅ 输出结构化 JSON（`system-data.json`）
- ✅ 检测外部服务（MySQL / Redis / Kafka / 支付宝等）
- ✅ 增量更新已有架构图

CodeArch V1 **不能**做什么：

- ❌ 没有函数/方法级的调用链追踪（粒度停在 Component 层）
- ❌ 没有为 AI Agent 优化的紧凑格式（JSON 体积大、token 占用高）
- ❌ 没有人类阅读的叙事文档（新成员看架构图仍需猜测"从哪开始读"）
- ❌ 没有死代码检测、循环依赖检测（仅靠 pattern 规则）
- ❌ 没有跨模块影响分析（"改了 X，会影响什么？"）
- ❌ 依赖目录命名约定，非标准目录结构会漏扫
- ❌ 不持久化，每次全量重扫

### 1.2 为什么要双态

| | 人类需要什么 | AI Agent 需要什么 |
|---|---|---|
| **格式** | 可视化图表、自然语言叙述 | 结构化记录、可查询图 |
| **关注点** | "这个项目做什么？从哪开始读？" | "哪个函数处理这个路由？改了 X 会影响 Y 吗？" |
| **粒度** | 模块/组件级就够 | 需要函数/方法/路由级精度 |
| **交互** | 点击、拖拽、搜索 | query / trace / impact 工具调用 |
| **Token 敏感度** | 不敏感 | 极度敏感（120× 差异） |

**核心矛盾**：同一份 `system-data.json`，人类看嫌太干，AI 看嫌太胖。

**解决方案**：不要二选一，而是让同一份分析结果产出三种格式，各取所需。

---

## 2. 现有项目对标分析

### 2.1 DeusData/codebase-memory-mcp（21.8k ⭐）

| 维度 | codebase-memory-mcp | 可汲取的经验 |
|------|---------------------|-------------|
| **语言覆盖** | 158 种（tree-sitter AST 编译进二进制） | 引入 tree-sitter WASM 替代目录正则 |
| **分析粒度** | 函数/类/方法/路由/接口级 | 从 Component 级细化到 Function/Method 级 |
| **知识图谱** | 14 Node Labels + 15 Edge Types | edges 增加 CALLS / IMPLEMENTS / HTTP_CALLS / DATA_FLOWS |
| **搜索能力** | BM25 FTS5 + 语义搜索 + Cypher 图查询 | 增加 search_graph / trace_path 能力 |
| **持久化** | SQLite WAL + 后台 watcher + team-shared artifact | 持久化索引，增量更新，团队共享 |
| **性能** | Linux 内核 28M LOC，3 分钟 | 批量扫描而非逐文件 read |
| **Token 效率** | 5 次查询 ~3,400 tokens（vs 412,000） | 图结构天然比文本紧凑 |
| **多 Agent** | 自动检测 11 种 Agent 并写入配置 | 参考 context-gatekeeper 的 CLI 模式 |
| **缺失** | **无人类可读的架构图 / 引导文档** | **这是 CodeArch 的核心差异优势** |

### 2.2 Context-Gatekeeper（内部项目）

| 可复用能力 | 说明 |
|-----------|------|
| MCP server 架构 | `server.ts` + `tools/` 的代码结构可直接参考 |
| Watchdog 权限模型 | 三层 Token 设计可引入到 CodeArch 的管理工具 |
| After-Chain 自动编排 | store→extract→recall 的工具链模式 |
| CLI 自动安装 | `context-gatekeeper-cli install --all` 可复用到 CodeArch |
| sql.js 持久化 | 纯 JS SQLite，已验证可用于索引存储 |

### 2.3 定位差

```
codebase-memory-mcp:  代码知识图谱引擎（AI 专用，无人视图）
CodeArch V1:          架构图生成器（人类专用，无 AI 专用产出）
CodeArch V2 目标:      双态代码智能平台（人类视图 + AI 图谱，同源生成）
```

**CodeArch 的独特价值**：codebase-memory-mcp 无人类可读产出，这正是 CodeArch 的差异化优势。V2 不是丢弃 V1 的架构图，而是**在架构图之上**增加 AI 图谱和叙事文档。

---

## 3. 同源双态设计

### 3.1 总体架构

```
                            ┌──────────────────────────┐
                            │    源码扫描 (一次分析)      │
                            │  AST 解析 + 目录扫描 +     │
                            │  依赖推断 + 影响分析       │
                            └──────────┬───────────────┘
                                       │
                            ┌──────────▼───────────────┐
                            │   system-data.json v2    │
                            │   统一数据源 (知识图谱)    │
                            │                          │
                            │  components (细粒度)      │
                            │  + graph.nodes / edges   │
                            │  + onboarding 数据        │
                            │  + impact_map 数据        │
                            └──┬─────────┬─────────┬───┘
                               │         │         │
                  ┌────────────▼──┐ ┌───▼────────▼───┐ ┌───────────────┐
                  │  graph.json   │ │architecture.html│ │README.onboard │
                  │  AI 优化       │ │  人类交互视图    │ │   .md (NEW)   │
                  │  token-effic. │ │  (保留并增强)    │ │  人类阅读入口  │
                  │  ~1,200 tokens│ │                 │ │               │
                  └───────┬───────┘ └─────────────────┘ └───────────────┘
                          │
                 ┌────────▼────────┐
                 │   MCP Tools     │
                 │  search_graph   │
                 │  trace_path     │
                 │  get_module     │
                 │  detect_impact  │
                 │  onboard_project│
                 └─────────────────┘
```

### 3.2 核心原则

| 原则 | 说明 |
|------|------|
| **一次分析** | 所有数据从同一次扫描派生，保证一致性 |
| **图即真相** | 知识图谱是唯一数据源，视图和文档都是它的渲染 |
| **Token 优先** | AI 产出极致压缩（短 key、展平数组、无冗余字段） |
| **叙事引导** | 人类产出必须回答 "从哪开始 / 如何理解 / 注意什么" |
| **渐进深度** | 从组件级→函数级逐步细化，不一次要求完美 |
| **增量友好** | 支持持久化索引 + 文件变更检测，避免全量重扫 |

---

## 4. 统一数据模型：system-data.json v2

### 4.1 完整 Schema（顶层）

```json
{
  "meta": { /* V1 元数据，保持不变 */ },

  // ────────── 已有结构（增强）──────────
  "components": [],        // V2: 粒度从 Component 细化到 Function/Class/Method
  "dependencies": [],      // V2: edge 类型扩展
  "externalServices": [],  // V1: 保持不变
  "domains": [],           // V1: 保持不变
  "warnings": [],          // V1: 保持不变

  // ────────── V2 新增：AI 专用 ──────────
  "graph": {
    "nodes": [],           // 知识图谱节点（短 key，token 优化）
    "edges": []            // 所有关系边（细粒度）
  },

  // ────────── V2 新增：人类专用 ──────────
  "onboarding": {
    "project_summary": "",   // 一段话概括
    "tech_stack": [],        // 技术栈列表
    "where_to_start": [],    // 建议阅读入口
    "modules": [],           // 模块级描述
    "key_flows": [],         // 关键业务流程
    "conventions": [],       // 代码约定
    "gotchas": []            // 注意事项/坑
  },

  // ────────── V2 新增：影响分析 ──────────
  "impact_map": {
    "hotspots": [],         // 高入度依赖的热点组件
    "dead_code": [],        // 无调用者的死代码
    "circular_deps": [],    // 循环依赖
    "architecture_smells": [] // 架构异味
  },

  // ────────── V2 新增：索引元数据 ──────────
  "index_meta": {
    "version": 2,
    "fingerprint": "",      // 源码指纹 (git tree hash)
    "incremental_base": "", // 增量更新基准
    "file_count": 0,
    "scan_duration_ms": 0
  }
}
```

### 4.2 Components 粒度细化

```json
// V1 (组件级)
{
  "id": "C_ORDER",
  "name": "OrderController",
  "type": "Controller",
  "layer": "entry",
  "file": "controller/OrderController.java",
  "routes": [{"method": "POST", "path": "/api/orders"}],
  "methods": ["createOrder", "getOrder", "cancelOrder"]
}

// V2 (方法级细化)
{
  "id": "C_ORDER",
  "name": "OrderController",
  "type": "Controller",
  "layer": "entry",
  "file": "controller/OrderController.java",
  "routes": [
    { "method": "POST", "path": "/api/orders", "handler": "createOrder" },
    { "method": "GET", "path": "/api/orders/{id}", "handler": "getOrder" },
    { "method": "PUT", "path": "/api/orders/{id}/cancel", "handler": "cancelOrder" }
  ],
  "methods": [
    {
      "name": "createOrder",
      "params": ["@RequestBody CreateOrderRequest req"],
      "returns": "ResponseEntity<Order>",
      "calls": ["svc_order.validateOrder", "svc_order.createOrder"],
      "annotations": ["@PostMapping", "@PreAuthorize('hasRole(USER)')"]
    }
  ]
}
```

### 4.3 Graph：AI 优化节点/边结构

```json
// AI-optimized：短 key，无冗余
{
  "graph": {
    "nodes": [
      {
        "i": "fn_createOrder",           // id (短前缀)
        "l": "Function",                  // label
        "n": "OrderController.createOrder", // name (全限定)
        "f": "controller/OrderController.java:34", // file:line
        "e": ["POST /api/orders"],       // exports (对外暴露)
        "p": ["CreateOrderRequest"],     // params
        "r": "ResponseEntity<Order>",    // returns
        "d": "order"                      // domain
      }
    ],
    "edges": [
      { "f": "fn_createOrder", "t": "fn_validateOrder", "y": "CALLS" },
      { "f": "ctrl_order", "t": "svc_order", "y": "INJECTS" },
      { "f": "svc_order", "t": "MySQL", "y": "QUERIES" },
      { "f": "fn_sendNotify", "t": "fn_sendEmail", "y": "ASYNC_CALLS" }
    ]
  }
}
```

**Edge 类型全集**：

| Type | 含义 | 示例 |
|------|------|------|
| `CALLS` | 同步方法调用 | Controller → Service |
| `ASYNC_CALLS` | 异步调用 | Service → @Async 方法 |
| `INJECTS` | 依赖注入 | Controller 注入 Service |
| `IMPLEMENTS` | 接口实现 | ServiceImpl → Service 接口 |
| `INHERITS` | 类继承 | ChildController → BaseController |
| `HTTP_CALLS` | 跨服务 HTTP 调用 | Service → PaymentClient |
| `QUERIES` | 数据库查询 | Repository → MySQL |
| `SUBSCRIBES` | 消息订阅 | Listener → Kafka topic |
| `PUBLISHES` | 消息发布 | Service → Kafka topic |
| `DATA_FLOWS` | 数据流转 | dto → entity 转换 |

### 4.4 Onboarding：人类引导数据

```json
{
  "onboarding": {
    "project_summary": "这是一个 Spring Boot 3.x 电商后端服务，采用 DDD-lite 按业务域分包，包含 order/product/payment/logistics 四个域。核心入口是 OrderController（12 个端点），80% 的流量经过 OrderService。依赖 MySQL + Redis + 支付宝。",
    
    "tech_stack": [
      "Java 17", "Spring Boot 3.x", "Spring Security",
      "MySQL 8", "Redis 7", "支付宝 SDK", "Docker"
    ],

    "where_to_start": [
      {
        "file": "controller/OrderController.java",
        "why": "主入口 — 12 个 REST API，覆盖订单 CRUD + 支付 + 退款",
        "priority": 3
      },
      {
        "file": "service/OrderServiceImpl.java",
        "why": "核心业务逻辑 — 订单状态机、库存校验、支付编排",
        "priority": 3
      },
      {
        "file": "entity/Order.java",
        "why": "核心数据模型 — 订单实体定义，包含状态枚举",
        "priority": 2
      },
      {
        "file": "config/SecurityConfig.java",
        "why": "安全配置 — JWT 认证 + 角色权限模型",
        "priority": 2
      }
    ],

    "modules": [
      {
        "name": "order",
        "purpose": "订单生命周期管理：创建、支付、发货、取消、退款",
        "entry_points": ["POST /api/orders", "GET /api/orders/{id}"],
        "key_classes": ["OrderController", "OrderService", "OrderRepository"],
        "depends_on": ["product", "payment", "logistics"],
        "complexity": "high",
        "node_count": 45
      }
    ],

    "key_flows": [
      {
        "name": "用户下单完整链路",
        "description": "从购物车提交到支付完成的全流程",
        "trigger": "POST /api/orders (用户提交订单)",
        "steps": [
          { "component": "OrderController.createOrder", "action": "接收请求，参数校验" },
          { "component": "OrderService.createOrder", "action": "构建订单对象" },
          { "component": "InventoryService.checkStock", "action": "检查库存" },
          { "component": "PaymentGateway.charge", "action": "调用支付宝预下单" },
          { "component": "OrderRepository.save", "action": "持久化订单" },
          { "component": "InventoryService.deduct", "action": "扣减库存" },
          { "component": "NotificationService.sendEmail", "action": "发送确认邮件（异步）" }
        ],
        "rollback": "支付失败 → 释放库存 → 标记订单为 CANCELLED",
        "diagram_type": "sequence"
      }
    ],

    "conventions": [
      "所有 Service 接口必须有对应的 ServiceImpl",
      "Controller 不得直接注入 Repository（发现 1 处违规）",
      "异常统一使用 @RestControllerAdvice 处理",
      "DTO 命名规范：{Entity}{Action}Request / {Entity}Response",
      "API 路径前缀：/api/v1/"
    ],

    "gotchas": [
      {
        "severity": "error",
        "title": "循环依赖",
        "detail": "OrderService ↔ InventoryService 存在循环依赖，当前通过 @Lazy 缓解，计划拆分为事件驱动。修改任一方需格外小心。"
      },
      {
        "severity": "warning",
        "title": "PaymentGateway 超时配置",
        "detail": "支付宝超时时间在 application.yml 中配置而非代码常量，修改时需同步更新告警规则。"
      },
      {
        "severity": "info",
        "title": "遗留代码",
        "detail": "LegacyUtil.deprecatedMethod() 无调用者，计划在 v2.1 移除。"
      }
    ]
  }
}
```

---

## 5. 三态产出设计

### 5.1 graph.json — AI Agent 专用

**设计目标**：在 Agent session 启动时用最少 token 注入项目全貌。

```json
{
  "_v": 2,
  "_project": "ecommerce-api",
  "_lang": "java-spring",
  "_brief": "215 nodes, 480 edges, 4 domains. search_graph / trace_path to explore.",
  
  "n": [
    {"i":"ctrl_order","l":"Controller","n":"OrderController","f":"controller/OrderController.java","e":["POST /api/orders","GET /api/orders/{id}","PUT /api/orders/{id}/cancel","DELETE /api/orders/{id}"],"d":"order"},
    {"i":"svc_order","l":"Service","n":"OrderServiceImpl","f":"service/OrderServiceImpl.java","c":["repo_order","svc_inventory","client_payment"],"d":"order"},
    {"i":"repo_order","l":"Repository","n":"OrderRepository","f":"repository/OrderRepository.java","q":"MySQL","d":"order"}
  ],
  
  "e": [
    {"f":"ctrl_order","t":"svc_order","y":"INJECTS"},
    {"f":"svc_order","t":"repo_order","y":"CALLS"},
    {"f":"svc_order","t":"svc_inventory","y":"CALLS"},
    {"f":"svc_order","t":"client_payment","y":"HTTP_CALLS"},
    {"f":"repo_order","t":"MySQL","y":"QUERIES"}
  ],
  
  "d": [
    {"n":"order","c":["ctrl_order","svc_order","repo_order","entity_order"],"x":["product","payment"]},
    {"n":"product","c":["ctrl_product","svc_product","repo_product"],"x":[]}
  ],
  
  "x": [
    {"n":"MySQL","t":"database","k":"spring.datasource.url"},
    {"n":"Redis","t":"cache","k":"spring.data.redis.host"},
    {"n":"支付宝","t":"payment","k":"alipay.gateway-url"}
  ],
  
  "h": [
    {"f":"svc_order","in":8,"out":5,"risk":"high","reason":"8 inbound deps, any change has wide impact"}
  ],
  
  "z": [
    {"n":"LegacyUtil.deprecatedMethod","f":"util/LegacyUtil.java:23","reason":"zero callers, deprecated 2025"}
  ]
}
```

**Token 效率估算**：

| 场景 | 当前方式 | graph.json | 节省 |
|------|---------|-----------|------|
| 理解项目结构 | ~50,000 tokens (逐文件浏览) | ~1,200 tokens | **97.6%** |
| 查找功能的入口 | ~15,000 tokens (grep + read) | ~200 tokens (search_graph) | **98.7%** |
| 追踪调用链 | ~30,000 tokens (逐文件追踪) | ~300 tokens (trace_path) | **99.0%** |

**配套 MCP Tools**：

| Tool | 输入 | 输出 | 用途 |
|------|------|------|------|
| `onboard_project` | `repo_path` | 注入 session 上下文的架构摘要 | Session 启动时自动调用 |
| `search_graph` | `query`, `label?`, `domain?` | 匹配的节点列表 | 查找组件/函数 |
| `trace_path` | `node_id`, `direction`, `depth` | 调用链（上游/下游） | 理解数据流 |
| `get_module` | `domain_name` | 模块完整上下文 | 快速理解一个模块 |
| `detect_impact` | `file_path` | 受影响组件列表 + 风险等级 | 修改前评估影响 |
| `find_entry_points` | — | 所有 API 入口 | 知道从哪开始 |

### 5.2 architecture.html — 人类交互视图（增强）

保留 V1 所有功能，增加：

| 增强点 | 说明 | 数据来源 |
|--------|------|---------|
| **热度图模式** | 节点大小/颜色按 inbound deps 数量变化 | `impact_map.hotspots` |
| **死代码标记** | 红色虚线边框 + tooltip | `impact_map.dead_code` |
| **循环依赖高亮** | 参与循环的边闪烁红色 | `impact_map.circular_deps` |
| **代码链接** | 双击节点/边 → 跳转源码 | `components[].file` + `graph.edges` |
| **Onboarding 侧边栏** | 右侧常驻 "新成员引导" 面板 | `onboarding` 数据 |
| **关键流程动画** | "下单流程" 自动高亮节点序列 | `onboarding.key_flows` |

### 5.3 README.onboard.md — 人类叙事文档（NEW）

完整模板见 [附录 A](#附录-a-readmeonboardmd-模板)。

核心设计原则：
- **第一屏必须回答三个问题**：这是什么项目？从哪开始读？有什么坑？
- **目录即导航**：每个模块一页，包含入口、依赖、复杂度
- **关键流程可视化**：Mermaid 序列图 + 文字描述
- **警告前置**：循环依赖、热点、死代码等直接标红

---

## 6. SKILL.md 执行流程变更

### 6.1 新流程（8 步）

```
Step 0: 范围检测 (已有)
  → 检测 monorepo/单体、识别所有 source roots

Step 1: 语言检测 (已有)
  → 匹配语言包、识别框架版本

Step 2: AST 级细粒度扫描 (增强)
  旧: 按目录约定正则匹配，提取组件名/类型/路由
  新: tree-sitter AST 解析，提取:
    - 类/接口/枚举定义
    - 方法签名 + 注解/装饰器
    - 路由定义 (HTTP method + path)
    - 注入点 (构造函数参数 / @Autowired 字段)
    - 继承/实现关系

Step 3: 依赖重建 + 调用链构建 (增强)
  旧: 正则模式匹配 (如 XController → XService by naming)
  新: 
    - 从 AST 提取方法调用链 (fn_A calls fn_B)
    - 跨文件 import 解析
    - HTTP client 调用检测
    - 消息队列 publish/subscribe 检测
  产出: graph.edges (CALLS / INJECTS / IMPLEMENTS / HTTP_CALLS / ...)

Step 4: 外部服务检测 (已有)
  → 扫描配置文件 + SDK imports

Step 5: 影响分析 (NEW)
  → 入度统计 → 热点检测
  → 出度统计 → 死代码检测
  → 环检测 (DFS) → 循环依赖
  → 架构异味 (Controller 直接访问 Repository 等)
  产出: impact_map

Step 6: 聚合 (已有)
  → nodeCount > 25 → 按域聚合

Step 7: Onboarding 数据生成 (NEW)
  → 项目摘要 (从 meta + domains 推断)
  → 推荐入口 (按入度 + routes 数量排序)
  → 模块描述 (从 domain + components 推断)
  → 关键流程 (从 routes → calls 构建 sequence)
  → 约定推断 (从 annotation pattern 统计)
  → 注意事项 (从 impact_map warnings 转换)
  产出: onboarding

Step 8: 三态输出 (增强)
  旧: architecture.html + system-data.json
  新:
    1. system-data.json v2 (统一数据源)
    2. graph.json (AI-optimized, from system-data.json 裁剪)
    3. architecture.html (Human visual, from system-data.json 渲染)
    4. README.onboard.md (Human narrative, from onboarding 数据渲染)
```

### 6.2 Step 7 详细规则：Onboarding 自动生成

#### 项目摘要生成规则

```
IF project has ≤ 5 domains:
  summary = "{projectName} 是一个 {framework} 项目，包含 {domain_count} 个业务域：{domain_list}。"
           + "核心入口是 {top_entry_point}（{route_count} 个端点）。"
           + "依赖 {external_service_list}。"
ELSE:
  summary = "{projectName} 是一个 {framework} 大型项目，包含 {domain_count} 个业务域。"
           + "主要入口分布在 {top_3_entry_points}。"
           + "外部依赖：{external_service_list}。"
```

#### 推荐入口排序规则

```
对于所有 entry 层组件，按以下加权排序：
  priority = routes.length * 3 
           + (inbound_deps * 2) 
           + (methods.length * 1)
取 Top 5，赋 priority 3/2/1
```

#### 模块描述生成规则

```
对于每个 domain:
  purpose = "[domain] 模块管理 {从实体/服务名推断}"
  entry_points = [从该域所有 Controller/Router 的 routes 提取]
  key_classes = [该域 Top 5 组件按入度排序]
  depends_on = [从 edges 提取该域组件指向其他域组件的边]
  complexity = 
    low:  node_count ≤ 10
    medium: 10 < node_count ≤ 30
    high: node_count > 30
```

#### 关键流程推断规则

```
对于每个高优先级入口方法:
  1. 从 entry method 出发
  2. 沿 CALLS edge BFS 遍历到 data 层
  3. 收集路径上的所有方法调用
  4. 去重、按调用顺序排列
  5. 生成 sequence flow 描述
只保留 depth ≥ 3 的流程（太短无价值）
```

---

## 7. 语言包扩展：从目录正则到 AST 查询

### 7.1 当前方式的问题

```yaml
# V1: 依赖目录命名约定
directories:
  controller/:    { type: Controller, layer: entry }
  service/impl/:  { type: Service, layer: service }
```

问题：
- 非标准目录名会漏扫
- 无法区分 Controller 和普通类
- 无法提取路由定义
- 无法提取调用链
- 每增加一种框架就要手写目录映射

### 7.2 V2 方案：tree-sitter AST 查询

```yaml
# V2: 指定 language + AST query
id: java-spring
language: java                    # tree-sitter language name
grammar: "tree-sitter-java"       # npm package name

ast_queries:
  controllers:
    query: |
      (class_declaration
        (modifiers
          (annotation
            name: (identifier) @ann_name
            (#match? @ann_name "RestController|Controller")))
        name: (identifier) @class_name
        body: (class_body) @body)
    extract:
      id: "ctrl_{class_name}"
      type: "Controller"
      layer: "entry"
      file: "$filepath"

  services:
    query: |
      (class_declaration
        (modifiers
          (annotation
            name: (identifier) @ann_name
            (#match? @ann_name "Service")))
        name: (identifier) @class_name
        body: (class_body) @body)
    extract:
      id: "svc_{class_name}"
      type: "Service"
      layer: "service"

  routes:
    query: |
      (annotation
        name: (identifier) @ann_name
        (#match? @ann_name "GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping|RequestMapping")
        arguments: (annotation_argument_list
          (element_value_pair
            key: (identifier) @key
            value: (string_literal) @path)))
    extract:
      method: "derive from @ann_name"
      path: "@path"

  methods:
    query: |
      (method_declaration
        (modifiers (annotation)?)*
        type: (_) @return_type
        name: (identifier) @method_name
        parameters: (formal_parameters) @params)
    extract:
      name: "@method_name"
      returns: "@return_type"
      params: "@params"

  injections:
    query: |
      (field_declaration
        (modifiers
          (annotation
            name: (identifier) @ann_name
            (#match? @ann_name "Autowired|Inject|Resource"))))
    extract:
      injects: "field_type"

  calls:
    query: |
      (method_invocation
        object: (identifier)? @object
        name: (identifier) @called_method)
    extract:
      from: "current_method"
      to: "@object.@called_method"
      type: "CALLS"
```

### 7.3 语言覆盖优先级

```
Phase 2.1 (优先): TypeScript/JavaScript, Python, Java, Go   (覆盖 95% 的编码 Agent 场景)
Phase 2.2:       Rust, C#, PHP, Ruby, Kotlin, Swift         (覆盖到 99%)
Phase 2.3:       其他 148 种语言 (tree-sitter 原生支持)     (长尾覆盖)
```

---

## 8. 落地路线图

### Phase 1: 零侵入增强（当前 V1 基础上）— 1 周

**不改扫描逻辑，只增加输出格式。**

| 任务 | 产出 | 工作量 |
|------|------|--------|
| 1.1 扩展 `TEMPLATES/system-data.json` schema | 增加 `graph`, `onboarding`, `impact_map` 字段定义 | 2h |
| 1.2 编写数据转换层 | `system-data.json v1 → graph.json` (裁剪+压缩) | 3h |
| 1.3 编写 `README.onboard.md` 模板 | 从 `components + dependencies + domains` 渲染叙事文档 | 4h |
| 1.4 SKILL.md Step 7→8 拆分 | 增加 Step 7 (onboarding 生成) | 2h |
| 1.5 更新 `REFERENCE.md` | 文档化新 schema | 1h |

**里程碑**：同一个项目扫描后，同时产出 `graph.json` + `architecture.html` + `README.onboard.md`。

### Phase 2: 引入 tree-sitter AST 解析 — 2-3 周

| 任务 | 产出 | 工作量 |
|------|------|--------|
| 2.1 安装 `web-tree-sitter` + 4 种 grammar | npm deps | 2h |
| 2.2 编写 AST query 引擎 | `src/ast-query.ts`: 加载 grammar → 执行 query → 提取结构化数据 | 8h |
| 2.3 重写 4 个语言包为 AST query 格式 | `LANGUAGES/java-spring.yaml` 等 | 8h |
| 2.4 实现调用链构建 | 跨文件 method invocation 解析 → `CALLS` edges | 6h |
| 2.5 实现影响分析 | 入度统计、死代码检测、循环依赖检测 | 4h |
| 2.6 性能基准测试 | 对比 V1 vs V2 扫描速度 + token 效率 | 2h |

**里程碑**：分析方法级粒度，产出真正的知识图谱 edges。

### Phase 3: MCP Server + 持久化 — 3-4 周

| 任务 | 产出 | 工作量 |
|------|------|--------|
| 3.1 MCP server 骨架 | 参考 context-gatekeeper 的 `server.ts` 架构 | 8h |
| 3.2 实现 6 个 MCP tools | search_graph, trace_path, get_module, detect_impact, onboard_project, find_entry_points | 12h |
| 3.3 sql.js 持久化索引 | 增量更新、指纹检测 | 8h |
| 3.4 CLI 安装器 | `npx codearch install --all` 自动检测 Agent | 6h |
| 3.5 team-shared artifact | `.codearch/index.db` git-tracked | 4h |
| 3.6 跨 Agent 兼容测试 | Cursor / Claude Code / Cline / Continue | 6h |

**里程碑**：CodeArch 成为一个完整的 MCP server，所有 MCP 兼容 Agent 可用。

---

## 9. 与兄弟项目的协同

### 9.1 与 context-gatekeeper 的分工

```
context-gatekeeper:  约束管理 (Agent 应该遵守什么规则？)
                     "不要直接提交到 main 分支"
                     "所有新文件必须用 TypeScript strict mode"

CodeArch V2:         结构理解 (这个项目长什么样？)
                     "OrderController 是入口，改了 OrderService 会影响 Payment"
                     "这里有循环依赖要小心"
```

两者互补：CodeArch 告诉 Agent **项目是怎么组织的**，context-gatekeeper 告诉 Agent **在这个项目里应该遵守什么约定**。

Session 启动时的注入顺序：
```
1. CodeArch.onboard_project  → 注入项目结构上下文 (~500 tokens)
2. context-gatekeeper.memory_recall → 注入项目约束 (~300 tokens)
3. Agent 开始工作，拥有完整的项目认知
```

### 9.2 技术复用

| 从 context-gatekeeper 复用 | 用途 |
|---------------------------|------|
| `src/mcp/server.ts` 架构 | CodeArch MCP server 骨架 |
| `src/utils/watchdog.ts` | 索引写入权限控制 |
| `src/utils/db.ts` (sql.js) | 持久化索引存储 |
| `src/utils/after-chain.ts` | tool chaining（index→search→inject） |
| `bin/context-gatekeeper-cli.js` | Agent 自动检测 + 配置写入逻辑 |

---

## 附录 A: README.onboard.md 模板

```markdown
# 📘 {{projectName}} — 架构导览

> 🤖 自动生成于 {{generatedAt}} | {{nodeCount}} 个组件 | {{domainCount}} 个业务域 | {{routeCount}} 个 API 端点
> 
> 📊 [交互式架构图](./architecture.html) | 🗂️ [结构化数据](./system-data.json)

---

## 🗺️ 项目概览

{{projectSummary}}

| 指标 | 值 |
|------|-----|
| 技术栈 | {{techStack}} |
| 语言包 | {{languagePack}} |
| 源文件数 | {{fileCount}} |
| 测试覆盖率 | (需手动补充) |

---

## 🚪 从哪里开始阅读？

| 优先级 | 文件 | 为什么 |
|--------|------|--------|
{{#each whereToStart}}
| {{priorityStars}} | `{{file}}` | {{why}} |
{{/each}}

---

## 📦 业务域

{{#each modules}}

### {{emoji}} {{name}} ({{nameCn}})

**职责**：{{purpose}}  
**入口**：{{entryPoints}}  
**依赖**：{{dependsOn}}  
**核心类**：{{keyClasses}}  
**复杂度**：{{complexityBadge}} ({{nodeCount}} 组件)

{{/each}}

---

## 🔗 关键流程

{{#each keyFlows}}

### {{name}}

{{description}}

**触发条件**：`{{trigger}}`

```mermaid
sequenceDiagram
{{#each steps}}
    {{component}}->>+{{next.component}}: {{action}}
{{/each}}
```

**回滚逻辑**：{{rollback}}

{{/each}}

---

## ⚠️ 注意事项

| 严重级别 | 标题 | 详情 |
|----------|------|------|
{{#each gotchas}}
| {{severityEmoji}} | {{title}} | {{detail}} |
{{/each}}

---

## 🧩 架构决策记录 (ADR)

| ID | 决策 | 日期 |
|----|------|------|
{{#each adrs}}
| {{id}} | {{title}} | {{date}} |
{{/each}}
*(通过 CodeArch 生成后，手动补充决策背景和权衡)*

---

## 📐 架构图

打开 [`architecture.html`](./architecture.html) 查看交互式架构图：
- 🏗️ **分层视图**：Entry → Service → Data → Infra → External
- 🔄 **流程视图**：组件间调用流向
- 🔍 **搜索**：快速定位组件或路由
- 🌐 **API 测试**：直接在图中调用后端接口
- 🌓 **主题切换**：浅色/深色模式

---

## 📝 代码约定

{{#each conventions}}
- {{.}}
{{/each}}

---

*本文档由 [CodeArch](https://github.com/shuimo233/context-gatekeeper) 自动生成。运行 `npx codearch scan` 更新。*
```

---

## 附录 B: 对比总结

| 维度 | CodeArch V1 | codebase-memory-mcp | CodeArch V2 目标 |
|------|------------|---------------------|-----------------|
| 分析方式 | Agent 逐文件扫描 | tree-sitter AST (C 二进制) | tree-sitter WASM (Node.js) |
| 语言覆盖 | 4 | 158 | 10 (Phase 2.1) → 158 (Phase 2.3) |
| 分析粒度 | Component (类级) | Function/Class/Route | Function/Class/Route |
| 人类产出 | architecture.html | — 无 — | architecture.html + README.onboard.md |
| AI 产出 | system-data.json (大) | graph (紧凑，不可视) | graph.json (紧凑) + MCP tools |
| Token 效率 | ~50,000 (全量扫描) | ~3,400 (5 次查询) | ~1,200 (graph.json) |
| 持久化 | 无 | SQLite + 后台同步 | SQLite (sql.js) + 增量更新 |
| 团队共享 | 无 | graph.db.zst (git) | .codearch/index.db (git) |
| 部署 | Cursor Skill | 单二进制 | MCP server (npx) |
| 独特优势 | 架构图 + 人类视角 | 速度 + 深度 + 语言覆盖 | **双态**：人类文档 + AI 图谱 |

---

*文档版本: v1.0 | 作者: CodeArch Team | 日期: 2026-06-30*
