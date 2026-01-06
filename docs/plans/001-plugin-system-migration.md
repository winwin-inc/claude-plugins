---
created: 2025-01-06 10:00:00
session_id: calm-mapping-giraffe
status: completed
---

# Wiki Generator 插件系统改造计划

## 概述

将 repo-wiki 项目从 CLI 安装工具改造为 Claude Code 插件系统,支持通过 `/plugin marketplace add` 安装。

## 用户需求
- ✅ 创建完整的 marketplace (支持未来扩展多个插件)
- ✅ 移除 CLI 安装工具 (wiki-generator 命令)
- ✅ 插件名称: wiki-generator

## 设计方案

### 核心策略
采用**纯净插件模式**: 完全移除 Python 包和 CLI 工具,只保留 Claude Code 插件结构。

**理由**:
- 最大化简化项目结构
- 专注于插件系统,无历史包袱
- 更清晰的定位和更易维护

### 最终目录结构

```
repo-wiki/
├── .claude-plugin/              # 🆕 插件根目录
│   ├── marketplace.json         # 🆕 Marketplace 配置
│   ├── plugin.json              # 🆕 插件清单
│   ├── README.md                # 🆕 插件使用说明
│   ├── commands/                # 🆕 Wiki 命令
│   │   └── wiki-generate.md
│   └── templates/               # 🆕 文档模板 (可选)
└── README.md                    # 📝 更新为插件安装方式
```

### 完全移除
- ❌ `wiki_generator/` 目录 (包括所有 Python 代码)
- ❌ `pyproject.toml` (不再需要 Python 包配置)
- ❌ `tests/` (如果有)
- ❌ `.claude/` (SpeckKit 命令,如果不需要)

## 实施步骤

### 阶段 1: 创建插件目录结构

**任务**:
1. 创建 `.claude-plugin/` 目录
2. 从 `wiki_generator/.claude/commands/` 复制 `wiki-generate.md` 到 `.claude-plugin/commands/`
3. (可选) 复制 templates/ 目录到 `.claude-plugin/templates/`

**关键文件**:
- [wiki_generator/.claude/commands/wiki-generate.md](wiki_generator/.claude/commands/wiki-generate.md)

---

### 阶段 2: 创建插件配置文件

#### 2.1 创建 `.claude-plugin/marketplace.json`

```json
{
  "name": "claude-plugins",
  "version": "1.0.0",
  "description": "Claude Code 插件市场 - 包含 Wiki Generator 和其他插件",
  "owner": {
    "name": "Repo Wiki Generator Team",
    "url": "https://github.com/user/repo-wiki"
  },
  "plugins": [
    {
      "name": "wiki-generator",
      "source": "./",
      "description": "自动生成和维护项目 Wiki 文档的 Claude Code 插件",
      "version": "3.0.0",
      "author": {
        "name": "Repo Wiki Generator Team"
      }
    }
  ]
}
```

#### 2.2 创建 `.claude-plugin/plugin.json`

```json
{
  "name": "wiki-generator",
  "description": "自动生成和维护项目 Wiki 文档的 Claude Code 插件",
  "version": "3.0.0",
  "author": {
    "name": "Repo Wiki Generator Team"
  },
  "commands": ["./commands/wiki-generate.md"],
  "homepage": "https://github.com/user/repo-wiki",
  "repository": "https://github.com/user/repo-wiki"
}
```

---

### 阶段 3: 移除 Python 包和测试代码

**删除文件和目录**:
```bash
rm -rf wiki_generator/
rm -rf tests/
rm pyproject.toml
rm -rf .claude/  # 如果不需要 SpeckKit 命令
```

**保留文件**:
- `README.md` (将更新)
- `specs/` (如果有文档价值)
- `docs/` (除 PLUGIN-MIGRATION.md 外的其他文档)

---

### 阶段 4: 更新文档

#### 4.1 更新 [README.md](README.md)

**内容结构**:
```markdown
# Wiki Generator - Claude Code 插件

自动生成和维护项目 Wiki 文档的 Claude Code 插件。

## 快速开始

### 安装插件

\`\`\`bash
# 通过 Marketplace 安装
/plugin marketplace add https://github.com/user/repo-wiki

# 或本地安装
/plugin marketplace add /path/to/repo-wiki
\`\`\`

### 使用

\`\`\`bash
# 生成完整 Wiki
/wiki-generate --full

# 生成特定模块
/wiki-generate --module src/utils
\`\`\`

## 配置

在项目根目录创建 `wiki-config.json`:

\`\`\`json
{
  "output_dir": "docs",
  "exclude_patterns": ["node_modules", "dist"]
}
\`\`\`

## 功能特性

- 🚀 自动生成项目概览文档
- 📦 模块文档自动提取
- 🔧 技术栈识别
- 📊 API 文档生成
- 🎨 可定制模板

## 插件结构

\`\`\`
.claude-plugin/
├── marketplace.json
├── plugin.json
├── commands/
│   └── wiki-generate.md
└── templates/
\`\`\`
```

#### 4.2 创建 [.claude-plugin/README.md](.claude-plugin/README.md)

**内容**:
- 插件详细功能说明
- 所有命令和参数说明
- 配置文件完整选项
- 使用示例和最佳实践
- 故障排除指南

---

### 阶段 5: 测试验证

#### 5.1 插件功能测试

