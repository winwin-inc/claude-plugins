# 快速开始：优化 Wiki 文档结构和模板

**版本**: 1.0.0
**创建日期**: 2025-01-04
**功能**: [spec.md](spec.md)

---

## 概述

本文档介绍如何使用优化后的 Wiki Generator 生成符合参考项目标准的文档结构。

**新特性**:
- ✅ 分层目录结构（按功能模块组织）
- ✅ 统一文档格式（引用、目录、Section sources）
- ✅ 完整文档类型（11 种模板）
- ✅ 中英文双语支持
- ✅ 自动交叉引用链接

---

## 前置要求

- Python 3.11+
- 已安装 `wiki-generator` 工具
- 项目使用 Git 版本控制

---

## 安装

### 方法 1：使用 uvx（推荐）

```bash
uvx wiki-generator
```

### 方法 2：全局安装

```bash
uv pip install wiki-generator
wiki-generator
```

### 方法 3：开发模式安装

```bash
git clone https://github.com/your-org/repo-wiki.git
cd repo-wiki
uv pip install -e .
```

---

## 基础使用

### 1. 初始化配置

在你的项目根目录运行：

```bash
wiki-generator --init
```

这将创建：
- `.claude/wiki-config.json` - 配置文件
- `.claude/templates/` - 模板目录（可自定义）

### 2. 配置文件示例

创建 `.claude/wiki-config.json`：

```json
{
  "output_dir": "docs",
  "language": "zh",
  "structure_template": "reference",
  "include_sources": true,
  "generate_toc": true,
  "sections": {
    "required": [
      "quickstart",
      "overview",
      "techstack",
      "architecture",
      "development",
      "deployment",
      "testing",
      "troubleshooting",
      "security"
    ],
    "optional": [
      "datamodel",
      "corefeatures"
    ]
  }
}
```

### 3. 生成文档

#### 完整生成（新项目推荐）

```bash
wiki-generator --full
```

这将：
1. 分析整个代码库
2. 检测项目类型和技术栈
3. 自动判断需要哪些条件文档
4. 生成完整的分层目录结构
5. 创建所有必需文档

#### 增量更新（保持结构）

```bash
wiki-generator --update
```

这将：
1. 识别变更的代码模块
2. 只更新受影响的文档
3. 保持目录结构不变
4. 完全覆盖修改的文档（不保留手动编辑）

---

## 配置选项详解

### 语言设置

```json
{
  "language": "zh"      // 只生成中文文档
  // "language": "en"   // 只生成英文文档
  // "language": "both" // 同时生成中英文文档
}
```

**生成的目录结构**:
- `language: "zh"` → `docs/zh/content/`
- `language: "en"` → `docs/en/content/`
- `language: "both"` → `docs/zh/content/` + `docs/en/content/`

### 结构模板

#### Reference 模板（默认）

```json
{
  "structure_template": "reference"
}
```

生成与参考项目一致的结构：
```
docs/
└── zh/
    └── content/
        ├── 00-快速开始.md
        ├── 01-项目概述.md
        ├── 02-技术栈与依赖.md
        ├── 03-系统架构设计.md
        ├── 04-数据模型/
        ├── 05-核心功能/
        ├── 10-开发指南.md
        ├── 11-部署指南.md
        ├── 12-测试策略.md
        ├── 13-故障排除.md
        └── 14-安全考虑.md
```

#### Simple 模板

```json
{
  "structure_template": "simple"
}
```

生成简化的扁平结构：
```
docs/
└── zh/
    └── content/
        ├── quickstart.md
        ├── overview.md
        ├── techstack.md
        └── ...
```

#### Custom 模板

```json
{
  "structure_template": "custom",
  "sections": {
    "required": ["quickstart", "overview"],
    "optional": ["datamodel"]
  }
}
```

完全自定义文档列表。

### 格式化选项

```json
{
  "formatting": {
    "code_block_syntax": true,   // 代码块语法高亮
    "line_numbers": true,        // 显示行号
    "section_sources": true      // 显示章节来源
  }
}
```

### 链接配置

```json
{
  "links": {
    "auto_generate": true,  // 自动生成交叉引用
    "validate": true        // 验证链接有效性
  }
}
```

---

## 文档类型说明

### 必需文档

| 文档 | 模板名 | 说明 |
|------|--------|------|
| 快速开始 | `quickstart.md.template` | 5 分钟入门指南 |
| 项目概述 | `overview.md.template` | 项目介绍和目标 |
| 技术栈与依赖 | `techstack.md.template` | 技术选型说明 |
| 系统架构 | `architecture.md.template` | 架构设计 |
| 开发指南 | `development.md.template` | 开发环境设置 |
| 部署指南 | `deployment.md.template` | 部署流程 |
| 测试策略 | `testing.md.template` | 测试方法 |
| 故障排除 | `troubleshooting.md.template` | 常见问题解决 |
| 安全考虑 | `security.md.template` | 安全最佳实践 |

### 条件文档

| 文档 | 模板名 | 触发条件 |
|------|--------|----------|
| 数据模型 | `datamodel.md.template` | 检测到 ORM（SQLAlchemy, Django ORM） |
| 核心功能 | `corefeatures.md.template` | 检测到核心业务逻辑模块 |

