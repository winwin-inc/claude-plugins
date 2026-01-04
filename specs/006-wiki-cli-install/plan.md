# Implementation Plan: Wiki Generator CLI 安装工具优化

**Branch**: `006-wiki-cli-install` | **Date**: 2026-01-04 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/006-wiki-cli-install/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

优化现有 Wiki Generator CLI 安装工具（cli.py），保留核心安装功能，移除不必要的复杂性。用户通过 `uvx wiki-generator` 命令即可一键将 Claude Code 自定义命令和模板文件安装到当前项目目录，并自动初始化 `wiki-config.json` 配置文件。

技术方法：
- 使用 Python 标准库（shutil、json、pathlib）实现文件操作
- 通过 `uvx` 实现零安装分发
- 支持跨平台文件复制和回滚机制
- 生成带默认配置的 JSON 文件（5 个核心字段）

---

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Python 标准库（shutil、json、pathlib、argparse），无第三方依赖
**Storage**: 文件系统（`.claude/` 目录、`wiki-config.json` 配置文件）
**Testing**: Shell 集成测试（测试整个安装工作流）
**Target Platform**: Linux、macOS、Windows (WSL)
**Project Type**: single（独立 Python CLI 工具）
**Performance Goals**:
  - 工具启动时间 < 2 秒（从执行命令到第一个输出）
  - 安装时间 < 5 秒（复制 < 100 个文件）
  - 内存占用 < 50 MB
  - 文件总数 < 100 个

**Constraints**:
  - 只依赖 Python 标准库（不使用第三方包）
  - 安装过程应该是幂等的（多次运行结果一致）
  - 必须支持回滚机制（失败时恢复原始状态）
  - 所有用户可见消息使用简体中文

**Scale/Scope**:
  - 支持跨平台（Linux/macOS/Windows）
  - 复制 < 100 个文件
  - 生成 1 个配置文件（5 个字段）
  - 目标用户：所有使用 Claude Code 的开发者

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

基于项目 CLAUDE.md 指南制定以下核心原则：

### I. Python 依赖管理 (NON-NEGOTIABLE)
- ✅ 不使用 `uv` 管理此工具的依赖（工具本身无第三方依赖）
- ✅ 用户通过 `uvx wiki-generator` 调用（`uvx` 自动管理 Python 环境）
- ✅ 如果用户使用 `pip install` 安装，可使用 `uv pip install`（但非必需）

### II. 语言与文档规范
- ✅ 所有用户可见消息使用**简体中文**
- ✅ 变量名用英文，注释用中文
- ✅ 错误消息、帮助信息、进度提示都用中文

### III. 文档策略
- ✅ **只编写代码，不生成文档**（安装工具本身不生成 Wiki 文档）
- ✅ 安装的工具文件（`.claude/` 目录）用于后续 Wiki 生成

### IV. 代码质量
- ✅ 遵循 PEP 8 代码规范
- ✅ 包含详细的中文注释和 Docstring
- ✅ 使用类型注解（Type Hints）

### V. 避免过度工程 (NON-NEGOTIABLE)
- ✅ 只保留核心安装功能（移除现有 cli.py 中的复杂文档生成逻辑）
- ✅ 优先选择简单直接的解决方案
- ✅ 不创建不必要的抽象层

### 宪法原则符合性评估

| 原则 | 设计决策 | 符合性 | 验证方法 |
|------|---------|--------|----------|
| **I. Python 依赖管理** | 工具本身无第三方依赖，用户通过 `uvx` 调用 | ✅ PASS | 检查 `pyproject.toml` 无运行时依赖 |
| **II. 语言与文档规范** | 所有输出消息使用中文 | ✅ PASS | 源代码中的所有字符串都是中文 |
| **III. 文档策略** | 只安装命令和模板，不生成文档 | ✅ PASS | 功能范围明确为安装工具 |
| **IV. 代码质量** | 遵循 PEP 8，包含类型注解 | ⏳ TODO | 代码审查时验证 |
| **V. 避免过度工程** | 移除复杂逻辑，只保留安装功能 | ✅ PASS | 功能单一，职责明确 |

### 潜在风险与缓解措施

| 风险 | 宪法原则影响 | 缓解措施 | 残余风险 |
|------|-------------|---------|----------|
| 过度简化导致功能缺失 | V. 避免过度工程 | 明确定义 MVP 范围，后续迭代添加 | 低 |
| 跨平台兼容性问题 | II. 语言与文档规范 | 在多个平台测试 | 低 |
| 回滚机制复杂度 | V. 避免过度工程 | 使用简单的文件列表跟踪 | 低 |

### 最终评估

✅ **PASS** - 当前设计完全符合项目宪法原则，无违规行为。

**关键优势**：
1. 工具本身无依赖，符合"轻量级"要求
2. 所有输出使用中文，符合语言规范
3. 功能单一明确，符合"避免过度工程"
4. 使用 `uvx` 分发，用户体验最佳

---

## Project Structure

### Documentation (this feature)

```text
specs/006-wiki-cli-install/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── api-contracts.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
repo-wiki/
├── wiki_generator/              # 新的安装工具包
│   ├── __init__.py              # 包初始化
│   ├── __main__.py              # 命令行入口点（供 uvx 调用）
│   ├── installer.py             # 核心安装逻辑
│   └── config.py                # 配置文件生成和验证
├── cli.py                       # 现有工具（将被替换或简化）
├── .claude/                     # Wiki 命令和模板（将被复制）
│   ├── commands/
│   └── templates/
├── pyproject.toml               # 项目配置
├── tests/                       # 集成测试
│   └── integration/
│       └── test_installation.sh
└── README-WIKI-GENERATOR.md     # 工具文档
```

**Structure Decision**:
- 采用单一项目结构（single project）
- 新建 `wiki_generator/` 包（不使用现有的 `cli.py`）
- 将安装逻辑模块化（`installer.py` 和 `config.py`）
- 保留集成测试，不编写单元测试（遵循"避免过度工程"）

---

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

**说明**：当前设计遵循项目宪法原则，无违规行为需要论证。

---

## Constitution Check (Post-Design)

*GATE: Design phase completion verification - Re-evaluated after Phase 1*

### 宪法原则符合性评估（设计后）

与设计前评估一致，所有原则仍然符合。设计阶段所做的决策：

1. **模块化设计**（`installer.py` + `config.py`）：
   - 符合"避免过度工程"原则（职责单一，不过度抽象）
   - 符合"代码质量"原则（易于理解和维护）

2. **使用 Python 标准库**：
   - 符合"Python 依赖管理"原则（无第三方依赖）
   - 符合"轻量级"要求

3. **错误处理和回滚**：
   - 符合"避免过度工程"原则（使用简单文件列表跟踪）
   - 不引入复杂的快照或事务机制

### 最终评估（设计后）

✅ **PASS** - 设计阶段完成后，仍然完全符合项目宪法原则。

**确认**：
- 所有核心实体和函数设计都遵循简洁原则
- 没有引入不必要的复杂性
- 跨平台兼容性通过标准库实现

---



### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
