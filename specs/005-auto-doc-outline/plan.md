# Implementation Plan: 自动文档大纲提取与主题映射

**Branch**: `005-auto-doc-outline` | **Date**: 2026-01-04 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-auto-doc-outline/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

通过分析实际项目（dingtalk-sdk-generator 和 dingtalk-notable-connect）的 Wiki 文档结构，优化 `/wiki-generate` 命令，实现：
1. **自动技术栈检测**：支持 20+ 框架和库的自动识别（FastAPI、Django、React、SQLAlchemy 等）
2. **智能模块识别**：扫描服务层、页面层、API 路由、模型层，自动识别业务模块
3. **自适应文档深度**：根据模块规模（1-4/5-20/21-50/>50 文件）生成 1-4 层文档结构
4. **Monorepo 支持**：检测多包项目结构，为每个子项目生成独立文档集
5. **智能内容填充**：从 README、配置文件、代码注释提取信息，自动填充 70%+ 文档内容

技术方法：通过静态分析（grep/find）、模式匹配、模板变量填充实现全串行文档生成流程。所有核心逻辑在 **Claude Code Agent/Skill** 中实现，不创建独立的 Python 模块包。

## Technical Context

**Language/Version**: Shell/Bash (核心) + Python 3.11+ (辅助片段)
**Primary Dependencies**:
  - Shell 工具：`bash` (4.0+), `grep`, `find`, `sed`, `awk`
  - Claude Code：自定义斜杠命令 (`/wiki-generate`)
  - Agent/Skill 框架：Claude Code 内置 Agent 或 Skill 系统

**Storage**: 文件系统 (Markdown 文档生成到 `docs/` 或 `zh/content/`)
**Testing**: Shell 脚本集成测试（测试整个 Agent/Skill 工作流）
**Target Platform**: Linux/macOS (Claude Code 运行环境)
**Project Type**: single (Claude Code Agent/Skill + 文档生成脚本)

**Performance Goals**:
  - 技术栈检测时间 < 5 秒（中型项目）
  - 业务模块识别时间 < 30 秒（大型项目）
  - 文档生成时间 < 90 秒（大型项目）
  - 内存占用 < 500 MB

**Constraints**:
  - 采用**全串行处理**策略（避免并发问题和资源竞争）
  - 只统计源代码文件（排除测试、配置、构建文件）
  - 检测失败时生成基础文档 + 警告 + 手动配置指南
  - **所有核心逻辑在 Agent/Skill 中实现**（不创建 core/、utils/ Python 模块）

**Scale/Scope**:
  - 支持 20+ 技术栈检测规则
  - 支持小型到超大型项目（1-1000+ 文件）
  - 生成 1-4 层文档结构
  - 目标文档覆盖率 ≥ 90%

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

基于项目 CLAUDE.md 指南制定以下核心原则：

### I. Python 依赖管理 (NON-NEGOTIABLE)
- ✅ 使用 `uv` 管理所有 Python 依赖（如果有辅助 Python 脚本）
- ✅ 命令格式：`uv run pytest` / `uv run python ...`
- ❌ 禁止直接使用 `python` 或 `pytest` 命令

### II. 语言与文档规范
- ✅ 所有交互使用**简体中文**（代码注释、文档、错误消息、日志）
- ✅ 变量名用英文，注释用中文
- ✅ **只编写代码，不生成文档**（除非用户明确要求）

### III. 测试策略
- ✅ 使用 Shell 脚本集成测试（测试整个 Agent/Skill 工作流）
- ✅ 不编写 Python 单元测试（遵循"避免过度工程"原则）
- ✅ 测试覆盖率通过端到端测试验证

### IV. 代码质量
- ✅ Shell 脚本遵循 Shell 最佳实践（ShellCheck）
- ✅ Python 片段遵循 PEP 8（如果有）
- ✅ 所有脚本包含详细的中文注释

### V. 避免过度工程 (NON-NEGOTIABLE)
- ✅ 避免创建不必要的抽象层
- ✅ 优先选择简单直接的解决方案
- ✅ **不创建独立的 Python 模块包**（core/、utils/ 等）
- ✅ **在 Agent/Skill 中实现所有核心逻辑**

## Project Structure

### Documentation (this feature)

```text
specs/005-auto-doc-outline/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── tech-stack-detection-rules.md
│   └── file-extraction-strategies.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
repo-wiki/
├── .claude/                   # Claude Code 配置和命令
│   ├── commands/
│   │   └── wiki-generate.md   # 文档生成命令（入口，调用 Agent/Skill）
│   ├── skills/                # Claude Code Skills（核心逻辑实现）
│   │   └── doc-generator/
│   │       ├── tech_stack_detection.md      # 技术栈检测逻辑
│   │       ├── module_scanning.md           # 业务模块识别逻辑
│   │       ├── monorepo_detection.md        # Monorepo 结构检测
│   │       ├── content_extraction.md        # 信息提取逻辑
│   │       ├── outline_generation.md        # 文档大纲生成
│   │       ├── content_generation.md        # 文档内容生成
│   │       └── index_generation.md          # 文档索引生成
│   └── templates/             # 文档模板
│       ├── base-docs/         # 基础必需文档模板
│       ├── tech-specific/     # 技术栈特定文档模板
│       └── modules/           # 业务模块文档模板
│
├── tests/                     # 测试目录
│   ├── integration/           # 集成测试（Shell 脚本）
│   │   ├── test_tech_stack_detection.sh
│   │   ├── test_module_scanning.sh
│   │   ├── test_content_extraction.sh
│   │   ├── test_full_workflow.sh
│   │   └── test_monorepo_support.sh
│   └── fixtures/              # 测试固件
│       ├── projects/          # 测试用项目样本
│       │   ├── fastapi-project/
│       │   ├── django-project/
│       │   ├── react-project/
│       │   └── monorepo-project/
│       └── expected_outputs/  # 预期输出样本
│
├── pyproject.toml             # 项目配置（如果有辅助 Python 工具）
├── cli.py                     # Wiki Generator 安装工具
└── CLAUDE.md                  # Claude Code 指南
```

