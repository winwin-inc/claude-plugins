# Repo Wiki Generator

> 通过 AI 自动生成和维护项目 Wiki 文档的 Claude Code 工具

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-8D75B7.svg)](https://github.com/astral-sh/ruff)

## 📖 简介

Repo Wiki Generator 是一个强大的 Claude Code 自定义命令工具，能够自动分析代码库并生成高质量的技术文档。

### ✨ 核心特性

- 🤖 **AI 驱动** - 利用 Claude AI 智能分析代码结构
- 📝 **自动文档生成** - 从代码自动生成 API 文档、模块文档
- 🔄 **增量更新** - 基于代码变更智能更新文档
- ✅ **质量验证** - 内置质量评分系统（目标 ≥80 分）
- 📊 **多格式导出** - 支持 PDF、HTML、DOCX 等格式
- 🎨 **架构图生成** - 自动生成 Mermaid 架构图
- 🌍 **多语言翻译** - 支持多语言文档翻译
- 🚀 **一键安装** - 快速集成到任何 Claude Code 项目

## 🎯 成功指标

- 减少 **70%** 的文档维护工作量
- 文档质量分数 ≥ **80 分**
- API 文档覆盖率 ≥ **85%**
- 模块文档覆盖率 ≥ **90%**
- 代码示例准确率 ≥ **95%**

## 📦 快速开始

### 安装

在你的项目目录中运行：

```bash
# 方式一：使用 uvx（推荐）
uvx wiki-generator

# 方式二：安装后使用
uv pip install -e .
wiki-generator
```

这会将 `.claude/` 目录（包含所有 wiki 命令和模板）复制到你的项目。

### 验证安装

安装完成后，在 Claude Code 中测试：

```
/wiki-overview
```

如果看到项目概览文档生成，说明安装成功！

## 🚀 使用指南

### 基本命令

安装后，你可以在 Claude Code 中使用以下命令：

| 命令 | 说明 |
|------|------|
| `/wiki-overview` | 生成项目概览文档 |
| `/wiki-module <模块名>` | 生成指定模块文档 |
| `/wiki-api <API路径>` | 生成 API 文档 |
| `/wiki-update` | 增量更新现有文档 |
| `/wiki-export --format pdf` | 导出文档为指定格式 |
| `/wiki-quality` | 检查文档质量 |

### 配置文件

在项目根目录创建 `.claude/wiki-config.json`：

```json
{
  "output_dir": "docs",
  "exclude_patterns": [
    "node_modules",
    "dist",
    ".git",
    "__pycache__"
  ],
  "template_dir": ".claude/templates",
  "quality_threshold": 80,
  "diagrams": {
    "enabled": true,
    "detail_level": "medium"
  }
}
```

### 示例工作流

```bash
# 1. 在你的项目中安装 wiki-generator
cd /path/to/your/project
uvx wiki-generator

# 2. 在 Claude Code 中生成完整文档
/wiki-overview
/wiki-module src/core
/wiki-module src/utils

# 3. 检查文档质量
/wiki-quality

# 4. 导出为 PDF
/wiki-export --format pdf
```

## 📁 项目结构

```
repo-wiki/
├── src/                          # 源代码
│   ├── cli.py                    # CLI 入口
│   ├── __main__.py               # 模块入口
│   ├── core/                     # 核心功能
│   │   ├── config_manager.py     # 配置管理
│   │   ├── file_handler.py       # 文件处理
│   │   ├── file_scanner.py       # 代码扫描
│   │   ├── source_parser.py      # 源码解析
│   │   └── ...
│   ├── models/                   # 数据模型
│   │   ├── config.py             # 配置模型
│   │   └── command.py            # 命令模型
│   └── utils/                    # 工具函数
│       ├── formatter.py          # 格式化输出
│       ├── validator.py          # 验证器
│       └── file_helper.py        # 文件助手
├── .claude/                      # Claude Code 命令和模板
│   ├── commands/                 # 自定义命令定义
│   │   ├── wiki-init.md
│   │   ├── wiki-overview.md
│   │   ├── wiki-module.md
│   │   └── ...
│   ├── templates/                # 文档模板
│   │   ├── overview.md.template
│   │   ├── module.md.template
│   │   └── ...
│   ├── BEST-PRACTICES.md         # 最佳实践
│   └── README.md                 # 命令文档
├── docs/                         # 生成的文档
├── specs/                        # 功能规范
│   ├── 001-wiki-generator-commands/
│   ├── 002-command-install/
│   └── 003-fix-package-structure/
├── pyproject.toml                # 项目配置
├── CLAUDE.md                     # Claude Code 指南
└── README-WIKI-GENERATOR.md      # Wiki Generator 详细文档
```

## 🔧 开发

### 环境设置

```bash
# 克隆仓库
git clone https://github.com/user/repo-wiki.git
cd repo-wiki

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装开发依赖
uv pip install -e ".[dev]"
```

### 代码质量

```bash
# 代码检查
ruff check src/

# 代码格式化
ruff format src/

# 一键修复
ruff check --fix src/
```

### 测试

```bash
# 运行测试
pytest

# 测试覆盖率
pytest --cov=src --cov-report=html
```

## 📋 配置选项

### wiki-config.json

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `output_dir` | string | `"docs"` | 文档输出目录 |
| `exclude_patterns` | array | `[]` | 排除的文件/目录模式 |
| `template_dir` | string | `".claude/templates"` | 模板目录 |
| `quality_threshold` | number | `80` | 质量阈值（0-100） |
| `diagrams.enabled` | boolean | `true` | 是否生成架构图 |
| `diagrams.detail_level` | string | `"medium"` | 图表详细程度（low/medium/high） |

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🔗 相关链接

- [Claude Code](https://claude.ai/code) - 官方 Claude Code 文档
- [Wiki 命令规范](specs/001-wiki-generator-commands/spec.md) - Wiki 命令设计规范
- [安装工具文档](README-WIKI-GENERATOR.md) - 安装工具详细说明
- [最佳实践](.claude/BEST-PRACTICES.md) - 文档生成最佳实践

## 🙏 致谢

- 感谢 Anthropic 团队提供 Claude Code
- 感谢所有贡献者的支持

---

**版本**: 1.0.0
**最后更新**: 2025-01-04
