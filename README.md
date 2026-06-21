# CodeArch

> Architecture diagram generation skill for Cursor agents.

从源码自动生成交互式架构图（纯 HTML/CSS + JSON）。支持 Java Spring Boot、Node.js/Express、Python/FastAPI、Go。

**零外部依赖** — 生成的 HTML 文件完全自包含，内置浏览器可直接打开，无需 CDN。

## 快速使用

在 Cursor agent 中说：

```
生成架构图
architecture diagram
map the APIs
```

## 目录结构

```
docs/architecture/
├── SKILL.md                    ← Cursor Agent 入口（5 步执行流程）
├── REFERENCE.md                ← 语言包规则 + schema 参考
├── architecture.html           ← 交互式架构图（浏览器打开）
├── LANGUAGES/                  ← 语言支持包
│   ├── java-spring.yaml        # Java / Spring Boot
│   ├── nodejs-express.yaml     # Node.js / Express
│   ├── python-fastapi.yaml     # Python / FastAPI
│   └── go-stdlib.yaml          # Go / stdlib
├── TEMPLATES/                  ← 输出模板
│   ├── architecture.html       # HTML 视图模板（纯 HTML/CSS）
│   ├── system-data.json        # JSON 数据模板
└── SCRIPTS/
    ├── install.sh              # 一键安装
    ├── update.sh               # 更新语言包
    ├── test-codearch-full.js   # 完整测试套件
    └── TEST_GUIDE.md           # 测试指南
```

## 工作原理

1. **检测语言** — 匹配 `pom.xml`/`package.json`/`requirements.txt` 等信号
2. **扫描组件** — 按目录约定提取 Controller/Service/Repository/Entity
3. **推断依赖** — 从 `@Autowired`、注入字段、命名约定推断组件关系
4. **检测外部服务** — 从配置和 import 识别 MySQL/Redis/Neo4j/Qdrant 等
5. **渲染输出** — 生成 `architecture.html` + `system-data.json`

## 输出格式

| 文件 | 说明 |
|------|------|
| `architecture.html` | 交互式架构图（纯 HTML/CSS），支持缩放/平移/域过滤/节点高亮/API 测试 |
| `system-data.json` | 结构化 JSON，可被 CI 工具消费 |

### 架构图功能

- **分层视图** — 按 Frontend/Entry/Service/Data/Infra 分层展示
- **流程视图** — 水平布局展示组件流向
- **交互式高亮** — 点击组件高亮相关组件
- **域过滤** — 按业务域筛选组件
- **搜索** — 快速定位组件/路由
- **API 测试** — 直接在图中测试后端 API
- **主题切换** — 支持浅色/深色模式

## 安装

```bash
./SCRIPTS/install.sh
```

## 测试

```bash
# 运行完整测试套件
node ./SCRIPTS/test-codearch-full.js

# 或参考测试指南
cat ./SCRIPTS/TEST_GUIDE.md
```

## 支持的语言

| 语言 | 框架 | 状态 |
|------|------|------|
| Java | Spring Boot | 完整 |
| Node.js | Express | 完整 |
| Python | FastAPI | 完整 |
| Go | stdlib / chi / Gin | 完整 |

## 扩展语言包

参考 `LANGUAGES/README.md`，创建 `LANGUAGES/<framework>.yaml` 即可。

## License

MIT
