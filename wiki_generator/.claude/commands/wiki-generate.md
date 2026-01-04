---
description: Wiki 文档生成器 - 通过参数控制生成行为
argument-hint: [--full | --update | --module=<path> | --validate | --translate=<lang>]
allowed-tools: all
---

# Wiki 文档生成命令

## 任务描述

根据传入的参数自动分析代码库并生成、更新或验证项目 Wiki 文档。这是一个统一的命令入口，通过不同的参数控制具体行为。

## 参数说明

- `--full`: 完整生成所有文档（包括初始化、概览、架构、所有模块、API、开发指南、索引）
- `--update`: 增量更新文档（基于 Git 提交分析，智能检测并保护手动编辑内容）
- `--module=<path>`: 为指定模块生成文档
- `--validate`: 验证文档质量并生成报告
- `--translate=<lang>`: 翻译文档到其他语言

## 执行步骤

### 1. 参数解析和验证

首先解析 `$ARGUMENTS` 以确定用户意图：

```bash
# 检测参数类型
PARAMS="$ARGUMENTS"

# 确定操作模式
if echo "$PARAMS" | grep -q -- "--full"; then
    MODE="full"
elif echo "$PARAMS" | grep -q -- "--update"; then
    MODE="update"
elif echo "$PARAMS" | grep -q -- "--module="; then
    MODE="module"
    MODULE_PATH=$(echo "$PARAMS" | grep -o -- "--module=[^ ]*" | cut -d'=' -f2)
elif echo "$PARAMS" | grep -q -- "--validate"; then
    MODE="validate"
elif echo "$PARAMS" | grep -q -- "--translate="; then
    MODE="translate"
    TARGET_LANG=$(echo "$PARAMS" | grep -o -- "--translate=[^ ]*" | cut -d'=' -f2)
else
    echo "❌ 错误：未指定参数。请使用 --full, --update, --module=<path>, --validate 或 --translate=<lang>"
    exit 1
fi
```

### 2. 配置管理

读取或生成配置文件：

```bash
CONFIG_FILE=".claude/wiki-config.json"

# 检查配置文件是否存在
if [ ! -f "$CONFIG_FILE" ]; then
    echo "📝 配置文件不存在，生成默认配置..."
    cp .claude/templates/wiki-config.json.template "$CONFIG_FILE"
fi
```

### 3. 根据模式执行

#### 模式 A: `--full` 完整生成

**阶段 1: 初始化**
- 创建 `docs/` 目录结构
- 创建 `docs/modules/`, `docs/api/`, `docs/diagrams/` 子目录

**阶段 2: 项目分析**
- 扫描项目根目录文件（README, package.json, requirements.txt 等）
- 识别项目类型（Node.js/Python/Java/Go/Ruby）
- 分析技术栈和框架
- 识别所有模块和组件

**阶段 3: 文档生成**
- 生成项目概览（`docs/00-Overview.md`）
- 生成架构文档（`docs/01-Architecture.md`）
- 生成所有模块文档（`docs/modules/*.md`）
- 生成 API 文档（`docs/api/ENDPOINTS.md`）
- 生成开发指南（`docs/02-Development.md`）
- 生成导航索引（`docs/README.md`）

**阶段 4: 优化**
- 生成 Mermaid 图表
- 自动运行质量验证

#### 模式 B: `--update` 智能增量更新

**变更检测**
- 分析最近 5 次 Git 提交
- 识别修改、新增、删除的文件
- 映射到受影响的模块

**智能更新（核心特性）**
- 使用 Git diff 比较当前文档与上次 AI 生成版本
- 按章节（Markdown 标题）进行对比
- **识别并跳过手动编辑的章节**
- **更新未修改的章节以同步代码变化**
- 100% 保证不丢失手动编辑内容

**变更报告**
- 生成 `docs/CHANGELOG.md` 追加
- 列出跳过的章节（手动编辑保护）
- 列出更新的章节（代码变化同步）

#### 模式 C: `--module=<path>` 单模块生成

**验证**
- 检查路径是否存在

