# Tasks: 自动文档大纲提取与主题映射

**Input**: Design documents from `/specs/005-auto-doc-outline/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Architecture**: Claude Code Agent/Skill (Shell 脚本 + 内联 Python 片段)

**Tests**: 本项目使用 Shell 脚本集成测试，不编写 Python 单元测试。

**Organization**: Tasks are grouped by implementation phases from spec.md (阶段 1-5). Each phase builds on the previous one and delivers incremental value.

## Format: `[ID] [P?] [Phase] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[PhaseX]**: Which implementation phase this task belongs to (Phase 1-5)
- Include exact file paths in descriptions

## Path Conventions

- **Agent/Skill 文件**: `.claude/skills/doc-generator/`
- **命令文件**: `.claude/commands/`
- **模板文件**: `.claude/templates/`
- **集成测试**: `tests/integration/`
- **测试固件**: `tests/fixtures/`

---

## Phase 1: Setup & 技术栈检测增强 (1-2 天)

**Purpose**: 初始化 Agent/Skill 结构，实现技术栈检测功能（20+ 框架）

**Independent Test**: 在 FastAPI/Django/React 测试项目上运行技术栈检测，验证准确率 ≥ 95%

### Setup Tasks

- [X] T001 创建 Agent/Skill 目录结构 `.claude/skills/doc-generator/`
- [X] T002 创建文档模板目录结构 `.claude/templates/{base-docs,tech-specific,modules}/`
- [X] T003 创建集成测试目录 `tests/integration/` 和测试固件 `tests/fixtures/{projects,expected_outputs}/`
- [ ] T004 [P] 准备测试用项目：FastAPI 项目、Django 项目、React 项目、Monorepo 项目 到 `tests/fixtures/projects/`

### 技术栈检测实现

- [X] T005 [Phase1] 创建技术栈检测 Skill `.claude/skills/doc-generator/tech_stack_detection.md`，包含检测函数框架
- [X] T006 [Phase1] [P] 实现后端框架检测（FastAPI、Flask、Django）使用 `grep -r "from fastapi"`
- [X] T007 [Phase1] [P] 实现 ORM 检测（SQLAlchemy、Django ORM、Tortoise ORM）
- [X] T008 [Phase1] [P] 实现 CLI 框架检测（Click、Typer、argparse）
- [X] T009 [Phase1] [P] 实现前端框架检测（React、Vue、Streamlit，检查 `package.json`）
- [X] T010 [Phase1] [P] 实现任务队列检测（Celery、RQ）
- [X] T011 [Phase1] [P] 实现消息队列检测（Kafka、RabbitMQ）
- [X] T012 [Phase1] [P] 实现数据库检测（PostgreSQL、MySQL、MongoDB，检查依赖）
- [X] T013 [Phase1] [P] 实现缓存检测（Redis、Memcached）
- [X] T014 [Phase1] [P] 实现容器化检测（Dockerfile、docker-compose、Kubernetes）
- [X] T015 [Phase1] [P] 实现 API 规范检测（OpenAPI、GraphQL、gRPC）
- [X] T016 [Phase1] 添加检测失败处理逻辑（生成警告 + 手动配置指南）
- [ ] T017 [Phase1] 编写集成测试 `tests/integration/test_tech_stack_detection.sh`，验证检测准确率 ≥ 95%

**Checkpoint**: 技术栈检测功能完成，可以准确识别 20+ 技术栈

---

## Phase 2: 业务模块识别 & Monorepo 支持 (2-3 天)

**Purpose**: 实现业务模块自动识别、模块规模评估、Monorepo 结构检测

**Independent Test**: 在测试项目上运行模块识别，验证覆盖率 ≥ 90%，文件统计只包含源代码文件

### 业务模块识别实现

