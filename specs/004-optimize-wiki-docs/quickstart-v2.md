# 快速开始：优化 Wiki 文档结构和模板 v2.0

**版本**: 2.0.0
**创建日期**: 2025-01-04
**功能**: [spec.md](spec.md)

---

## ⚠️ 架构说明（v2.0）

**重要**: 本功能采用职责分离架构

- **Python 包** (`wiki-generator`): 提供安装、配置验证、迁移工具
- **Claude Code 命令** (`/wiki-generate`): 使用 AI 生成文档内容

**工作流程**:
1. 使用 `wiki-generator --init` 初始化项目
2. 使用 Claude Code `/wiki-generate` 命令生成文档

---

## 概述

本文档介绍如何使用优化后的 Wiki Generator 工具和模板。

**新特性**:
- ✅ 22 个高质量模板（中英各 11 个）
- ✅ 配置文件验证（JSON Schema）
- ✅ 一键初始化（`--init`）
- ✅ 配置迁移工具（`--migrate`）
- ✅ 统一的文档格式（`<cite>`、目录、Section sources）

---

## 前置要求

- Python 3.11+
- Claude Code（用于生成文档）
- 已安装 `wiki-generator` 工具

---

## 安装 Wiki Generator

### 方法 1：使用 uv（推荐）

```bash
uv tool install wiki-generator
```

### 方法 2：使用 pip

```bash
pip install wiki-generator
```

### 方法 3：开发模式

```bash
git clone https://github.com/your-org/repo-wiki.git
cd repo-wiki
pip install -e .
```

---

## 基础使用

### 1. 初始化项目

在你的项目根目录运行：

```bash
wiki-generator --init
```

**这将创建**:
- `.claude/wiki-config.json` - 配置文件
- `.claude/templates/` - 22 个模板文件（中英各 11 个）
- `.claude/commands/wiki-generate.md` - Claude Code 命令
- `.claude/schema/wiki-config-schema.json` - JSON Schema

**输出示例**:
```
✅ 成功安装到: /path/to/project/.claude
✅ 配置文件已创建: .claude/wiki-config.json
✅ 模板版本: 2.0.0

下一步:
1. 编辑 .claude/wiki-config.json 配置
2. 在 Claude Code 中运行 /wiki-generate 命令
3. 验证配置: wiki-generator --validate
```

### 2. 验证配置

```bash
wiki-generator --validate
```

**成功输出**:
```
✅ 配置文件验证通过
```

**失败输出**:
```
❌ 配置文件验证失败
  - 字段 'language': 必须是 'zh', 'en', 或 'both' 之一
```

### 3. 生成文档（使用 Claude Code）

在 Claude Code 中执行：

```
/wiki-generate
```

Claude Code 将：
1. 读取 `.claude/wiki-config.json` 配置
2. 分析项目代码库
3. 根据模板生成文档
4. 保存到配置的输出目录（默认 `docs/`）

---

## 配置文件详解

### 基本配置

创建 `.claude/wiki-config.json`：

```json
{
  "output_dir": "docs",
  "language": "zh",
  "structure_template": "reference",
  "include_sources": true,
  "generate_toc": true
}
```

**字段说明**:
- `output_dir`: 文档输出目录（默认: `"docs"`）
- `language`: 文档语言 - `"zh"`（中文）、`"en"`（英文）、`"both"`（双语）
- `structure_template`: 结构模板 - `"reference"`（参考项目）、`"simple"`（简化）、`"custom"`（自定义）
- `include_sources`: 是否包含 Section sources（默认: `true`）
- `generate_toc`: 是否生成目录索引（默认: `true`）

### 高级配置

```json
{
  "output_dir": "docs",
  "language": "both",
  "structure_template": "custom",
  "include_sources": true,
  "generate_toc": true,
  "sections": {
    "required": [
      "quickstart",
      "overview",
      "techstack"
    ],
    "optional": [
      "datamodel",
      "corefeatures"
    ]
  },
  "version": "2.0.0"
}
```

**sections 配置**:
- `required`: 必需生成的文档列表
- `optional`: 可选文档列表（Claude Code 根据项目特征决定）

---

## CLI 命令参考

### wiki-generator --init

初始化项目配置和模板

```bash
wiki-generator --init [OPTIONS]

选项:
  --force           强制覆盖已存在的 .claude/ 目录
  --no-validate     跳过配置验证
  --verbose         显示详细输出
```

### wiki-generator --validate

验证配置文件

```bash
wiki-generator --validate [OPTIONS]

选项:
  --config PATH     配置文件路径（默认: .claude/wiki-config.json）
```

### wiki-generator --migrate

迁移配置文件到最新版本

```bash
wiki-generator --migrate [OPTIONS]

选项:
  --backup/--no-backup  是否备份原文件（默认: --backup）
  --dry-run         显示将要执行的变更，但不实际修改
```

### wiki-generator --version

显示版本信息

```bash
wiki-generator --version
```

**输出示例**:
```
wiki-generator version 2.0.0
Template version: 2.0.0
Python 3.11.0
```

---

## 模板列表

### 中文模板（11 个）

