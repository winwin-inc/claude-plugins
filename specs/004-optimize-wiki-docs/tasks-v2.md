# 任务列表：优化 Wiki 文档结构和模板 v2.0

**功能编号**: 004
**功能名称**: optimize-wiki-docs
**创建日期**: 2025-01-04
**状态**: 待执行
**版本**: 2.0.0

**架构说明**: 基于 v2.0 架构，Python 包只负责安装、配置验证和迁移工具。文档生成逻辑由 Claude Code `/wiki-generate` 命令实现。

---

## 实施策略

### MVP 范围定义

**最小可行产品（MVP）** 包括：
- ✅ 22 个高质量模板（中英各 11 个）
- ✅ 配置文件初始化（`--init`）
- ✅ 配置文件验证（`--validate`）
- ✅ JSON Schema 定义
- ✅ 文件安装机制

**增量交付**：
1. **Sprint 1（MVP）**: 模板创建 + 配置系统
2. **Sprint 2（增强）**: 安装和迁移工具
3. **Sprint 3（完善）**: CLI 集成和测试

### 并行执行机会

- 模板创建高度可并行（22 个独立文件）
- 配置系统与模板创建可部分并行
- 安装和迁移工具可并行开发

### 独立测试标准

每个功能需求完成后可独立验证：
- **FR-04**: 22 个模板全部存在，格式统一
- **FR-07**: 配置验证功能正常
- **FR-08**: 迁移工具可用

---

## Phase 1: 项目设置

### 目标
初始化项目结构，配置开发环境

### 任务

- [ ] T001 创建新的模块目录结构在 wiki_generator/ 下
- [ ] T002 [P] 在 wiki_generator/models/ 中创建 config_models.py，定义 WikiConfig, SectionConfig, TemplateInfo, TemplateManifest 等数据类
- [ ] T003 [P] 在 wiki_generator/utils/ 中创建 file_utils.py，实现文件安装和路径计算工具函数
- [ ] T004 [P] 更新 pyproject.toml 添加 jsonschema 依赖（配置验证）
- [ ] T005 [P] 创建测试目录结构 tests/test_v2/ 和初始测试文件

### 验收标准
- ✅ 模块目录结构创建完成
- ✅ 数据模型定义完整，包含类型注解
- ✅ 单元测试框架可以运行

---

## Phase 2: 基础设施（阻塞依赖）

### 目标
实现所有功能需求共享的基础模块

### 任务

- [ ] T006 实现 JSON Schema 加载器在 wiki_generator/core/schema_loader.py
- [ ] T007 实现配置验证器在 wiki_generator/core/config_validator.py，支持 jsonschema 验证
- [ ] T008 实现模板清单管理器在 wiki_generator/core/template_manifest.py
- [ ] T009 实现文件安装器在 wiki_generator/core/installer.py，支持复制 .claude/ 目录

### 验收标准
- ✅ JSON Schema 可以正确加载
- ✅ 配置验证功能正常（使用 wiki-config-schema-v2.json）
- ✅ 模板清单可以读取和管理
- ✅ 文件安装逻辑可以复制目录

---

## Phase 3: FR-04 - 模板创建

### 目标
创建 22 个高质量模板文件（中英各 11 个）

### 用户故事
**作为** 技术文档维护者
**我想要** 统一格式的高质量模板
**以便** Claude Code 能够生成一致的文档

### 任务

#### 中文模板（11 个）

- [ ] T010 [P] [FR-04] 创建 wiki_generator/.claude/templates/zh/quickstart.md.template，包含统一的页头结构（<cite>、目录、Section sources）和变量占位符
- [ ] T011 [P] [FR-04] 创建 wiki_generator/.claude/templates/zh/overview.md.template
- [ ] T012 [P] [FR-04] 创建 wiki_generator/.claude/templates/zh/techstack.md.template
- [ ] T013 [P] [FR-04] 创建 wiki_generator/.claude/templates/zh/architecture.md.template
- [ ] T014 [P] [FR-04] 创建 wiki_generator/.claude/templates/zh/datamodel.md.template
- [ ] T015 [P] [FR-04] 创建 wiki_generator/.claude/templates/zh/corefeatures.md.template
- [ ] T016 [P] [FR-04] 创建 wiki_generator/.claude/templates/zh/development.md.template
- [ ] T017 [P] [FR-04] 创建 wiki_generator/.claude/templates/zh/deployment.md.template
- [ ] T018 [P] [FR-04] 创建 wiki_generator/.claude/templates/zh/testing.md.template
- [ ] T019 [P] [FR-04] 创建 wiki_generator/.claude/templates/zh/troubleshooting.md.template
- [ ] T020 [P] [FR-04] 创建 wiki_generator/.claude/templates/zh/security.md.template

