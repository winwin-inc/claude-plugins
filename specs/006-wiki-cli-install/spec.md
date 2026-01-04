# Feature Specification: Wiki Generator CLI 安装工具优化

**Feature Branch**: `006-wiki-cli-install`
**Created**: 2026-01-04
**Status**: Draft
**Input**: User description: "优化 python 代码，只保留核心功能：自动安装 Claude Code 自定义命令及其相关模板文件到用户的项目中，通过 `uvx wiki-generator` 命令调用，将 .claude 目录下功能文件安装到当前目录，初始化 wiki-config.json"

---

## Executive Summary

优化现有 Wiki Generator CLI 安装工具（cli.py），保留核心安装功能，移除不必要的复杂性。用户通过 `uvx wiki-generator` 命令即可一键将 Claude Code 自定义命令和模板文件安装到当前项目目录，并自动初始化配置文件。

## Clarifications

### Session 2026-01-04 (Initial)

- Q: wiki-config.json 应该包含哪些配置字段？每个字段的默认值是什么？ → A: 包含 5 个核心字段：output_dir（默认: "docs"）、exclude_patterns（默认: ["node_modules", "dist", ".git"]）、quality_threshold（默认: 80）、diagrams_enabled（默认: true）、diagrams_detail_level（默认: "medium"）

### Session 2026-01-04 (Code Cleanup)

- Q: 需要保留哪些 Python 文件？删除哪些无效代码？ → A: 只保留 4 个核心文件（`__init__.py`, `__main__.py`, `installer.py`, `config.py`），删除所有旧代码（`cli.py`, `cli_v2.py`, `core/`, `models/`, `utils/` 目录）

---

## User Scenarios & Testing

### User Story 1 - 一键安装 Claude Code Wiki 命令 (Priority: P1)

开发者想要在自己的项目中使用 Claude Code 的 Wiki 文档生成功能，通过单个命令 `uvx wiki-generator` 即可将所有必需的自定义命令、模板和配置文件安装到项目根目录。

**Why this priority**: 这是核心使用场景，是用户使用工具的入口点。没有这个功能，用户无法使用任何 Wiki 生成命令。

**Independent Test**: 可以在空目录中完全测试 - 运行命令后验证 `.claude/` 目录和 `wiki-config.json` 文件是否正确创建。

**Acceptance Scenarios**:

1. **Given** 用户在一个空的项目目录中，**When** 运行 `uvx wiki-generator`，**Then** 应该在当前目录创建 `.claude/` 目录，包含所有必需的命令和模板文件
2. **Given** 项目目录已存在某些 `.claude/` 文件，**When** 运行安装命令，**Then** 应该提示用户是否覆盖现有文件（默认跳过已存在文件）
3. **Given** 安装成功完成，**When** 检查项目根目录，**Then** 应该存在 `wiki-config.json` 配置文件，包含默认配置

---

### User Story 2 - 配置文件自动初始化 (Priority: P2)

用户在安装过程中，系统自动生成 `wiki-config.json` 配置文件，包含合理的默认值，用户可以根据需要修改配置。

**Why this priority**: 配置文件是后续 Wiki 生成功能的基础，但没有配置文件时，工具应该能够使用内置默认值工作。

**Independent Test**: 安装后检查 `wiki-config.json` 文件是否存在并包含有效的 JSON 配置。

**Acceptance Scenarios**:

1. **Given** 用户首次运行安装命令，**When** 安装过程完成，**Then** 应该生成 `wiki-config.json` 包含 5 个默认字段（output_dir: "docs"、exclude_patterns: ["node_modules", "dist", ".git"]、quality_threshold: 80、diagrams_enabled: true、diagrams_detail_level: "medium"）
2. **Given** `wiki-config.json` 已存在，**When** 用户再次运行安装，**Then** 应该保留现有配置不覆盖
3. **Given** 配置文件生成，**When** 用户查看配置内容，**Then** 应该包含清晰的中文注释说明每个配置项的用途

---

### User Story 3 - 轻量级安装体验 (Priority: P3)

用户期望安装过程快速、简洁，不下载不必要的依赖，不创建冗余文件。

**Why this priority**: 提升用户体验，减少安装时间和磁盘占用。

**Independent Test**: 测量安装命令的执行时间和生成的文件数量。

**Acceptance Scenarios**:

1. **Given** 用户运行 `uvx wiki-generator`，**When** 安装过程执行，**Then** 应该在 5 秒内完成（不包括网络下载时间）
2. **Given** 安装完成，**When** 检查生成的文件，**Then** 应该只包含必需的命令和模板文件（不超过 50 个文件）
3. **Given** 用户运行 `uvx wiki-generator --help`，**When** 查看帮助信息，**Then** 应该显示简洁的用法说明和可用选项

---

### Edge Cases

- **网络中断**: 如果 `uvx` 无法下载包，应该给出清晰的错误提示和解决方案
- **权限不足**: 如果当前目录没有写入权限，应该提前检测并提示用户
- **文件冲突**: 如果目标文件已存在且内容不同，应该询问用户是否覆盖（提供 `--force` 选项跳过询问）
- **配置文件损坏**: 如果现有 `wiki-config.json` 不是有效的 JSON，应该备份并重新生成
- **部分安装失败**: 如果部分文件复制失败，应该回滚已安装的文件并报告错误