| 模板 | 文件名 | 说明 |
|------|--------|------|
| 快速开始 | `quickstart.md.template` | 5 分钟入门指南 |
| 项目概述 | `overview.md.template` | 项目介绍和目标 |
| 技术栈与依赖 | `techstack.md.template` | 技术选型说明 |
| 系统架构 | `architecture.md.template` | 架构设计 |
| 数据模型 | `datamodel.md.template` | 数据结构 |
| 核心功能 | `corefeatures.md.template` | 核心业务逻辑 |
| 开发指南 | `development.md.template` | 开发环境设置 |
| 部署指南 | `deployment.md.template` | 部署流程 |
| 测试策略 | `testing.md.template` | 测试方法 |
| 故障排除 | `troubleshooting.md.template` | 常见问题 |
| 安全考虑 | `security.md.template` | 安全最佳实践 |

### 英文模板（11 个）

对应的英文模板位于 `templates/en/` 目录。

---

## 配置验证

### 验证时机

建议在以下情况验证配置：
1. 初始化后（`--init --validate`）
2. 手动编辑配置文件后
3. Claude Code 生成文档前

### 常见验证错误

#### 错误 1: 无效的语言值

```json
{
  "language": "chinese"  // ❌ 错误
}
```

**修正**:
```json
{
  "language": "zh"  // ✅ 正确
}
```

#### 错误 2: custom 模式缺少 sections

```json
{
  "structure_template": "custom"  // ❌ 缺少 sections
}
```

**修正**:
```json
{
  "structure_template": "custom",
  "sections": {
    "required": ["quickstart", "overview"]
  }  // ✅ 正确
}
```

---

## 迁移旧配置

### 从 v1.0 迁移到 v2.0

如果你使用的是旧版本配置：

```bash
# 1. 备份现有配置
cp .claude/wiki-config.json .claude/wiki-config.json.backup

# 2. 迁移配置
wiki-generator --migrate

# 3. 查看变更
cat .claude/migration-report.md

# 4. 验证新配置
wiki-generator --validate
```

**迁移报告示例**:
```
✅ 成功迁移到版本 2.0.0

变更:
  - 添加字段: language = zh
  - 重命名字段: lang -> language
  - 添加字段: structure_template = reference
  - 更新版本: 1.0 -> 2.0

备份: .claude/wiki-config.json.backup
```

---

## 与 Claude Code 集成

### wiki-generate 命令

`/wiki-generate` 命令由 Claude Code 执行，负责：

1. **读取配置**: 加载 `.claude/wiki-config.json`
2. **分析项目**: 扫描代码库，识别技术栈和结构
3. **选择模板**: 根据配置选择合适的模板
4. **生成内容**: 使用 AI 填充模板变量
5. **保存文档**: 写入配置的输出目录

### 模板变量

Claude Code 将填充以下变量：

- `{title}`: 文档标题
- `{cite_files}`: 引用文件列表
- `{toc}`: 目录索引
- `{section1_title}`, `{section1_content}`: 章节标题和内容
- `{section1_sources}`: 章节来源

---

## 故障排除

### 问题 1: 配置文件不存在

```bash
❌ 错误: 配置文件不存在: .claude/wiki-config.json
```

**解决方法**:
```bash
wiki-generator --init
```

### 问题 2: 模板文件缺失

```bash
❌ 错误: 找不到模板文件: templates/zh/quickstart.md.template
```

**解决方法**:
```bash
# 重新初始化
wiki-generator --init --force
```

### 问题 3: 配置验证失败

```bash
❌ 配置文件验证失败
  - 字段 'language': 必须是 'zh', 'en', 或 'both' 之一
```

**解决方法**:
根据错误消息修正配置文件，然后重新验证。

---

## 示例项目

### Python Web 项目

```bash
# 1. 初始化
cd my-project
wiki-generator --init

# 2. 配置（可选）
cat > .claude/wiki-config.json << EOF
{
  "language": "zh",
  "structure_template": "reference"
}
EOF

# 3. 验证配置
wiki-generator --validate

# 4. 生成文档（在 Claude Code 中）
# 执行: /wiki-generate

# 5. 查看结果
ls docs/zh/content/
```

### 双语项目

```bash
# 配置
cat > .claude/wiki-config.json << EOF
{
  "language": "both",
  "structure_template": "reference"
}
EOF

# 生成文档后
ls docs/zh/content/ docs/en/content/
```

---

## 性能目标

### Python 包性能

| 操作 | 目标时间 | 说明 |
|------|---------|------|
| 初始化（--init） | < 3 秒 | 复制 22 个模板文件 |
| 配置验证（--validate） | < 1 秒 | JSON Schema 验证 |
| 配置迁移（--migrate） | < 2 秒 | 应用迁移规则 |

### Claude Code 命令性能

| 操作 | 目标时间 | 说明 |
|------|---------|------|
| 小型项目 | < 15 秒 | < 100 文件，< 10K 行代码 |
| 中型项目 | < 30 秒 | 100-500 文件，10K-50K 行代码 |
| 大型项目 | < 90 秒 | > 500 文件，> 50K 行代码 |

---

## 下一步

- 📖 阅读 [spec.md](spec.md) 了解完整功能规范
- 🔧 查看 [plan.md](plan.md) 了解实施计划
- 📝 查看 [data-model.md](data-model-v2.md) 了解数据模型
- 🎯 自定义模板以满足项目需求

---

**版本**: 2.0.0
**最后更新**: 2025-01-04
**状态**: ✅ 就绪