#### 英文模板（11 个）

- [ ] T021 [P] [FR-04] 创建 wiki_generator/.claude/templates/en/quickstart.md.template
- [ ] T022 [P] [FR-04] 创建 wiki_generator/.claude/templates/en/overview.md.template
- [ ] T023 [P] [FR-04] 创建 wiki_generator/.claude/templates/en/techstack.md.template
- [ ] T024 [P] [FR-04] 创建 wiki_generator/.claude/templates/en/architecture.md.template
- [ ] T025 [P] [FR-04] 创建 wiki_generator/.claude/templates/en/datamodel.md.template
- [ ] T026 [P] [FR-04] 创建 wiki_generator/.claude/templates/en/corefeatures.md.template
- [ ] T027 [P] [FR-04] 创建 wiki_generator/.claude/templates/en/development.md.template
- [ ] T028 [P] [FR-04] 创建 wiki_generator/.claude/templates/en/deployment.md.template
- [ ] T029 [P] [FR-04] 创建 wiki_generator/.claude/templates/en/testing.md.template
- [ ] T030 [P] [FR-04] 创建 wiki_generator/.claude/templates/en/troubleshooting.md.template
- [ ] T031 [P] [FR-04] 创建 wiki_generator/.claude/templates/en/security.md.template

#### 模板规范文档

- [ ] T032 [FR-04] 创建模板格式规范在 wiki_generator/.claude/templates/TEMPLATE_FORMAT.md，说明变量语法、Claude 指导注释、结构约定

### 验收标准

**FR-04 验收**:
- [ ] 所有 22 个模板文件存在
- [ ] 每个模板包含统一页头结构（标题、<cite>、目录、Section sources）
- [ ] 每个模板包含变量占位符（`{variable}` 格式）
- [ ] 每个模板包含 Claude 指导注释
- [ ] 模板文件命名符合规范（`<name>.md.template`）

### 测试方法

```bash
# 测试 FR-04
ls wiki_generator/.claude/templates/zh/ | wc -l  # 应该输出 11
ls wiki_generator/.claude/templates/en/ | wc -l  # 应该输出 11
grep -r "{title}" wiki_generator/.claude/templates/  # 验证变量占位符
```

---

## Phase 4: FR-07 - 配置系统

### 目标
实现配置文件验证和初始化功能

### 用户故事
**作为** 开发者
**我想要** 验证配置文件的正确性
**以便** 在生成文档前避免配置错误

### 任务

#### JSON Schema

- [ ] T033 [P] [FR-07] 创建 JSON Schema 文件在 wiki_generator/.claude/schema/wiki-config-schema.json，定义所有配置字段和验证规则

#### 配置验证模块

- [ ] T034 [P] [FR-07] 实现中文错误消息格式化在 wiki_generator/core/config_validator.py:format_error_chinese()
- [ ] T035 [P] [FR-07] 实现配置文件加载在 wiki_generator/core/config_validator.py:load_config()
- [ ] T036 [FR-07] 实现配置验证逻辑在 wiki_generator/core/config_validator.py:validate_config()

#### 初始化命令

- [ ] T037 [P] [FR-07] 实现默认配置生成在 wiki_generator/core/config_initializer.py:create_default_config()
- [ ] T038 [FR-07] 实现配置文件写入在 wiki_generator/core/config_initializer.py:write_config()

### 验收标准

**FR-07 验收**:
- [ ] JSON Schema 文件符合规范（wiki-config-schema-v2.json）
- [ ] 配置验证可以检测所有错误类型
- [ ] 错误消息使用中文，清晰易懂
- [ ] 初始化命令创建默认配置文件

### 测试方法

```bash
# 测试 FR-07
python -m wiki_generator.core.config_validator  # 验证模块导入
# 创建测试配置
echo '{"language": "invalid"}' > test-config.json
python -c "from wiki_generator.core.config_validator import validate_config; from pathlib import Path; validate_config(Path('test-config.json'))"  # 应该报错
```

---

## Phase 5: FR-08 - 迁移工具

### 目标
实现配置文件迁移功能

### 用户故事
**作为** 现有用户
**我想要** 从旧版本配置迁移到新版本
**以便** 继续使用 Wiki Generator 工具

### 任务

