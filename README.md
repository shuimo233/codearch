# CodeArch

> Architecture diagram generation skill for AI coding agents (Cursor, Claude Code, etc).

从源码自动生成架构文档。**零外部依赖**，一次扫描产出四份固定文档：人看交互式架构图，Agent 看紧凑知识图谱。

支持 Java Spring Boot、Node.js/Express、Python/FastAPI、Go。

## 安装

### Claude Code

**项目级安装**（仅当前项目可用）：

```bash
# 在项目根目录执行
git clone https://github.com/shuimo233/codearch.git .claude/skills/codearch
```

**全局安装**（所有项目可用）：

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/shuimo233/codearch.git ~/.claude/skills/codearch
```

### Cursor

**项目级安装**：

```bash
git clone https://github.com/shuimo233/codearch.git .cursor/skills/codearch
```

**全局安装**：

```bash
mkdir -p ~/.cursor/skills
git clone https://github.com/shuimo233/codearch.git ~/.cursor/skills/codearch
```

### 其他 Agent（通用方式）

将 `docs/architecture/` 目录复制到项目根目录，Agent 即可读取 `SKILL.md` 执行：

```bash
git clone https://github.com/shuimo233/codearch.git /tmp/codearch
cp -r /tmp/codearch/docs/architecture ./docs/architecture
rm -rf /tmp/codearch
```

### 验证安装

安装后在 Agent 中输入以下任意一句即可触发：

```
生成架构图
architecture diagram
```

如果 Agent 正确加载了 Skill，它会按照 SKILL.md 的 8 步流程执行扫描并生成输出文件。

> **注意**：如果 Agent 没有自动识别，可以显式引用 Skill 文件：
> - Claude Code: `/skill` 然后选择 codearch，或输入 `请按照 docs/architecture/SKILL.md 执行`
> - Cursor: `@skill codearch` 或 `请按照 .cursor/skills/codearch/SKILL.md 执行`

## 目录结构

```
codearch/
├── SKILL.md                         ← Agent 入口（触发条件 + 流程摘要）
└── docs/architecture/
    ├── SKILL.md                     ← 完整 8 步执行流程
    ├── REFERENCE.md                 ← 语言包规则 + schema 参考
    ├── LANGUAGES/                   ← 语言支持包
    │   ├── README.md                # 扩展指南
    │   ├── java-spring.yaml         # Java / Spring Boot
    │   ├── nodejs-express.yaml      # Node.js / Express
    │   ├── python-fastapi.yaml      # Python / FastAPI
    │   └── go-stdlib.yaml           # Go / stdlib
    └── TEMPLATES/                   ← 输出模板
        ├── architecture.html        # 交互式架构图（纯 HTML/CSS）
        ├── system-data.json         # 统一数据源 schema（V2）
        └── README.onboard.md        # 人类导航文档模板
```

## 工作原理

1. **检测语言** — 匹配 `pom.xml`/`package.json`/`requirements.txt`/`go.mod` 信号
2. **扫描组件** — 按目录约定提取 Controller/Service/Repository/Entity 等
3. **推断依赖** — 从注入注解、导入语句、命名约定推断组件关系
4. **检测外部服务** — 从配置和 import 识别 MySQL/Redis/Kafka 等
5. **影响分析** — 热点检测、死代码、循环依赖
6. **生成导览** — 项目摘要、推荐入口、关键流程、注意事项
7. **三态输出** — 同时产出 `architecture.html` + `graph.json` + `README.onboard.md` + `system-data.json`

## 输出文件

| 文件 | 面向 | 说明 |
|------|------|------|
| `architecture.html` | 人类 | 交互式架构图（零依赖纯 HTML/CSS），缩放/平移/过滤/高亮/API 测试 |
| `README.onboard.md` | 人类 | 叙事架构导览——从哪开始读、有什么坑 |
| `graph.json` | AI Agent | 紧凑知识图谱（~1200 tokens），可快速注入上下文 |
| `system-data.json` | 工具 | 统一数据源，包含 onboarding/impact 数据 |

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
