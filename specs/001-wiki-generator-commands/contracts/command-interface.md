# 命令接口契约

**版本**: 1.0.0
**最后更新**: 2025-01-03

---

## 命令文件格式

### 基本结构

所有命令文件必须遵循以下格式：

```markdown
---
description: 命令描述（必填）
argument-hint: 参数提示（可选）
allowed-tools: 工具列表（可选）
model: 模型名称（可选）
---

# 命令标题

## 任务描述
[具体的任务说明]

## 上下文
[分析上下文]

## 步骤
1. [步骤 1]
2. [步骤 2]
3. [步骤 3]

## 输出
- 输出文件：`path/to/file.md`
- 控制台：[成功/失败消息]

## 质量标准
- [标准 1]
- [标准 2]
```

### Frontmatter 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| description | string | ✅ | 命令描述，显示在 /help 中 |
| argument-hint | string | ❌ | 参数提示，显示在自动完成中 |
| allowed-tools | array | ❌ | 允许使用的工具列表 |
| model | string | ❌ | 指定的 AI 模型 |

---

## 参数占位符

### 所有参数：`$ARGUMENTS`

捕获所有传入的参数：

```markdown
---
description: 执行操作
---

执行操作：$ARGUMENTS
```

**使用示例**:
```bash
/wiki.fix-issue 123 high-priority
# $ARGUMENTS 变为 "123 high-priority"
```

### 位置参数：`$1`, `$2`, `$3`...

访问特定位置的参数：

```markdown
---
argument-hint: [pr-number] [priority] [assignee]
description: 审查 PR
---

审查 PR #$1，优先级为 $2，分配给 $3。
```

**使用示例**:
```bash
/wiki.review-pr 456 high alice
# $1 = "456", $2 = "high", $3 = "alice"
```

---

## 工具权限

### 允许所有工具

```yaml
---
allowed-tools: all
---
```

### 允许特定工具

```yaml
---
allowed-tools: Read, Glob, Grep, Write
---
```

### 限制特定命令

```yaml
---
allowed-tools: Bash(git add:*), Bash(git status:*)
---
```

---

## 输出规范

### 成功输出

**控制台消息**:
```
✅ 命令成功：[描述]
📄 生成文件：[文件路径]
⏱️ 耗时：[时间]
```

**文件输出**:
- 必须写入到指定路径
- 使用 Markdown 格式
- 包含适当的标题和结构

### 错误输出

**控制台消息**:
```
❌ 命令失败：[错误描述]

💡 建议：
- [建议 1]
- [建议 2]

🔗 帮助：/wiki.help
```

---

## 质量标准

所有命令必须满足：

1. **描述清晰**: description 字段准确描述命令功能
2. **参数明确**: 参数提示和使用示例清晰
3. **输出可预测**: 输出格式符合契约
4. **错误处理**: 提供友好的错误消息和建议
5. **性能达标**: 满足性能目标要求

---

## 示例命令

### 示例 1：无参数命令

```markdown
---
description: 初始化 Wiki 文档结构
---

# 初始化 Wiki 文档结构

## 任务
创建 Wiki 文档所需的目录结构和配置文件。

## 步骤
1. 创建 `docs/` 目录
2. 创建子目录
3. 生成配置文件

## 输出
- 目录：`docs/`
- 配置：`.claude/wiki-config.json`

## 质量标准
- 所有目录创建成功
- 配置文件包含默认值
```

### 示例 2：单参数命令

```markdown
---
argument-hint: [module-path]
description: 生成模块文档
---

# 生成模块文档

## 任务
为指定模块生成详细文档。

## 步骤
1. 分析模块路径 `$1`
2. 提取 API 接口
3. 生成使用示例

## 输出
- 文档：`docs/modules/[module-name].md`

## 质量标准
- API 覆盖率 ≥ 80%
- 包含代码示例
```

---

**契约状态**: ✅ 完成
**最后更新**: 2025-01-03