- [X] T018 [Phase2] 创建业务模块扫描 Skill `.claude/skills/doc-generator/module_scanning.md`，包含扫描逻辑框架
- [X] T019 [Phase2] 实现服务层识别（扫描 `src/services/`、`app/services/`、`services/`）
- [X] T020 [Phase2] 实现页面层识别（扫描 `pages/`、`app/pages/`、`src/pages/`）
- [X] T021 [Phase2] 实现路由识别（扫描 `api/`、`routers/`、`views/`）
- [X] T022 [Phase2] 实现模型层识别（扫描 `models/`、`src/models/`）
- [X] T023 [Phase2] 实现文件统计逻辑（只统计 `.py`、`.js`、`.tsx`、`.ts`、`.jsx`，排除 `test/`、`tests/`、`__pycache__/` 等）
- [X] T024 [Phase2] 实现模块规模评估逻辑（1-4/5-20/21-50/>50 文件 → 1-4 层深度）
- [ ] T025 [Phase2] 编写集成测试 `tests/integration/test_module_scanning.sh`，验证识别覆盖率 ≥ 90%

### Monorepo 支持实现

- [X] T026 [Phase2] 创建 Monorepo 检测 Skill `.claude/skills/doc-generator/monorepo_detection.md`
- [X] T027 [Phase2] 实现配置文件检测（`pnpm-workspace.yaml`、`nx.json`、`package.json` workspaces）
- [X] T028 [Phase2] 实现目录结构检测（`packages/`、`apps/`、`workspaces/`）
- [X] T029 [Phase2] 实现子项目独立文档生成逻辑（每个子项目单独应用检测规则）
- [ ] T030 [Phase2] 编写集成测试 `tests/integration/test_monorepo_support.sh`，使用 `tests/fixtures/projects/monorepo-project/`

**Checkpoint**: 业务模块识别和 Monorepo 支持完成，可以自动识别项目结构并确定文档层级

---

## Phase 3: 自适应内容生成 (3-5 天)

**Purpose**: 实现项目信息提取、文档模板变量填充、模块化文档内容生成

**Independent Test**: 在真实项目上运行内容生成，验证自动填充率 ≥ 70%

### 信息提取实现

- [X] T031 [Phase3] 创建信息提取 Skill `.claude/skills/doc-generator/content_extraction.md`
- [X] T032 [Phase3] 实现 README.md 提取逻辑（项目名称、描述、核心功能列表）
- [X] T033 [Phase3] 实现配置文件提取（`pyproject.toml`、`package.json`、`setup.py` 元数据）
- [X] T034 [Phase3] 实现代码 Docstring 提取（从主模块、类、函数的文档字符串）
- [X] T035 [Phase3] 实现代码注释提取（关键逻辑的行内注释）
- [X] T036 [Phase3] 实现分层降级策略（README → 配置文件 → Docstring → 注释 → 通用模板）
- [ ] T037 [Phase3] 编写集成测试 `tests/integration/test_content_extraction.sh`，验证信息提取完整性

### 文档生成实现

- [X] T038 [Phase3] 创建文档大纲生成 Skill `.claude/skills/doc-generator/outline_generation.md`
- [X] T039 [Phase3] 实现模块化文档大纲生成逻辑（根据模块规模生成 1-4 层结构）
- [X] T040 [Phase3] 创建文档内容生成 Skill `.claude/skills/doc-generator/content_generation.md`
- [X] T041 [Phase3] 实现文档模板变量填充逻辑（替换 `{{PROJECT_NAME}}`、`{{FEATURE_1}}` 等变量）
- [X] T042 [Phase3] 创建基础文档模板（快速开始、项目概述、开发指南、部署指南、测试策略、故障排除、安全考虑）
- [ ] T043 [Phase3] [P] 创建技术栈特定文档模板（API 文档、数据模型、CLI 命令参考）
- [X] T044 [Phase3] 实现模块文档模板（根据模块规模：小型/中型/大型/超大型）
- [X] T045 [Phase3] 添加 `<cite>` 引用生成逻辑（链接到源代码文件）
- [ ] T046 [Phase3] 编写集成测试 `tests/integration/test_content_generation.sh`，验证生成内容质量

**Checkpoint**: 自适应内容生成完成，可以自动填充 70%+ 文档内容

---

## Phase 4: 文档索引和导航生成 (1-2 天)

**Purpose**: 实现文档索引文件生成、交叉引用链接

**Independent Test**: 在生成的文档中验证索引包含所有文档，链接 100% 有效

### 索引生成实现