**模块分析**
- 扫描指定目录的代码文件
- 提取导出函数、类、接口
- 识别模块职责和功能
- 分析 import/require 依赖

**文档生成**
- 生成 `docs/modules/<module-name>.md`
- 包含：概述、API 列表、依赖关系图、使用示例

#### 模式 D: `--validate` 质量验证

**结构检查**
- 文档完整性验证
- 标题层级结构检查
- 内部链接有效性验证

**内容检查**
- 代码示例准确性
- Mermaid 图表语法验证

**质量评分**
- 规则引擎评分（60%）：结构、链接、代码示例
- AI 评分（40%）：内容质量、可读性、专业性
- 总分范围：0-100

**生成报告**
- 优点列表
- 问题列表
- 改进建议

#### 模式 E: `--translate=<lang>` 多语言翻译

**语言检测**
- 识别源文档语言
- 验证目标语言支持

**智能翻译**
- 翻译所有文档
- **保持代码示例不翻译**
- **保持技术术语不翻译**（HTTP, API, SQL 等）
- 保持 Mermaid 图表代码不翻译

**目录组织**
- 创建 `docs/<lang>/` 目录
- 保持与原文档相同的文件结构

### 4. 错误处理

常见错误场景：

**错误 1: 目录不存在**
```bash
/wiki-generate --module=src/auth
# ❌ 错误：模块路径 src/auth 不存在
# 💡 建议：检查路径或使用 --full 初始化
```

**错误 2: 不是 Git 仓库**
```bash
/wiki-generate --update
# ❌ 错误：当前目录不是 Git 仓库
# 💡 建议：--update 需要 Git 仓库，使用 --full 生成完整文档
```

**错误 3: 配置文件损坏**
```bash
# ❌ 错误：.claude/wiki-config.json 格式错误
# 💡 建议：备份旧配置，重新生成默认配置
```

## 输出

### 成功输出
```
✅ 命令成功：[操作描述]
📄 生成文件：[文件路径]
⏱️ 耗时：[时间]
📊 质量分数：[分数]/100
```

### 错误输出
```
❌ 命令失败：[错误描述]

💡 建议：
- [建议 1]
- [建议 2]

🔗 帮助：使用 --help 查看参数说明
```

## 质量标准

### 文档质量
- 质量分数 ≥ 80
- 代码示例可运行
- Mermaid 图表语法正确
- 内部链接有效

### 性能目标
- `--full`：< 5 分钟（100 个模块）
- `--module=<path>`：< 10 秒（单模块）
- `--update`：< 2 分钟（增量）
- `--validate`：< 30 秒（全部文档）
- `--translate=<lang>`：< 3 分钟（全部文档）

### 用户体验
- 所有交互使用简体中文
- 错误消息友好具体
- 提供明确的建议和解决方案

## 参数组合使用

支持参数组合以实现复杂工作流：

```bash
# 生成并验证
/wiki-generate --full --validate

# 更新并翻译
/wiki-generate --update --translate=en

# 生成模块并验证
/wiki-generate --module=src/auth --validate
```

参数按顺序执行，后续参数可以使用前者的结果。

## 注意事项

1. **代码优先原则**：本项目专注于命令实现，不为自身生成文档（除非用户明确要求）
2. **中文优先**：所有用户交互使用简体中文
3. **手动编辑保护**：`--update` 模式通过 Git diff 智能检测并保护手动编辑内容
4. **增量更新优先**：推荐使用 `--update` 而非重新生成，以保留手动改进

## 示例使用

```bash
# 新项目完整初始化
/wiki-generate --full

# 代码修改后更新文档
/wiki-generate --update

# 为新模块生成文档
/wiki-generate --module=src/payment

# 发布前验证质量
/wiki-generate --validate

# 为国际团队翻译文档
/wiki-generate --translate=en

# 组合使用：生成并验证
/wiki-generate --full --validate
```

---

**版本**: 1.0.0
**最后更新**: 2025-01-03
**项目宪章**: 遵循所有 8 条核心原则
