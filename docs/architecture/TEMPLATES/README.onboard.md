# 📘 {{PROJECT_NAME}} — 架构导览

> 🤖 由 CodeArch 自动生成于 {{GENERATED_AT}} | {{NODE_COUNT}} 个组件 | {{DOMAIN_COUNT}} 个业务域 | {{ROUTE_COUNT}} 个 API 端点
>
> 📊 [交互式架构图](./architecture.html) | 🗂️ [结构化数据](./system-data.json) | 🧠 [AI 知识图谱](./graph.json)

---

## 🗺️ 项目概览

{{PROJECT_SUMMARY}}

| 指标 | 值 |
|------|-----|
| 技术栈 | {{TECH_STACK}} |
| 语言包 | {{LANGUAGE_PACK}} |
| 源文件数 | {{FILE_COUNT}} |
| 外部依赖 | {{EXTERNAL_SERVICES}} |

---

## 🚪 从哪里开始阅读？

{{#WHERE_TO_START}}
| 优先级 | 文件 | 为什么 |
|--------|------|--------|
{{#rows}}
| {{PRIORITY}} | `{{FILE}}` | {{WHY}} |
{{/rows}}
{{/WHERE_TO_START}}

{{#NO_WHERE_TO_START}}
> ⚠️ 未检测到明确的入口文件。请手动补充。
{{/NO_WHERE_TO_START}}

---

## 📦 业务域

{{#MODULES}}

### {{EMOJI}} {{NAME}}

**职责**：{{PURPOSE}}

**入口**：{{ENTRY_POINTS}}

**依赖**：{{DEPENDS_ON}}

**核心类**：{{KEY_CLASSES}}

**复杂度**：{{COMPLEXITY_BADGE}} ({{NODE_COUNT}} 个组件)

{{/MODULES}}

{{#NO_MODULES}}
> ⚠️ 未检测到明确的业务域划分。项目可能较小或结构扁平。请查看下方组件清单。
{{/NO_MODULES}}

---

## 🔗 关键流程

{{#KEY_FLOWS}}

### {{NAME}}

{{DESCRIPTION}}

**触发条件**：`{{TRIGGER}}`

```mermaid
sequenceDiagram
{{#STEPS}}
    {{FROM}}->>+{{TO}}: {{ACTION}}
{{/STEPS}}
```

{{#ROLLBACK}}
**回滚逻辑**：{{TEXT}}
{{/ROLLBACK}}

{{/KEY_FLOWS}}

{{#NO_FLOWS}}
> ℹ️ 未检测到深度 ≥ 3 的关键业务流程。需要 AST 级扫描（Phase 2）来提取方法级调用链。当前可参考 [交互式架构图](./architecture.html) 中的组件依赖关系。
{{/NO_FLOWS}}

---

## ⚠️ 注意事项

{{#GOTCHAS}}
| 严重级别 | 标题 | 详情 |
|----------|------|------|
{{#rows}}
| {{SEVERITY}} | {{TITLE}} | {{DETAIL}} |
{{/rows}}
{{/GOTCHAS}}

{{#NO_GOTCHAS}}
未检测到严重架构问题。🎉
{{/NO_GOTCHAS}}

---

## 📐 架构图

打开 [`architecture.html`](./architecture.html) 查看交互式架构图：

- 🏗️ **分层视图**：Entry → Service → Data → Infra → External → Job → Event → Frontend
- 🔄 **流程视图**：按业务域展示组件间调用流向
- 🔍 **搜索**：快速定位组件或路由
- 🌐 **API 测试**：直接在图中调用后端接口
- 🌓 **主题切换**：浅色/深色模式

---

## 📝 代码约定

{{#CONVENTIONS}}
- {{TEXT}}
{{/CONVENTIONS}}

{{#NO_CONVENTIONS}}
*(扫描中未检测到明确的代码约定模式)*
{{/NO_CONVENTIONS}}

---

## 🧩 架构决策记录 (ADR)

{{#ADRS}}
| ID | 决策 | 日期 |
|----|------|------|
{{#rows}}
| {{ID}} | {{TITLE}} | {{DATE}} |
{{/rows}}
{{/ADRS}}

{{#NO_ADRS}}
*(通过 CodeArch 生成后，手动补充架构决策的上下文和权衡)*
{{/NO_ADRS}}

---

*本文档由 [CodeArch](https://github.com/shuimo233/context-gatekeeper) 自动生成。运行 `生成架构图` 更新。*