- [X] T047 [Phase4] 创建索引生成 Skill `.claude/skills/doc-generator/index_generation.md`
- [X] T048 [Phase4] 实现文档索引生成逻辑（包含所有生成的文档）
- [X] T049 [Phase4] 实现文档分组逻辑（快速开始、核心功能、技术文档、开发相关、部署与运维）
- [X] T050 [Phase4] 实现文档简短描述生成（1 句话）
- [X] T051 [Phase4] 实现文档间交叉引用链接
- [X] T052 [Phase4] 实现链接有效性验证逻辑
- [ ] T053 [Phase4] 编写集成测试 `tests/integration/test_index_generation.sh`，验证链接有效率 = 100%

**Checkpoint**: 文档索引和导航生成完成，所有文档链接有效

---

## Phase 5: 集成测试和优化 (2-3 天)

**Purpose**: 端到端测试、性能优化、边缘情况修复

**Independent Test**: 在多个真实项目上运行完整工作流，验证性能目标（检测 < 5 秒、识别 < 30 秒、生成 < 90 秒）

### 端到端集成测试

- [ ] T054 [Phase5] 创建端到端工作流测试 `tests/integration/test_full_workflow.sh`
- [ ] T055 [Phase5] 在 dingtalk-sdk-generator 项目上测试完整工作流
- [ ] T056 [Phase5] 在 dingtalk-notable-connect 项目上测试完整工作流
- [ ] T057 [Phase5] [P] 在 FastAPI 测试项目上测试完整工作流
- [ ] T058 [Phase5] [P] 在 Django 测试项目上测试完整工作流
- [ ] T059 [Phase5] [P] 在 React 测试项目上测试完整工作流
- [ ] T060 [Phase5] [P] 在 CLI 工具测试项目上测试完整工作流
- [ ] T061 [Phase5] 在 Monorepo 测试项目上测试完整工作流

### 性能优化

- [ ] T062 [Phase5] 优化技术栈检测性能（使用 `grep --exclude-dir` 跳过 `node_modules/`、`__pycache__/`）
- [ ] T063 [Phase5] 优化业务模块识别性能（缓存扫描结果）
- [ ] T064 [Phase5] 优化文件扫描算法（只扫描必要的目录）
- [ ] T065 [Phase5] 验证性能目标（检测 < 5 秒、识别 < 30 秒、生成 < 90 秒）

### 边缘情况修复

- [ ] T066 [Phase5] 修复不规范目录结构的处理逻辑
- [ ] T067 [Phase5] 修复缺失 README 的降级处理
- [ ] T068 [Phase5] 修复空项目的处理逻辑
- [ ] T069 [Phase5] 修复超大项目（>1000 文件）的性能问题
- [ ] T070 [Phase5] 添加调试模式（详细日志输出）

### 命令集成

- [ ] T071 [Phase5] 更新 `.claude/commands/wiki-generate.md`，集成所有 Agent/Skill 调用
- [ ] T072 [Phase5] 添加命令行参数支持（`--full`、`--tech-only`、`--modules-only`、`--verbose`）
- [ ] T073 [Phase5] 添加进度指示器和用户反馈

**Checkpoint**: 所有功能完成，性能达标，边缘情况处理完善

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 文档完善、代码质量提升、最终验证

- [ ] T074 [P] 为所有 Agent/Skill 文件添加详细的中文注释
- [ ] T075 [P] 使用 ShellCheck 验证所有 Shell 脚本质量
- [ ] T076 [P] 优化文档模板样式和格式
- [ ] T077 [P] 添加更多技术栈检测规则（如果有遗漏）
- [ ] T078 创建用户文档，说明如何使用 `/wiki-generate` 命令
- [ ] T079 在 quickstart.md 中添加快速开始指南
- [ ] T080 运行所有集成测试，验证整体功能
- [ ] T081 性能基准测试（记录各阶段耗时）
- [ ] T082 代码重构和优化（如果有需要）

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (技术栈检测)**: 无依赖 - 可以立即开始
- **Phase 2 (业务模块识别)**: 依赖 Phase 1 完成（需要技术栈检测辅助模块识别）
- **Phase 3 (内容生成)**: 依赖 Phase 2 完成（需要模块识别结果生成文档）
- **Phase 4 (索引生成)**: 依赖 Phase 3 完成（需要已生成的文档创建索引）
- **Phase 5 (集成测试)**: 依赖 Phase 1-4 全部完成（端到端测试需要完整工作流）
- **Phase 6 (Polish)**: 依赖 Phase 5 完成（基于测试结果进行优化）