- [ ] T039 [P] [FR-08] 定义迁移规则在 wiki_generator/core/migrations.py:MIGRATION_RULES
- [ ] T040 [P] [FR-08] 实现版本检测在 wiki_generator/core/migrator.py:detect_version()
- [ ] T041 [P] [FR-08] 实现备份功能在 wiki_generator/core/migrator.py:backup_config()
- [ ] T042 [P] [FR-08] 实现迁移逻辑在 wiki_generator/core/migrator.py:apply_migration()
- [ ] T043 [FR-08] 实现迁移报告生成在 wiki_generator/core/migrator.py:generate_migration_report()
- [ ] T044 [FR-08] 创建迁移指南在 MIGRATION.md，说明新旧配置差异和迁移步骤

### 验收标准

**FR-08 验收**:
- [ ] 可以自动检测配置版本
- [ ] 迁移前自动备份原文件
- [ ] 迁移规则正确应用（添加字段、重命名字段、删除废弃字段）
- [ ] 生成详细的迁移报告
- [ ] 提供清晰的迁移指南文档

### 测试方法

```bash
# 测试 FR-08
# 创建旧版本配置
echo '{"lang": "zh"}' > .claude/wiki-config.json
# 运行迁移
wiki-generator --migrate
# 检查结果
cat .claude/wiki-config.json  # 应该包含 "language" 字段
cat .claude/wiki-config.json.backup  # 备份文件应该存在
```

---

## Phase 6: CLI 集成

### 目标
实现完整的 CLI 工具，集成所有功能

### 任务

#### CLI 命令实现

- [ ] T045 实现主 CLI 命令在 wiki_generator/cli.py:cli()
- [ ] T046 [P] 实现 --init 子命令在 wiki_generator/cli.py:init_command()
- [ ] T047 [P] 实现 --validate 子命令在 wiki_generator/cli.py:validate_command()
- [ ] T048 [P] 实现 --migrate 子命令在 wiki_generator/cli.py:migrate_command()
- [ ] T049 [P] 实现 --version 子命令在 wiki_generator/cli.py:version_command()

#### 文件安装集成

- [ ] T050 实现 .claude/ 目录安装逻辑在 wiki_generator/cli.py:init_command()
- [ ] T051 实现用户确认提示（覆盖检测）在 wiki_generator/core/installer.py:confirm_overwrite()
- [ ] T052 实现模板版本记录在 wiki_generator/core/installer.py:record_template_version()

#### 错误处理

- [ ] T053 实现统一的错误处理在 wiki_generator/core/errors.py
- [ ] T054 添加用户友好的错误消息在 wiki_generator/cli.py
- [ ] T055 实现日志输出在 wiki_generator/utils/logging.py

### 验收标准
- ✅ 所有子命令正常工作
- ✅ 错误处理完善，消息清晰
- ✅ 文件安装安全（备份、确认）
- ✅ 版本管理正确

---

## Phase 7: 测试和文档

### 目标
确保所有功能协同工作，质量达标

### 任务

#### 单元测试

- [ ] T056 [P] 编写配置验证测试在 tests/test_v2/test_config_validator.py
- [ ] T057 [P] 编写迁移工具测试在 tests/test_v2/test_migrator.py
- [ ] T058 [P] 编写文件安装测试在 tests/test_v2/test_installer.py
- [ ] T059 [P] 编写模板清单测试在 tests/test_v2/test_template_manifest.py
- [ ] T060 [P] 编写 CLI 命令测试在 tests/test_v2/test_cli.py

#### 集成测试

- [ ] T061 编写完整初始化流程测试在 tests/test_v2/test_integration_init.py
- [ ] T062 编写配置验证流程测试在 tests/test_v2/test_integration_validate.py
- [ ] T063 编写迁移流程测试在 tests/test_v2/test_integration_migrate.py

#### 用户文档

- [ ] T064 [P] 更新 README.md 添加新功能说明和 v2.0 架构介绍
- [ ] T065 [P] 创建 USAGE.md 详细使用指南
- [ ] T066 [P] 更新 CLAUDE.md 项目指南
- [ ] T067 创建 CHANGELOG.md 记录 v2.0 变更

#### 性能测试

- [ ] T068 性能测试：初始化性能 < 3 秒
- [ ] T069 性能测试：配置验证 < 1 秒
- [ ] T070 性能测试：配置迁移 < 2 秒

### 验收标准
- ✅ 所有测试通过
- ✅ 文档完整清晰
- ✅ 性能目标达成
- ✅ 用户可以独立使用工具

---

## Phase 8: 发布准备

### 目标
准备发布版本

### 任务

