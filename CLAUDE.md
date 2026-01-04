# Repo Wiki Generator - Claude Code 指南

本项目提供 Claude Code 自定义斜杠命令，用于自动生成和维护项目 Wiki 文档。

## ⚠️ 语言要求

**所有交互、注释、提交消息、文档必须使用简体中文。**

- 会话语言、代码注释、提交消息、文档内容：简体中文
- 变量和函数名：英文（编程惯例）
- 例外：技术术语（HTTP、API、SQL 等）可保留英文

## ⚠️ 文档生成策略

**本项目例外**：作为 Wiki 生成器，它为其他项目生成文档。

- **本项目自身**：代码优先，文档按需（不自动生成文档）
- **其他项目**：通过 `/wiki` 命令自动生成文档（核心功能）

## 项目概述

**目标**：通过 AI 分析代码库，自动生成高质量技术文档。

**核心能力**：
- 自动文档生成（从代码分析）
- 增量更新（基于代码变更）
- 质量验证和评分
- 多格式导出（PDF、HTML、DOCX）
- 架构图生成（Mermaid）
- 多语言翻译支持

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
