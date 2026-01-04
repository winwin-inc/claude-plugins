# Wiki Generator 优化快速启动指南

## 🚀 下次会话开始步骤

### 1. 查看跟踪文档
```bash
cat TEMPLATE-OPTIMIZATION-TRACKER.md
```

### 2. 查看当前进度
- 查看 TEMPLATE-OPTIMIZATION-TRACKER.md 中的"总体进度"部分
- 找到下一个待完成的 Phase

### 3. 备份当前模板（每个会话开始前）
```bash
cp -r wiki_generator/.claude/templates wiki_generator/.claude/templates.backup.$(date +%Y%m%d)
```

### 4. 开始下一个 Phase
按照跟踪文档中的步骤执行

---

## 📋 优化阶段概览

| Phase | 名称 | 优先级 | 预计时间 | 状态 |
|-------|------|--------|----------|------|
| 1 | 统一模板变量格式 | 🔴 高 | 1-2h | ⏳ 待开始 |
| 2 | 添加 Claude 指导注释 | 🔴 高 | 2-3h | ⏳ 待开始 |
| 3 | 优化代码示例格式 | 🟡 中 | 2-3h | ⏳ 待开始 |
| 4 | 增强 API 文档支持 | 🟡 中 | 3-4h | ⏳ 待开始 |
| 5 | 优化 Mermaid 图表生成 | 🟢 低 | 2-3h | ⏳ 待开始 |
| 6 | 添加文档元数据 | 🟢 低 | 1-2h | ⏳ 待开始 |
| 7 | 优化章节结构 | 🟢 低 | 2-3h | ⏳ 待开始 |
| 8 | 更新 Skills | 🔴 高 | 4-6h | ⏳ 待开始 |

---

## 🎯 建议会话分配

### 会话 1: Phase 1-2（高优先级基础工作）
**目标**: 建立统一的基础，立即见效

### 会话 2: Phase 3-4（中等优先级改进）
**目标**: 增强代码展示和 API 文档

### 会话 3: Phase 5-6（低优先级优化）
**目标**: 可视化和元数据增强

### 会话 4: Phase 7-8（收尾工作）
**目标**: 结构优化和技能更新

### 会话 5: 测试验证（可选）
**目标**: 全面测试和文档更新

---

## 🔧 常用命令

### 备份模板
```bash
cp -r wiki_generator/.claude/templates wiki_generator/.claude/templates.backup.$(date +%Y%m%d)
```

### 检查变量格式
```bash
# 查找所有 {{ }} 格式的变量
grep -r '{{' wiki_generator/.claude/templates/

# 查找所有 { } 格式的变量
grep -r '{' wiki_generator/.claude/templates/ | grep -v '{{'
```

### 统计文件数量
```bash
# 统计模板文件数量
find wiki_generator/.claude/templates -name "*.md.template" | wc -l

# 统计 skills 文件数量
find wiki_generator/.claude/skills -name "*.md" | wc -l
```

### 对比参考项目
```bash
# 查看参考项目的文档格式
ls /home/yewenbin/work/tools/dingtalk-notable-connect/.qoder/repowiki/zh/content/
```

---

## 📝 完成检查清单

每个 Phase 完成后，在 TEMPLATE-OPTIMIZATION-TRACKER.md 中：
- [ ] 更新状态为 ✅ 已完成
- [ ] 记录完成日期
- [ ] 记录遇到的问题和解决方案
- [ ] 验证完成标准

---

## 💡 快速参考

### 变量格式标准
- ✅ 正确: `{project_name}`
- ❌ 错误: `{{project_name}}`

### 代码示例格式
```markdown
```python title="src/main.py"
# 代码内容
```
```

### Claude 指导注释
```markdown
<!-- Claude: 从 README.md 提取项目描述 -->
{project_description}
```

---

## 📚 关键文档

- **跟踪文档**: [TEMPLATE-OPTIMIZATION-TRACKER.md](./TEMPLATE-OPTIMIZATION-TRACKER.md)
- **优化计划**: `/home/yewenbin/.claude/plans/replicated-riding-planet.md`
- **参考项目 1**: `/home/yewenbin/work/tools/dingtalk-notable-connect/.qoder/repowiki`
- **参考项目 2**: `/home/yewenbin/work/common/dingtalk-sdk-generator/.qoder/repowiki`

---

**创建日期**: 2026-01-05
**下次会话**: Phase 1-2（统一变量格式 + Claude 指导注释）
