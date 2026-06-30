# CodeArch — 语言包扩展指南

## 支持的语言

| Pack | 框架 | 状态 |
|------|------|--------|
| `java-spring.yaml` | Spring Boot | 完整 |
| `nodejs-express.yaml` | Node.js / Express | 完整 |
| `python-fastapi.yaml` | Python / FastAPI | 完整 |
| `go-stdlib.yaml` | Go / stdlib / chi / Gin | 完整 |

## 添加新语言包

创建 `LANGUAGES/<framework>.yaml`，包含以下字段：

```yaml
id: my-framework              # 唯一标识
name: My Framework            # 显示名称
priority: 40                  # 匹配优先级（越高越先匹配）
projectType: mylang           # 项目类型标识

# 检测信号 — 匹配任一个即选中此包
signals:
  - glob: "*.myext"
  - pattern: '"my-framework"' in package.json

# 源码根目录
sourceRoots:
  - "src"

# 目录 → 组件类型/分层
directories:
  controllers/:    { type: Controller, layer: entry }
  services/:       { type: Service, layer: service }
  models/:         { type: Entity, layer: data }
  config/:         { type: Config, layer: infra }

# 文件后缀 → 组件类型/分层（目录未匹配时的回退）
fileSuffix:
  Controller.ext:  { type: Controller, layer: entry }
  Service.ext:     { type: Service, layer: service }

# 依赖推断模式
dependencyPatterns:
  - pattern: "import\\s+(\\w+)"
    confidence: explicit
    description: "模块导入"

# 路由提取模式
routePatterns:
  - pattern: '@route\\(["\']([^"\']+)["\']'
    method: "ROUTE"
    pathExtract: "$1"

# 外部服务检测
externalServicePatterns:
  - configKey: "DATABASE_URL"
    serviceType: "database"
    pattern: "postgres|mysql"
    type: "explicit"

# ID 前缀（每种组件类型唯一前缀）
idPrefix:
  Controller: "CTRL_"
  Service:    "SVC_"
  Entity:     "ENT_"
  Config:     "CFG_"
```

### 字段说明

| 字段 | 必须 | 说明 |
|------|------|------|
| `id` | ✅ | 唯一标识符 |
| `name` | ✅ | 显示名称 |
| `signals` | ✅ | 语言/框架检测信号 |
| `sourceRoots` | ✅ | 源码目录列表 |
| `directories` | ✅ | 目录到 (type, layer) 的映射 |
| `fileSuffix` | — | 文件名后缀回退规则 |
| `dependencyPatterns` | ✅ | 依赖推断正则 |
| `routePatterns` | — | 路由提取正则 |
| `externalServicePatterns` | — | 外部服务检测规则 |
| `idPrefix` | ✅ | 组件 ID 前缀，每种 type 必须唯一 |
| `frontendScan` | — | 前端扫描配置（参考 java-spring.yaml） |

### 组件类型与分层

**分层 (layer)**:
`entry` | `service` | `data` | `infra` | `external` | `job` | `event` | `frontend`

**组件类型 (type)**:
`Controller` | `Service` | `Repository` | `Entity` | `Router` | `Handler` | `Config` | `Client` | `Job` | `Consumer` | `Module` | `Component` | `View`

### ID 前缀规范

所有语言包必须确保每种 type 使用唯一前缀，避免跨语言包合并时冲突：

| 类型 | 推荐前缀 |
|------|---------|
| Controller | `CTRL_` |
| Service | `SVC_` |
| Repository | `REPO_` |
| Entity | `ENT_` |
| Config | `CFG_` |
| Client | `CLT_` |
| Router | `RTR_` |
| Handler | `HDL_` |
| Job | `JOB_` |
| Consumer | `CNS_` |
| View | `VW_` |
| Component | `CMP_` |