**自动检测逻辑**:
- 关键词匹配: 1 分
- Import 语句: 2 分
- 文件名匹配: 3 分
- 阈值: ≥ 1 分

---

## 高级用法

### 自定义模板

1. 复制默认模板：
```bash
cp -r wiki_generator/.claude/templates .claude/
```

2. 编辑模板文件：
```bash
.claude/templates/zh/quickstart.md.template
```

3. 模板变量：
```markdown
# {title}

<cite>
**本文档中引用的文件**
{cite_files}
</cite>

## 目录
{toc}

## {section1_title}
{section1_content}

**Section sources**
{section1_sources}
```

### 性能优化

对于大型项目，调整批处理配置：

```json
{
  "performance": {
    "batch_size": 100,          // 增加批处理大小
    "cache_templates": true,    // 启用模板缓存
    "max_workers": 1            // 单线程（稳定性优先）
  }
}
```

### 排除文件

在项目根目录创建 `.wikiignore`：

```
node_modules/
dist/
.git/
*.test.js
*.spec.py
```

---

## 文档覆盖策略

**重要**: 新版本采用**完全覆盖**策略（参考 [spec.md](spec.md) 澄清 Q2）

### 行为说明

- `--full` 或 `--update` 会完全覆盖已存在的文档
- 不保留任何手动编辑
- 适用于完全由 AI 生成的文档场景

### 如需保留手动编辑

**方法 1**: 使用 Git 分支
```bash
git checkout -b docs-manual
# 手动编辑文档
git commit -m "手动编辑文档"

# 更新时
git checkout main
wiki-generator --update

# 合并手动编辑
git merge docs-manual
```

**方法 2**: 复制备份
```bash
cp -r docs docs-manual-backup
wiki-generator --update
# 手动合并 docs-manual-backup 的更改
```

---

## 示例项目

### Python Web 项目

```bash
# 项目结构
my-project/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   └── api/
├── tests/
├── pyproject.toml
└── README.md

# 生成文档
cd my-project
wiki-generator --full

# 输出
✅ 分析项目: Python Web 项目（FastAPI + SQLAlchemy）
✅ 检测到条件文档: datamodel, api
✅ 生成文档结构: docs/zh/content/
✅ 创建 15 个文档（用时 12.3 秒）
```

### Node.js 项目

```bash
# 项目结构
my-nodejs-app/
├── src/
├── package.json
└── README.md

# 生成文档
cd my-nodejs-app
wiki-generator --full

# 输出
✅ 分析项目: Node.js 项目（Express + MongoDB）
✅ 检测到条件文档: api
✅ 生成文档结构: docs/en/content/
✅ 创建 12 个文档（用时 10.5 秒）
```

---

## 故障排除

### 问题 1: 配置文件无效

```bash
❌ 错误: CONFIG_INVALID
配置文件 .claude/wiki-config.json 不符合 schema
```

**解决方法**:
```bash
# 验证配置
wiki-generator --validate-config

# 查看详细错误
wiki-generator --validate-config --verbose
```

### 问题 2: 模板文件缺失

```bash
❌ 错误: TEMPLATE_NOT_FOUND
找不到模板文件: quickstart.md.template
```

**解决方法**:
```bash
# 重新初始化
wiki-generator --init --force

# 或手动复制模板
cp -r wiki_generator/.claude/templates .claude/
```

### 问题 3: 生成的文档为空

**可能原因**:
- 项目被 `.wikiignore` 排除
- 文件数少于阈值

**解决方法**:
```bash
# 检查排除规则
cat .wikiignore

# 强制生成（跳过检测）
wiki-generator --full --force
```

---

## 迁移指南

### 从旧版本迁移

如果你使用的是旧版 Wiki Generator：

1. **备份现有文档**:
```bash
cp -r docs docs-old-backup
```

2. **更新配置文件**:
```bash
# 使用迁移工具
wiki-generator --migrate-config

# 或手动迁移（参考 MIGRATION.md）
```

3. **生成新文档**:
```bash
wiki-generator --full
```

4. **对比差异**:
```bash
diff -r docs-old-backup docs
```

---

## 性能基准

基于 [spec.md](spec.md) 第 5.1 节的性能目标：

| 项目规模 | 文件数 | 代码行数 | 目标时间 |
|---------|--------|---------|---------|
| 小型 | < 100 | < 10K | < 15 秒 |
| 中型 | 100-500 | 10K-50K | < 30 秒 |
| 大型 | > 500 | > 50K | < 90 秒 |

查看你的项目性能：
```bash
wiki-generator --full --profile
```

输出示例：
```
性能报告:
- 项目规模: 中型（230 个文件，25K 行代码）
- 执行时间: 18.3 秒
- 平均速度: 12.6 文件/秒
- ✅ 符合性能目标（< 30 秒）
```

---

## 下一步

- 📖 阅读完整 [spec.md](spec.md) 了解功能详情
- 🔧 自定义模板（参考 [API Contracts](contracts/api-contracts.md)）
- 🎯 查看最佳实践（参考 `.claude/BEST-PRACTICES.md`）
- 🐛 报告问题或贡献代码

---

**版本**: 1.0.0
**最后更新**: 2025-01-04
**状态**: 就绪