**Structure Decision**:
- 采用 **Agent/Skill 架构**（而非 Python 模块包）
- 核心逻辑集中在 `.claude/skills/doc-generator/` 目录中
- 每个功能模块一个 Skill 文件（tech_stack_detection.md、module_scanning.md 等）
- 通过 `/wiki-generate` 命令调用相关 Skills
- 只保留集成测试，不编写单元测试（遵循"避免过度工程"原则）
- 符合项目定位：Claude Code 工具，非独立 Python 包

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

**说明**：当前设计遵循项目宪法原则，无违规行为需要论证。采用 Agent/Skill 架构是**更简单**的方案，而非过度工程。

---

## Constitution Check (Post-Design)

*GATE: Design phase completion verification - Re-evaluated after Phase 1*

### 宪法原则符合性评估

| 原则 | 设计决策 | 符合性 | 验证方法 |
|------|---------|--------|---------|
| **I. Python 依赖管理** | 不创建 Python 模块包，Agent/Skill 使用 Shell 脚本 | ✅ PASS | 无需 `uv` 依赖管理（Shell 脚本独立运行） |
| **II. 语言与文档规范** | Shell 脚本注释使用中文，变量名用英文 | ✅ PASS | Agent/Skill 文件包含详细中文注释 |
| **III. 测试策略** | 只编写集成测试（Shell 脚本），不编写单元测试 | ✅ PASS | `tests/integration/` 包含端到端测试 |
| **IV. 代码质量** | Shell 脚本遵循 Shell 最佳实践 | ✅ PASS | 使用 ShellCheck 验证脚本质量 |
| **V. 避免过度工程** | 采用 Agent/Skill 架构，不创建 core/、utils/ 模块 | ✅ PASS | 所有逻辑集中在 Agent/Skill 文件中，无复杂抽象 |

### 设计决策与宪法一致性验证

#### 1. 架构选择
- **决策**：采用 Claude Code Agent/Skill 架构，而非 Python 模块包
- **符合性**：✅ 完全符合"避免过度工程"原则
- **理由**：
  - Agent/Skill 比 Python 模块包**更简单**（无需打包、依赖管理）
  - 符合项目定位（Claude Code 工具，非独立 Python 包）
  - 用户可直接阅读和修改 Shell 脚本（无需理解 Python 模块结构）

#### 2. 实现语言
- **决策**：Shell/Bash 脚本为核心，Python 作为辅助片段
- **符合性**：✅ 符合"优先选择简单直接的解决方案"
- **理由**：Shell 工具（grep、find）快速可靠，无需额外依赖

#### 3. 测试策略
- **决策**：只编写集成测试，不编写单元测试
- **符合性**：✅ 符合"避免过度工程"原则
- **理由**：Agent/Skill 的单元测试价值低，端到端测试更能验证实际工作流

#### 4. 并发策略
- **决策**：全串行处理（用户明确选择）
- **符合性**：✅ 符合"优先选择简单直接的解决方案"
- **理由**：避免并发问题和资源竞争，性能满足需求

#### 5. 实施架构约束
- **决策**：不创建 core/、utils/ Python 模块
- **符合性**：✅ 符合"避免创建不必要的抽象层"
- **理由**：所有逻辑集中在 Agent/Skill 文件中更易维护

### 潜在风险与缓解措施

| 风险 | 宪法原则影响 | 缓解措施 |
|------|-------------|---------|
| Shell 脚本可维护性 | IV. 代码质量 | 提供详细中文注释，遵循 Shell 最佳实践，使用 ShellCheck 验证 |
| 文档生成质量 | II. 语言与文档规范 | 分层信息提取 + 人工审核指南 |
| 测试覆盖率不足 | III. 测试策略 | 通过端到端集成测试覆盖主要场景 |
| Agent/Skill 调试困难 | IV. 代码质量 | 添加详细日志输出，提供调试模式 |

### 最终评估

✅ **PASS** - 当前设计完全符合项目宪法原则，无违规行为。

**关键优势**：
1. 采用 Agent/Skill 架构是**最简单**的方案（比 Python 模块包更简单）
2. 所有逻辑集中在 Shell 脚本中，用户可直接阅读和修改
3. 无需依赖管理和打包，符合 Claude Code 工具定位
4. 只编写集成测试，避免过度工程

**建议**：
1. 在实施过程中确保所有 Shell 脚本包含详细的中文注释
2. 使用 ShellCheck 验证脚本质量
3. 编写全面的集成测试，覆盖主要场景
4. 定期更新 Agent 上下文，保持技术栈信息同步

---
