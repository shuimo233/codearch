# CodeArch Skill 测试流程

## 测试环境准备

### 1. 启动 HTTP 服务器

```powershell
cd "D:\Projects\web\online-shopping\online-shopping-system-master\e2e-test"
Start-Process -FilePath "python" -ArgumentList "-m http.server 8888" -WindowStyle Hidden
```

或使用 Node.js:

```bash
cd codearch/docs/architecture
npx serve . -p 8888
```

### 2. 浏览器测试步骤

使用 Cursor 内置浏览器测试架构图：

#### Step 1: 页面加载测试
- 导航到 `http://localhost:8888/architecture.html`
- 等待 Mermaid 渲染完成（约 3-5 秒）
- 截图确认页面正常显示

#### Step 2: 检查 systemData 完整性
在浏览器控制台执行：
```javascript
JSON.stringify({
  componentCount: systemData.components.length,
  metaNodeCount: systemData.meta.nodeCount,
  match: systemData.components.length === systemData.meta.nodeCount,
  domains: systemData.domains?.length,
  externalServices: systemData.externalServices?.length
})
```

#### Step 3: 检查组件树渲染
```javascript
JSON.stringify({
  treeNodes: document.querySelectorAll('.tree-node').length,
  layerGroups: document.querySelectorAll('.layer-group').length,
  visibleNodes: Array.from(document.querySelectorAll('.tree-node'))
    .filter(n => getComputedStyle(n).display !== 'none').length
})
```

#### Step 4: 检查 Mermaid 图渲染
```javascript
JSON.stringify({
  svgExists: !!document.querySelector('#mermaidContainer svg'),
  nodeCount: document.querySelectorAll('#mermaidContainer svg .node').length,
  edgeCount: document.querySelectorAll('#mermaidContainer svg .edgePath').length
})
```

#### Step 5: 测试交互功能
- 点击组件树中的组件 → 检查右侧详情面板
- 点击域名过滤器 → 检查组件列表过滤
- 点击主题切换 → 检查深色/浅色切换
- 点击分层/流程视图切换 → 检查视图切换

### 3. Playwright 自动化测试

```bash
cd codearch/docs/architecture
npm install playwright
node SCRIPTS/test-codearch-full.js
```

### 4. 常见问题修复

#### 问题：左侧组件列表为空
**原因**：旧版本代码使用中文层名称匹配
**修复**：确保 `renderTree()` 使用英文 key 遍历：
```javascript
const layerOrder = ['frontend', 'entry', 'service', 'data', 'infra', 'external', 'job', 'event'];
const layerLabel = { 'entry': '入口层', ... };
layerOrder.forEach(l => {
  if (!layers[l]) return;  // 使用英文 key
  html += `<div class="layer-title">${layerLabel[l]}</div>`;
});
```

#### 问题：Mermaid 图不渲染
**原因**：Mermaid CDN 加载失败
**修复**：
1. 检查网络连接
2. 手动注入 Mermaid CDN
3. 查看控制台错误

#### 问题：systemData 未定义
**原因**：`{{SYSTEM_DATA}}` 未被替换
**修复**：重新生成架构图，确保替换占位符

### 5. 测试检查清单

- [ ] 页面正常加载
- [ ] systemData 完整（componentCount === meta.nodeCount）
- [ ] 组件树显示正确数量的节点
- [ ] Mermaid SVG 渲染成功
- [ ] Mermaid 节点数量 > 0
- [ ] 点击组件显示详情
- [ ] 域名过滤器正常工作
- [ ] 主题切换正常工作
- [ ] Tab 切换正常
- [ ] 搜索功能正常
- [ [ ] 无控制台错误
