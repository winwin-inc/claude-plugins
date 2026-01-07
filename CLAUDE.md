# Repo Wiki Generator - Claude Code 指南

本项目提供 Claude Code 自定义斜杠命令，用于自动生成和维护项目 Wiki 文档。

## ⚠️ 关键规则

### 1. 语言要求
所有交互使用**简体中文**：
- 代码注释、文档、提交消息
- 错误消息、日志消息
- 变量名用英文，注释用中文

### 2. 文档策略
**只编写代码，不生成文档**（除非用户明确要求）。

## 快速开始

## 配置文件

### `{output_dir}/wiki-config.json`

配置文件位于 `output_dir` 指定的目录中（默认为 `docs/wiki-config.json`）。

首次运行 `/wiki-generate` 时，系统会提示您选择输出目录（默认为 `docs`），然后自动创建配置文件。

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

**重要**：
- 配置文件直接放在 `output_dir` 目录下，不使用 `.claude/` 子目录
- 使用 `WIKI_CONFIG` 环境变量可以指定自定义配置文件路径
- 配置路径解析由 `plugins/libs/config_resolver.sh` 统一管理

## 项目结构

```
claude-plugins/
├── CLAUDE.md                          # 项目指南文档（本文件）
├── README.md                          # 项目说明
└── plugins/                           # 核心插件目录
    ├── commands/                      # Claude Code 命令
    │   ├── commit.md                 # Git 提交命令
    │   ├── save-session.md            # 会话保存命令
    │   └── wiki-generate.md          # Wiki 生成命令（核心功能）
    ├── libs/                         # 核心库文件
    │   ├── config_resolver.sh        # 配置文件解析库
    │   └── metadata_tracker.sh       # 元数据追踪库
    ├── schemas/                      # 配置模式定义
    │   └── wiki-config-schema-v3.json # Wiki 配置模式 v3.1
    ├── scripts/                      # 脚本工具
    │   ├── add_region_markers.sh     # 区域标记添加脚本
    │   └── migrate-sessions.sh       # 会话迁移脚本
    ├── skills/                       # Claude Code 技能集
    │   └── doc-generator/            # 文档生成技能
    │       ├── change_detection.md   # 变更检测技能
    │       ├── content_extraction.md # 内容提取技能
    │       ├── content_generation.md # 内容生成技能
    │       ├── index_generation.md   # 索引生成技能
    │       ├── module_scanning.md    # 模块扫描技能
    │       ├── monorepo_detection.md # 单体仓库检测技能
    │       ├── outline_generation.md # 大纲生成技能
    │       ├── smart_merge.md        # 智能合并技能
    │       └── tech_stack_detection.md # 技术栈检测技能
    └── templates/                    # 文档模板
        └── wiki-generate/            # Wiki 生成模板
            ├── README.md             # 模板使用说明
            ├── TEMPLATE_FORMAT.md    # 模板格式说明
            ├── wiki-config.json.template # 配置文件模板
            ├── en/                   # 英文模板（12 个）
            │   ├── overview.md.template
            │   ├── quickstart.md.template
            │   ├── techstack.md.template
            │   ├── architecture.md.template
            │   ├── corefeatures.md.template
            │   ├── development.md.template
            │   ├── deployment.md.template
            │   ├── testing.md.template
            │   ├── troubleshooting.md.template
            │   ├── security.md.template
            │   ├── datamodel.md.template
            │   ├── api-reference.md.template
            │   └── api-endpoint.md.template
            └── zh/                   # 中文模板（12 个）
                ├── overview.md.template
                ├── quickstart.md.template
                ├── techstack.md.template
                ├── architecture.md.template
                ├── corefeatures.md.template
                ├── development.md.template
                ├── deployment.md.template
                ├── testing.md.template
                ├── troubleshooting.md.template
                ├── security.md.template
                ├── datamodel.md.template
                ├── api-reference.md.template
                └── api-endpoint.md.template
```

### 核心组件说明

#### 1. Wiki 生成命令
- **位置**: [plugins/commands/wiki-generate.md](plugins/commands/wiki-generate.md)
- **功能**: 定义完整的 Wiki 生成流程，支持增量更新和智能合并
- **特性**: 技术栈检测、Skill 协作机制、配置驱动

#### 2. 配置系统
- **配置模式**: [plugins/schemas/wiki-config-schema-v3.json](plugins/schemas/wiki-config-schema-v3.json)
  - 版本 3.1.0
  - 增量更新配置
  - 变更检测和智能合并
  - 元数据追踪
- **配置解析**: [plugins/libs/config_resolver.sh](plugins/libs/config_resolver.sh)
  - 统一管理配置文件路径
  - 支持配置文件初始化和迁移
  - 环境变量配置支持

#### 3. 模板系统
- **双语支持**: 中文 (`zh/`) 和英文 (`en/`)
- **12 个核心模板**:
  - 快速开始、项目概述、技术栈、系统架构
  - 核心功能、开发指南、部署指南、测试策略
  - 故障排除、安全考虑、数据模型、API 文档

#### 4. Skill 系统
- **位置**: [plugins/skills/doc-generator/](plugins/skills/doc-generator/)
- **9 个核心技能**:
  - 技术栈检测、模块扫描、内容提取、大纲生成
  - 内容生成、索引生成、变更检测、智能合并、单体仓库检测

## 相关文档

- [Wiki 生成命令](plugins/commands/wiki-generate.md) - 核心命令文档
- [模板格式说明](plugins/templates/wiki-generate/TEMPLATE_FORMAT.md) - 模板编写指南
- [配置模式定义](plugins/schemas/wiki-config-schema-v3.json) - 配置文件模式

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
