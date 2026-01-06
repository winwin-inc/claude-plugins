# Save Session Command

请执行以下任务来保存当前会话的计划和执行结果:

## 1. 创建保存目录结构

创建统一的目录结构:
```bash
mkdir -p docs/plans/sessions/$(date +%Y%m)
```

**说明**: 所有文档统一存储在 `docs/plans/` 目录下。

## 2. 保存计划文档（智能命名）

### 2.1 自动生成序号和摘要

如果存在 `plan.md` 或 `PLAN.md` 文件，自动生成规范的文件名：

```bash
# 步骤1: 获取当前最大序号
last_num=$(ls docs/plans/*.md 2>/dev/null | \
           sed -n 's/.*\/\([0-9]\{3,\}\)-.*/\1/p' | \
           sort -rn | head -1)
last_num=${last_num:-0}  # 如果没有文件，默认为0
let next_num=last_num+1
serial=$(printf "%03d" $next_num)

# 步骤2: 从 plan.md 提取标题生成摘要
title=$(grep -m1 '^# ' plan.md 2>/dev/null | sed 's/^# //' | sed 's/^\[.*\] //')
if [ -z "$title" ]; then
    title=$(sed -n '/^title:/p' plan.md | cut -d: -f2 | xargs)
fi
if [ -z "$title" ]; then
    title="plan"
fi

# 步骤3: 转换为文件名格式（小写、连字符、限制30字符）
summary=$(echo "$title" | \
          tr '[:upper:]' '[:lower:]' | \
          sed 's/[^a-z0-9]\+/-/g' | \
          sed 's/^-*\|-*$//g' | \
          cut -c1-30)

# 步骤4: 组合最终文件名
plan_filename="${serial}-${summary}.md"
plan_path="docs/plans/${plan_filename}"

echo "📋 计划文件名: $plan_filename"
```

### 2.2 复制并增强 plan.md

复制 plan.md 到目标路径，并在文件开头添加元数据:

```bash
cat > "$plan_path" << EOF
---
created: $(date '+%Y-%m-%d %H:%M:%S')
session_id: [当前会话标识]
status: completed
filename: ${plan_filename}
---

EOF

# 追加原 plan.md 内容
cat plan.md >> "$plan_path"

echo "✅ 计划已保存: $plan_path"
```

## 3. 生成执行摘要

创建会话摘要文件 `docs/plans/sessions/$(date +%Y%m)/session_$(date +%Y%m%d_%H%M%S).md`:

```bash
session_file="docs/plans/sessions/$(date +%Y%m)/session_$(date +%Y%m%d_%H%M%S).md"
plan_link="../../${plan_filename}"

cat > "$session_file" << EOF
# Claude Code 会话摘要

## 会话信息

- **执行时间**: $(date '+%Y-%m-%d %H:%M:%S')
- **工作目录**: $(pwd)
- **Git 分支**: $(git branch --show-current)
- **会话 ID**: [当前会话标识]

---

## 任务概述

### 主要目标

[请总结本次会话完成的主要任务，包括:]
- 主要目标
- 实施的关键步骤
- 使用的技术和工具

### 文件变更

\`\`\`bash
# 列出所有修改的文件
git status --short

# 显示变更统计
git diff --stat
\`\`\`

### 执行结果

[请描述:]
- ✅ 成功完成的任务
- ⚠️  遇到的问题及解决方案
- 📝 待办事项或后续建议
- 🧪 测试结果(如果有)

### 关键代码片段

[如果有重要的代码变更，摘录关键部分并说明其作用]

---

## 相关文档

- **计划文档**: [${plan_filename}](${plan_link})

---

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')
**状态**: ✅ 已完成
EOF

echo "✅ 会话摘要已保存: $session_file"
```

## 4. 生成索引模板

### 4.1 全局索引模板

**请将以下内容复制到 `docs/plans/README.md`:**

```markdown
# 项目计划文档索引

本目录包含所有项目计划和会话记录。

---

## 计划文档

### [001. Wiki Generator 插件系统改造](001-plugin-system-migration.md)
- **状态**: ✅ 已完成
- **创建日期**: 2025-01-06
- **会话ID**: calm-mapping-giraffe

### [${serial}. ${title}](plan_filename)
- **状态**: ✅ 已完成
- **创建日期**: $(date +%Y-%m-%d)
- **会话ID**: [当前会话标识]

<!-- 在此处添加新计划 -->

---

## 会话存档

- **[2025年01月](sessions/202601/README.md)** - 1 个会话

---

**最后更新**: $(date '+%Y-%m-%d %H:%M:%S')
```

### 4.2 月度索引模板

**请将以下内容复制到 `docs/plans/sessions/$(date +%Y%m)/README.md`:**

```markdown
# Claude Code 会话存档 - $(date +%Y年%m月)

本目录包含 $(date +%Y年%m月) 期间所有 Claude Code 会话的详细记录。

---

## 会话列表

### [$(date +%Y-%m-%d): 会话标题](session_$(date +%Y%m%d_%H%M%S).md)

**状态**: ✅ 已完成
**会话ID**: [会话ID]
**相关计划**: [${plan_filename}](../../${plan_filename})

**概述**: [会话概述...]

**关键成果**:
- [成果1]
- [成果2]

---

**最后更新**: $(date '+%Y-%m-%d %H:%M:%S')
```

## 5. 确认保存成功

输出保存结果摘要:

```
🎉 会话保存完成!

📁 保存位置:
  - 计划文档: docs/plans/${plan_filename}
  - 会话摘要: docs/plans/sessions/$(date +%Y%m)/session_$(date +%Y%m%d_%H%M%S).md

📋 下一步:
  1. 检查生成的文档内容
  2. 将全局索引模板复制到 docs/plans/README.md
  3. 更新月度索引 docs/plans/sessions/$(date +%Y%m)/README.md

🔗 快速导航:
  - 查看所有计划: cat docs/plans/README.md
  - 查看本月会话: cat docs/plans/sessions/$(date +%Y%m)/README.md
```

---

## 关键改进说明

### ✅ 移除的功能
1. **不再创建** `docs/claude-sessions/` 目录
2. **不再创建** `docs/execution-logs/` 目录
3. **不再追加** `history.log` 文件

### ✨ 新增的功能
1. **智能序号生成**: 自动扫描并递增序号（001、002、003...）
2. **智能摘要提取**: 从 plan.md 标题自动生成文件名摘要
3. **统一目录结构**: 所有文档集中在 `docs/plans/` 下
4. **自动关联**: 会话文件自动包含计划文档链接
5. **索引模板**: 提供全局和月度索引模板（需手动维护）

### 📋 文件命名规则

**Plan 文件**:
- 格式: `XXX-summary.md`
- 示例: `002-refactor-save-session.md`
- 规则:
  - XXX: 三位数字序号（001-999）
  - summary: 小写、连字符、最多30字符

**会话文件**:
- 格式: `session_YYYYMMDD_HHMMSS.md`
- 示例: `session_20260106_143000.md`
- 位置: `docs/plans/sessions/YYYYMM/`
