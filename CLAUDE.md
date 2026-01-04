# Repo Wiki Generator - Claude Code 指南

本项目提供 Claude Code 自定义斜杠命令，用于自动生成和维护项目 Wiki 文档。

## ⚠️ 关键规则

### 1. Python 依赖管理
使用 `uv` 管理依赖：
- ✅ `uv run pytest` / `uv run python ...`
- ✅ `uv sync` 同步依赖
- ❌ 不要直接使用 `python` 或 `pytest` 命令

### 2. 语言要求
所有交互使用**简体中文**：
- 代码注释、文档、提交消息
- 错误消息、日志消息
- 变量名用英文，注释用中文

### 3. 文档策略
**只编写代码，不生成文档**（除非用户明确要求）。

## 快速开始

### 安装 Wiki 命令

```bash
# 在你的项目目录中运行
uvx wiki-generator

# 或安装后直接使用
uv pip install -e .
wiki-generator
```

这会将 `.claude/` 目录（包含所有 wiki 命令和模板）复制到你的项目。


## 配置文件

### `.claude/wiki-config.json`

```json
{
  "output_dir": "docs",
  "exclude_patterns": ["node_modules", "dist", ".git"],
  "template_dir": ".claude/templates",
  "quality_threshold": 80,
  "diagrams": {
    "enabled": true,
    "detail_level": "medium"
  }
}
```

## 项目结构

```
repo-wiki/
├── cli.py                       # Wiki Generator 安装工具
├── .claude/                     # Wiki 命令和模板
│   ├── commands/                # Claude Code 自定义命令
│   │   ├── wiki-init.md
│   │   ├── wiki-overview.md
│   │   ├── wiki-module.md
│   │   └── ...
│   ├── templates/               # 文档模板
│   │   ├── overview.md.template
│   │   ├── module.md.template
│   │   └── ...
│   ├── backups/                 # 备份目录
│   ├── BEST-PRACTICES.md        # 最佳实践
│   └── README.md                # Wiki 文档说明
├── core/                        # 核心功能模块
├── utils/                       # 工具模块
├── models/                      # 数据模型
├── pyproject.toml               # 项目配置
├── specs/                       # 功能规范
│   ├── 001-wiki-generator-commands/  # Wiki 命令规范
│   ├── 002-command-install/         # 安装工具规范
│   └── 003-fix-package-structure/   # 包结构修复规范
└── README-WIKI-GENERATOR.md     # Wiki Generator 文档
```

## 相关文档

- [Wiki 命令规范](specs/001-wiki-generator-commands/spec.md)
- [安装工具文档](README-WIKI-GENERATOR.md)
- [项目最佳实践](.claude/BEST-PRACTICES.md)

## 成功指标

- 减少 70% 的文档维护工作量
- 文档质量分数 ≥ 80 分
- API 文档覆盖率 ≥ 85%
- 模块文档覆盖率 ≥ 90%
- 代码示例准确率 ≥ 95%

---

**版本**: 1.0.0
**最后更新**: 2025-01-04

## Active Technologies
- Python 3.11+ (Shell/Bash 脚本为核心，Python 作为辅助工具) (005-auto-doc-outline)
- 文件系统 (Markdown 文档生成到 `docs/` 或 `zh/content/`) (005-auto-doc-outline)
- Shell/Bash (核心) + Python 3.11+ (辅助片段) (005-auto-doc-outline)

## Recent Changes
- 005-auto-doc-outline: Added Python 3.11+ (Shell/Bash 脚本为核心，Python 作为辅助工具)