**测试清单**:
1. ✅ `/plugin marketplace add /path/to/repo-wiki` 成功加载
2. ✅ `/wiki-generate --full` 命令可用
3. ✅ 配置文件生成正确
4. ✅ 文档模板加载正常
5. ✅ 所有命令参数正常工作

#### 5.2 配置验证

**验证项目**:
- `marketplace.json` 格式正确
- `plugin.json` 路径引用正确
- 命令文件 frontmatter 格式正确
- 相对路径验证 (`./` 开头)

---

### 阶段 6: 发布

#### 6.1 Git 提交

```bash
git checkout -b refactor/plugin-system

# 添加新文件
git add .claude-plugin/
git add README.md

# 删除旧文件
git rm -r wiki_generator/
git rm -r tests/
git rm pyproject.toml
git rm -r .claude/  # 如果不需要

git commit -m "✨ refactor: 迁移到 Claude Code 插件系统

重大变更:
- 移除 Python CLI 工具和所有相关代码
- 创建标准 Claude Code 插件结构
- 支持 /plugin marketplace add 安装

Breaking Change:
- 不再支持 CLI 安装方式 (uvx wiki-generator)
- 请使用插件系统: /plugin marketplace add <url>
- 项目结构完全简化,不再包含 Python 包

新结构:
- .claude-plugin/ - 插件根目录
  ├── marketplace.json - Marketplace 配置
  ├── plugin.json - 插件清单
  ├── commands/ - Wiki 命令
  └── templates/ - 文档模板
"
```

#### 6.2 发布 Release

在 GitHub 创建 Release:
- **Tag**: `v3.0.0`
- **Title**: "Wiki Generator v3.0 - Claude Code 插件系统"
- **Release Notes**:
  ```markdown
  ## 🚀 重大更新: Claude Code 插件系统

  Wiki Generator 现在作为 Claude Code 插件提供!

  ✨ 新特性:
  - 通过 `/plugin marketplace add` 一键安装
  - 完全移除 Python CLI 工具
  - 更简洁的项目结构
  - 更好的 Claude Code 集成

  📦 安装方式:
  \`\`\`bash
  /plugin marketplace add https://github.com/user/repo-wiki
  \`\`\`

  ⚠️ Breaking Changes:
  - 不再支持 `uvx wiki-generator` CLI 安装
  - 项目不再包含 Python 包
  - 需要使用 Claude Code 插件系统

  📖 迁移指南: 查看 README.md
  ```

---

## 关键文件清单

### 需要创建的文件 ✨
1. `.claude-plugin/marketplace.json` - Marketplace 配置
2. `.claude-plugin/plugin.json` - 插件清单
3. `.claude-plugin/README.md` - 插件使用说明
4. `.claude-plugin/commands/wiki-generate.md` - 从 wiki_generator/.claude/commands/ 复制

### 需要修改的文件 📝
1. [README.md](README.md:1) - 完全重写为插件安装方式

### 需要删除的文件 ❌
1. `wiki_generator/` - 整个目录
2. `pyproject.toml` - Python 包配置
3. `tests/` - 测试代码 (如果有)
4. `.claude/` - SpeckKit 命令 (如果不需要)

---

## 预期成果

### 项目简化对比

**改造前**:
```
repo-wiki/
├── wiki_generator/          # Python 包 (500+ 行代码)
│   ├── __init__.py
│   ├── __main__.py
│   ├── installer.py
│   └── .claude/
├── pyproject.toml           # Python 包配置
├── tests/                   # 测试代码
└── .claude/                 # SpeckKit 命令
```

**改造后**:
```
repo-wiki/
├── .claude-plugin/          # 插件根目录
│   ├── marketplace.json
│   ├── plugin.json
│   ├── README.md
│   ├── commands/
│   │   └── wiki-generate.md
│   └── templates/
└── README.md
```

### 用户体验改进

**安装前 (v2.0)**:
```bash
# 需要 Python 环境
uvx wiki-generator
```

**安装后 (v3.0)**:
```bash
# 原生 Claude Code 集成
/plugin marketplace add https://github.com/user/repo-wiki
```

### 代码行数对比

| 类别 | v2.0 | v3.0 | 减少 |
|------|------|------|------|
| Python 代码 | ~500 行 | 0 行 | -100% |
| 配置文件 | pyproject.toml | plugin.json + marketplace.json | 更简洁 |
| 文档 | 混杂 | 集中在 README | 更清晰 |

---

## 风险和缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 现有用户无法升级 | 高 | 清晰的 Release notes + README 说明 |
| 插件配置错误 | 中 | 全面测试 + 格式验证 |
| 文档模板缺失 | 低 | 检查并迁移必要的 templates/ |

---

## 时间估算

- 阶段 1: 创建插件目录 (15 分钟)
- 阶段 2: 创建配置文件 (30 分钟)
- 阶段 3: 移除 Python 代码 (10 分钟)
- 阶段 4: 更新文档 (1 小时)
- 阶段 5: 测试验证 (1 小时)
- 阶段 6: 发布 (30 分钟)

**总计**: ~3 小时

---

## 后续优化 (v3.1+)

1. 添加更多模板到 templates/ 目录
2. 支持插件内嵌配置示例
3. 添加插件更新检测机制
4. 考虑添加其他相关插件到 marketplace
