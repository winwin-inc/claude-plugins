# Repo Wiki Generator

> 通过 AI 自动生成和维护项目 Wiki 文档的 Claude Code 工具（v2.0）

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-8D75B7.svg)](https://github.com/astral-sh/ruff)

## 📖 简介

Repo Wiki Generator v2.0 是一个强大的 Claude Code 自定义命令工具，能够自动分析代码库并生成高质量的技术文档。

### ✨ v2.0 核心特性

- 🎯 **配置驱动** - 通过 `.claude/wiki-config.json` 灵活控制生成行为
- 🔍 **技术栈显式检测** - 基于检测到的框架/库生成条件文档（SQLAlchemy、FastAPI 等）
- 🇨🇳 **中文优先** - 支持中文文件名和模板，完整的中文本地化
- 📂 **分层目录结构** - 按功能模块组织文档，参考项目标准
- ✅ **完全覆盖策略** - 每次重新生成整个文档，通过 Git 管理版本
- 🛡️ **部分成功机制** - 保留成功生成的文档，跳过失败的
- ✅ **质量验证** - 基础自动化验证（`<cite>` 块、目录、Section sources）
- 🚀 **一键安装** - 快速集成到任何 Claude Code 项目

### 🎯 成功指标

- 减少 **70%** 的文档维护工作量
- 文档质量分数 ≥ **80 分**
- API 文档覆盖率 ≥ **85%**
- 模块文档覆盖率 ≥ **90%**
- 代码示例准确率 ≥ **95%**

## 🆚 v1.0 vs v2.0

| 特性 | v1.0 | v2.0 |
|------|------|------|
| 配置方式 | AI 推测 | 配置驱动 |
| 文件命名 | 英文 | 中文文件名 |
| 目录结构 | 扁平 | 分层（按功能模块） |
| 更新策略 | 增量更新 | 完全覆盖 |
| 技术栈检测 | AI 自动检测 | 显式检测规则 |
| 错误处理 | 全部回滚 | 部分成功 |
| 质量验证 | AI 评分 | 基础自动化验证 |

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

这会将 `.claude/` 目录（包含所有 wiki 命令、模板和配置）复制到你的项目。

### 初始化配置

```bash
# 初始化项目配置和模板
wiki-generator --init

# 验证配置文件
wiki-generator --validate
```

### 生成文档

在 Claude Code 中运行：

```
/wiki-generate --full
```

## 🚀 使用指南

### Python CLI 命令

| 命令 | 说明 |
|------|------|
| `wiki-generator --init` | 初始化项目配置和模板 |
| `wiki-generator --validate` | 验证配置文件 |
| `wiki-generator --migrate` | 迁移旧配置到 v2.0 |
| `wiki-generator --version` | 显示版本信息 |

### Claude Code 命令

| 命令 | 说明 |
|------|------|
| `/wiki-generate --full` | 完整生成所有文档 |

### 配置文件

`.claude/wiki-config.json` 配置示例：

```json
{
  "output_dir": "docs",
  "language": "zh",
  "structure_template": "reference",
  "include_sources": true,
  "generate_toc": true
}
```

**配置选项**：

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `output_dir` | string | `"docs"` | 文档输出目录 |
| `language` | string | `"zh"` | 文档语言（`"zh"`/`"en"`/`"both"`） |
| `structure_template` | string | `"reference"` | 结构模板（`"reference"`/`"simple"`/`"custom"`） |
| `include_sources` | boolean | `true` | 是否包含源文件引用 |
| `generate_toc` | boolean | `true` | 是否生成目录索引 |

### 技术栈检测规则

v2.0 采用显式检测规则：

| 检测规则 | 触发条件 | 生成文档 |
|---------|---------|---------|
| SQLAlchemy | `from sqlalchemy` 或 `import sqlalchemy` | 数据模型/数据模型.md |
| Django ORM | `from django.db` | 数据模型/数据模型.md |
| FastAPI | `from fastapi` 或 `import fastapi` | API 文档/API 接口.md |
| Flask | `from flask` | API 文档/API 接口.md |
| Celery | `from celery` 或 `import celery` | 任务队列/任务队列.md |
| pytest | `import pytest` | 测试策略.md |
| Dockerfile | 文件存在 | 部署指南.md |

## 📁 项目结构

```
repo-wiki/
├── wiki_generator/              # 源代码包（v2.0）
│   ├── __init__.py
│   ├── cli_v2.py                # CLI 入口（v2.0）
│   ├── .claude/                 # Claude Code 命令和模板
│   │   ├── commands/            # 自定义命令定义
│   │   │   └── wiki-generate.md # Wiki 文档生成命令（v2.0）
│   │   ├── templates/           # 文档模板
│   │   │   ├── zh/              # 中文模板（11 个）
│   │   │   │   ├── quickstart.md.template
│   │   │   │   ├── overview.md.template
│   │   │   │   └── ...
│   │   │   └── en/              # 英文模板（11 个）
│   │   │       ├── quickstart.md.template
│   │   │       └── ...
│   │   ├── schema/              # JSON Schema
│   │   │   └── wiki-config-schema-v2.json
│   │   └── README.md            # 命令文档
│   ├── core/                    # 核心功能
│   │   ├── config_validator.py  # 配置验证器
│   │   ├── installer_v2.py      # 文件安装器（v2.0）
│   │   ├── migrator.py          # 配置迁移器
│   │   ├── migrations.py        # 迁移规则
│   │   ├── config_initializer.py # 配置初始化
│   │   ├── template_manifest.py # 模板清单
│   │   └── errors.py            # 统一错误处理
│   ├── models/                  # 数据模型
│   │   └── config_models.py     # 配置数据模型
│   └── utils/                   # 工具函数
│       ├── file_utils.py        # 文件工具
│       └── logger.py            # 日志模块
├── tests/test_v2/               # v2.0 测试套件
│   ├── test_config_validator.py # 配置验证测试
│   ├── test_migrator.py         # 迁移工具测试
│   ├── test_installer.py        # 文件安装测试
│   └── README.md                # 测试指南
├── specs/                       # 功能规范
│   └── 004-optimize-wiki-docs/  # v2.0 规范
├── pyproject.toml               # 项目配置
├── CLAUDE.md                    # Claude Code 指南
└── README.md                    # 本文件
```

## 📂 生成的文档结构

v2.0 采用分层目录结构：

```
docs/
└── zh/                          # 语言目录
    └── content/                 # 内容目录
        ├── 00-快速开始.md        # 必需文档（10 个）
        ├── 01-项目概述.md
        ├── 02-技术栈与依赖.md
        ├── 03-系统架构设计.md
        ├── 数据模型/             # 条件文档（检测到 SQLAlchemy）
        │   └── 数据模型.md
        ├── API 文档/             # 条件文档（检测到 FastAPI）
        │   └── API 接口.md
        ├── 04-核心功能.md
        ├── 05-开发指南.md
        ├── 06-部署指南.md
        ├── 07-测试策略.md
        ├── 08-故障排除.md
        └── 09-安全考虑.md
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
ruff check wiki_generator/

# 代码格式化
ruff format wiki_generator/

# 一键修复
ruff check --fix wiki_generator/
```

### 测试

```bash
# 运行所有测试
pytest tests/test_v2/

# 测试覆盖率
pytest tests/test_v2/ --cov=wiki_generator --cov-report=html

# 运行特定测试
pytest tests/test_v2/test_config_validator.py -v
```

## 🔄 从 v1.0 迁移

如果你有 v1.0 配置，需要迁移到 v2.0：

```bash
# 备份当前配置
cp .claude/wiki-config.json .claude/wiki-config.json.backup

# 迁移配置
wiki-generator --migrate

# 验证迁移结果
wiki-generator --validate
```

**主要变更**：
- `lang` → `language`
- 新增 `output_dir`、`structure_template`、`include_sources`、`generate_toc`
- 新增 `version` 字段

详细迁移指南：[MIGRATION.md](MIGRATION.md)

## 📋 文档模板

v2.0 提供 22 个高质量模板（中英各 11 个）：

### 必需文档（10 个）

1. 快速开始（quickstart.md.template）
2. 项目概述（overview.md.template）
3. 技术栈与依赖（techstack.md.template）
4. 系统架构设计（architecture.md.template）
5. 核心功能（corefeatures.md.template）
6. 开发指南（development.md.template）
7. 部署指南（deployment.md.template）
8. 测试策略（testing.md.template）
9. 故障排除（troubleshooting.md.template）
10. 安全考虑（security.md.template）

### 条件文档（根据技术栈生成）

- 数据模型（datamodel.md.template）- 检测到 SQLAlchemy/Django ORM
- API 接口（api.md.template）- 检测到 FastAPI/Flask
- 任务队列（taskqueue.md.template）- 检测到 Celery/RQ

## 🤝 贡献

欢迎贡献！请查看 [CLAUDE.md](CLAUDE.md) 了解开发指南。

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🔗 相关链接

- [Claude Code](https://claude.ai/code) - 官方 Claude Code 文档
- [v2.0 规范](specs/004-optimize-wiki-docs/spec.md) - 功能规范文档
- [迁移指南](MIGRATION.md) - v1.0 → v2.0 迁移指南
- [测试指南](tests/test_v2/README.md) - 测试文档
- [项目宪章](.specify/memory/constitution.md) - 项目治理原则

## 🙏 致谢

- 感谢 Anthropic 团队提供 Claude Code
- 感谢所有贡献者的支持

---

**版本**: 2.0.0
**最后更新**: 2025-01-04