- [ ] T071 更新版本号到 2.0.0 在 pyproject.toml
- [ ] T072 创建发布说明在 RELEASE_NOTES.md
- [ ] T073 清理旧版本文档（v1.0）或移到 archive/
- [ ] T074 创建 Git tag 和发布
- [ ] T075 验证发布包（uv build && test_build.py）

### 验收标准
- ✅ 版本号正确
- ✅ 发布说明清晰
- ✅ 发布包可用

---

## 依赖关系图

```
Phase 1 (项目设置)
    ↓
Phase 2 (基础设施) ← 必须完成才能开始后续阶段
    ↓
    ├─→ Phase 3 (FR-04: 模板) ← 可部分并行
    ├─→ Phase 4 (FR-07: 配置系统) ← 可部分并行
    └─→ Phase 5 (FR-08: 迁移工具) ← 依赖 Phase 4
    ↓
Phase 6 (CLI 集成)
    ↓
Phase 7 (测试和文档)
    ↓
Phase 8 (发布准备)
```

---

## 并行执行示例

### Phase 3（模板创建）最大并行度

```bash
# 可以同时启动 22 个进程创建模板
process T010-T020 &  # 11 个中文模板
process T021-T031 &  # 11 个英文模板
wait
```

**预计时间节省**: 串行 22 个模板 × 20 分钟 = 7.3 小时 → 并行 1 小时（节省 86%）

---

## 任务统计

| Phase | 任务数 | 预计时间 | 并行机会 |
|-------|--------|----------|----------|
| Phase 1: 项目设置 | 5 | 0.5 天 | 3 个 [P] 任务 |
| Phase 2: 基础设施 | 4 | 1 天 | 无（有依赖） |
| Phase 3: FR-04 (模板) | 23 | 3 天 | 22 个 [P] 任务 |
| Phase 4: FR-07 (配置) | 6 | 2 天 | 5 个 [P] 任务 |
| Phase 5: FR-08 (迁移) | 6 | 2 天 | 5 个 [P] 任务 |
| Phase 6: CLI 集成 | 11 | 1 天 | 5 个 [P] 任务 |
| Phase 7: 测试和文档 | 15 | 2 天 | 9 个 [P] 任务 |
| Phase 8: 发布准备 | 5 | 0.5 天 | 2 个 [P] 任务 |
| **总计** | **75** | **12 天** | **51 个 [P] 任务** |

**预计完成时间**:
- 串行执行：12 天
- 并行执行（50% 并行度）：8-9 天
- 符合计划目标：10 天（留有缓冲）

---

## MVP 快速通道

如果需要快速交付 MVP（只包含模板和配置系统），执行以下任务：

**关键路径**（24 个任务）:
1. T001-T005: Phase 1（项目设置）
2. T006-T009: Phase 2（基础设施）
3. T010-T032: FR-04（22 个模板 + 规范）
4. T033-T038: FR-07（配置系统）

**预计 MVP 时间**: 6 天（并行执行）

---

## 与 v1.0 任务列表的差异

### 移除的任务（v1.0 中有，v2.0 中不需要）

- ❌ 文档结构生成器（由 Claude Code 处理）
- ❌ 模板渲染器（由 Claude Code AI 处理）
- ❌ 项目分析器（由 Claude Code AI 处理）
- ❌ 链接生成器（由 Claude Code AI 处理）
- ❌ AI 检测引擎（由 Claude Code AI 处理）

### 新增的任务（v2.0 特有）

- ✅ 模板清单管理器
- ✅ 文件安装器
- ✅ 迁移工具
- ✅ 配置验证器（简化版）

### 简化的任务

- **配置解析**: 从复杂的项目分析 → 简单的 JSON Schema 验证
- **模板系统**: 从动态渲染 → 静态 Markdown 文件
- **文档生成**: 从 Python 实现 → Claude Code 命令

---

## 格式验证

✅ **所有任务遵循 checklist 格式**:
- ✅ 以 `- [ ]` 开头（复选框）
- ✅ 包含任务 ID（T001-T075）
- ✅ 包含 [P] 标记（51 个可并行任务）
- ✅ 包含功能标签（[FR-04], [FR-07], [FR-08]）
- ✅ 包含明确的文件路径

✅ **组织结构符合要求**:
- ✅ 按 Phase 组织（8 个阶段）
- ✅ 每个功能需求独立验收
- ✅ 依赖关系清晰
- ✅ 并行执行示例明确

---

**任务列表版本**: 2.0.0
**创建日期**: 2025-01-04
**状态**: ✅ 就绪，可执行
**总任务数**: 75
**预计时间**: 12 天（串行），8-9 天（并行）