### Parallel Opportunities

- **Phase 1**:
  - T006-T015（所有技术栈检测实现）可以并行开发（不同框架）
  - T004（准备测试项目）可以与 T005 并行

- **Phase 2**:
  - T019-T022（不同层的识别）可以并行开发
  - T030（Monorepo 测试）可以与 T026-T029 并行

- **Phase 3**:
  - T043（技术栈特定模板）可以并行开发（不同技术栈）
  - T032-T036（不同信息提取逻辑）可以并行开发

- **Phase 5**:
  - T057-T060（不同类型项目的测试）可以并行执行
  - T062-T064（不同性能优化）可以并行进行

- **Phase 6**:
  - T074-T077（文档和代码质量）可以并行进行

### Sequential Dependencies (Critical Path)

1. **Phase 1 必须最先完成**（所有后续阶段依赖技术栈检测）
2. **Phase 2 必须在 Phase 3 之前**（内容生成需要模块识别结果）
3. **Phase 3 必须在 Phase 4 之前**（索引生成需要已生成的文档）
4. **Phase 5 必须在 Phase 6 之前**（Polish 基于测试结果）

---

## Parallel Example: Phase 1 (技术栈检测)

```bash
# 同时实现所有技术栈检测逻辑（不同框架，无依赖）：
Task: "实现后端框架检测（FastAPI、Flask、Django）"
Task: "实现 ORM 检测（SQLAlchemy、Django ORM、Tortoise ORM）"
Task: "实现 CLI 框架检测（Click、Typer、argparse）"
Task: "实现前端框架检测（React、Vue、Streamlit）"
Task: "实现任务队列检测（Celery、RQ）"
Task: "实现消息队列检测（Kafka、RabbitMQ）"
```

---

## Implementation Strategy

### Incremental Phase-by-Phase Delivery

1. **Phase 1 完成** → 技术栈检测可用，可以识别项目使用的框架
2. **Phase 2 完成** → 业务模块识别可用，可以自动识别项目结构
3. **Phase 3 完成** → 内容生成可用，可以自动生成文档内容（MVP!）
4. **Phase 4 完成** → 索引生成可用，提供完整文档导航
5. **Phase 5 完成** → 性能优化，边缘情况处理，端到端测试通过

**MVP 建议**: Phase 1-3 完成后即可交付（技术栈检测 + 模块识别 + 内容生成 = 核心价值）

### Testing Strategy

- **集成测试为主**: 每个阶段结束时编写集成测试，验证整个工作流
- **真实项目测试**: 使用 dingtalk-sdk-generator、dingtalk-notable-connect 和测试固件项目
- **性能基准**: 记录各阶段耗时，确保满足性能目标
- **质量验证**: 使用 ShellCheck 验证脚本质量

---

## Notes

- **[P] 任务** = 不同文件，无依赖关系，可以并行开发
- **[PhaseX] 标签** = 标记任务所属的实施阶段（1-6）
- 每个阶段完成后都可以独立测试和验证
- 每个 Agent/Skill 文件应包含详细的中文注释
- 遵循项目宪法原则：避免过度工程、使用简体中文、优先选择简单方案
- 不创建 Python 模块包（core/、utils/），所有逻辑在 Agent/Skill 中实现
- 只编写集成测试，不编写 Python 单元测试

---

## Summary

- **Total Tasks**: 82
- **Setup Tasks**: 4
- **Phase 1 (技术栈检测)**: 13 tasks
- **Phase 2 (业务模块识别)**: 13 tasks
- **Phase 3 (内容生成)**: 16 tasks
- **Phase 4 (索引生成)**: 7 tasks
- **Phase 5 (集成测试)**: 20 tasks
- **Phase 6 (Polish)**: 9 tasks
- **Parallel Opportunities**: 38 tasks marked [P]
- **Estimated Time**: 9-15 天（符合 spec.md 估算）

**MVP Scope**: Phase 1-3 (技术栈检测 + 业务模块识别 + 内容生成) = 46 tasks，约 6-10 天

**Critical Path**: Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6

**Format Validation**: ✅ All tasks follow checklist format (`- [ ] [ID] [P?] [Phase?] Description with file path`)