---

## Requirements

### Functional Requirements

- **FR-001**: 系统必须在用户运行 `uvx wiki-generator` 时将 `.claude/` 目录及其内容复制到当前工作目录
- **FR-002**: 系统必须生成包含 5 个核心字段的 `wiki-config.json` 文件（如果不存在）：`output_dir`（默认: "docs"）、`exclude_patterns`（默认: ["node_modules", "dist", ".git"]）、`quality_threshold`（默认: 80）、`diagrams_enabled`（默认: true）、`diagrams_detail_level`（默认: "medium"）
- **FR-003**: 系统必须在安装过程中显示进度信息（复制文件列表、状态提示）
- **FR-004**: 系统必须支持 `--force` 选项强制覆盖已存在的文件
- **FR-005**: 系统必须支持 `--dry-run` 选项显示将要安装的文件列表而不实际复制
- **FR-006**: 系统必须在安装失败时回滚已安装的文件并返回非零退出码
- **FR-007**: 系统必须提供 `--version` 选项显示当前工具版本
- **FR-008**: 系统必须在安装完成后显示成功消息和下一步操作提示
- **FR-009**: 系统必须验证目标目录有足够的写入权限后再开始安装
- **FR-010**: 系统必须处理符号链接（保留或展开，基于平台兼容性考虑）

### 非功能需求

- **性能**: 安装过程应该在 5 秒内完成（不包括 `uvx` 下载时间）
- **兼容性**: 工具应该在 Linux、macOS 和 Windows (WSL) 上正常运行
- **依赖**: 工具应该只依赖 Python 标准库，不要求额外的第三方包
- **文件大小**: 生成的 `.claude/` 目录和 `wiki-config.json` 总大小应该 < 1 MB

### Key Entities

- **Claude Command Files**: Claude Code 自定义命令 Markdown 文件（`.claude/commands/*.md`）
- **Template Files**: Wiki 文档生成模板（`.claude/templates/**/*.md`）
- **Configuration File** (`wiki-config.json`): JSON 格式的配置文件，包含以下字段：
  - `output_dir`: 文档输出目录（默认: "docs"）
  - `exclude_patterns`: 排除的文件/目录模式列表（默认: ["node_modules", "dist", ".git"]）
  - `quality_threshold`: 文档质量分数阈值（默认: 80）
  - `diagrams_enabled`: 是否生成图表（默认: true）
  - `diagrams_detail_level`: 图表细节级别（默认: "medium"，可选: "low"|"medium"|"high"）
- **Installation Manifest**: 安装清单（可选），记录已安装的文件和版本信息

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: 用户可以通过单个命令 `uvx wiki-generator` 在 10 秒内完成安装（包括 `uvx` 启动时间）
- **SC-002**: 安装成功率 ≥ 99%（在正常网络和文件系统条件下）
- **SC-003**: 生成的配置文件 100% 符合 JSON 格式规范（可通过 `jq` 或其他 JSON 验证工具验证）
- **SC-004**: 95% 的用户能够在不查看文档的情况下成功完成首次安装
- **SC-005**: 安装后的文件总数 < 100 个（保持轻量级）
- **SC-006**: 工具启动时间 < 2 秒（从执行命令到显示第一个输出）

### User Acceptance

- 用户反馈安装过程"简单直观"
- 用户不需要修改任何系统环境变量或路径
- 生成的配置文件包含清晰的中文注释
- 错误消息提供明确的解决步骤

---

## Assumptions & Dependencies

### Assumptions

- 用户已安装 Python 3.11 或更高版本（`uvx` 的要求）
- 用户有当前目录的写入权限
- 用户的网络可以访问 PyPI（用于 `uvx` 下载包）
- 目标项目使用 Git 或类似的版本控制系统（不是必需，但建议）

### Dependencies

- **Python**: 3.11+（`uvx` 工具的最低要求）
- **uv**: 通过 `uvx` 自动处理，无需用户手动安装
- **操作系统**: Linux、macOS、Windows (WSL)

### Out of Scope

以下功能明确排除在此优化范围外：

- ~~交互式配置向导~~（用户可以直接编辑 `wiki-config.json`）
- ~~自动检测项目类型和定制模板~~（留待 Wiki 生成命令处理）
- ~~版本管理和更新检查~~（用户通过 `uvx` 获取最新版本）
- ~~卸载功能~~（用户手动删除 `.claude/` 目录和 `wiki-config.json`）
- ~~图形界面~~（纯命令行工具）

---

## Open Questions

当前没有未解决的关键问题。所有核心功能需求已明确。

---

## Notes

- 现有的 `cli.py` 文件包含大量复杂的文档生成逻辑，应该只保留安装功能
- 新的工具应该是一个独立的、轻量级的安装脚本，不依赖任何第三方包
- 安装过程应该是幂等的（多次运行结果一致）
- 所有用户可见的消息应该使用简体中文

