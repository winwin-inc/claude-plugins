# 任务列表：优化 Wiki 文档结构和模板

**功能编号**: 004
**功能名称**: optimize-wiki-docs
**创建日期**: 2025-01-04
**状态**: 待执行
**版本**: 1.0.0

---

## 实施策略

### MVP 范围定义

**最小可行产品（MVP）** 包括 FR-01 到 FR-05：
- ✅ 分层目录结构（FR-01）
- ✅ 自定义目录配置和 AI 检测（FR-02）
- ✅ 统一文档格式（FR-03）
- ✅ 11 种文档类型模板（FR-04）
- ✅ 中英文双语支持（FR-05）

**增量交付**：
1. **Sprint 1（MVP）**: FR-01 到 FR-05 - 核心模板和目录结构
2. **Sprint 2（增强）**: FR-06 - 交叉引用链接
3. **Sprint 3（完善）**: FR-07 到 FR-08 - 配置系统和迁移工具

### 并行执行机会

每个功能需求内的子任务大多可以并行执行（标记为 [P]）。

### 独立测试标准

每个 FR 完成后可独立验证：
- **FR-01**: 生成的目录结构与参考项目一致
- **FR-02**: AI 检测准确率 ≥ 80%，配置覆盖有效
- **FR-03**: 所有文档包含 `<cite>`、目录、Section sources
- **FR-04**: 11 种模板全部存在，变量替换正常
- **FR-05**: 中英文模板独立工作，双语生成正确
- **FR-06**: 链接准确率 ≥ 95%
- **FR-07**: 配置验证通过，自定义结构生效
- **FR-08**: 迁移工具可用，迁移指南清晰

---

## Phase 1: 项目设置

### 目标
初始化项目结构，配置开发环境

### 任务

- [ ] T001 创建新的模块目录结构在 wiki_generator/ 下
- [ ] T002 [P] 在 wiki_generator/models/ 中创建 data_models.py，定义 WikiConfig, DocumentMetadata, ProjectInfo, ConditionDocs 等数据类
- [ ] T003 [P] 在 wiki_generator/utils/ 中创建 path_utils.py，实现目录创建和路径计算工具函数
- [ ] T004 [P] 更新 pyproject.toml 添加 jsonschema 依赖（配置验证）
- [ ] T005 [P] 创建测试目录结构 tests/test_optimize/ 和初始测试文件

### 验收标准
- ✅ 模块目录结构创建完成
- ✅ 数据模型定义完整，包含类型注解
- ✅ 单元测试框架可以运行

---

## Phase 2: 基础设施（阻塞依赖）

### 目标
实现所有功能需求共享的基础模块

### 任务

- [ ] T006 实现配置解析器在 wiki_generator/core/config_parser.py，支持 JSON Schema 验证
- [ ] T007 实现模板渲染器在 wiki_generator/core/template_renderer.py，基于 string.Template
- [ ] T008 实现项目分析器在 wiki_generator/core/project_analyzer.py，支持 AI 检测条件文档
- [ ] T009 实现文档结构生成器在 wiki_generator/core/structure_generator.py，支持分层目录创建

### 验收标准
- ✅ 配置文件验证功能正常（使用 wiki-config-schema.json）
- ✅ 模板变量替换正常（支持 {variable} 语法）
- ✅ 项目分析准确检测技术栈和条件文档（≥80% 准确率）
- ✅ 分层目录结构正确生成（docs/{zh|en}/content/）

---

## Phase 3: FR-01 & FR-02 - 目录结构优化

### 目标
实现分层目录结构和自定义配置支持

### 用户故事
**作为** 项目负责人
**我想要** 生成的文档采用清晰的分层目录结构
**以便** 团队成员快速定位信息

### 任务

#### FR-01: 分层目录结构

- [ ] T010 [P] [FR-01] 实现目录创建逻辑在 wiki_generator/core/structure_generator.py:create_layered_structure()
- [ ] T011 [P] [FR-01] 实现数字前缀排序在 wiki_generator/utils/path_utils.py:generate_numbered_prefix()
- [ ] T012 [FR-01] 实现模块目录命名在 wiki_generator/core/structure_generator.py:create_module_dirs()
- [ ] T013 [FR-01] 添加目录冲突检测在 wiki_generator/utils/path_utils.py:detect_conflicts()
- [ ] T014 [FR-01] 编写单元测试 tests/test_structure_generator.py 验证目录结构生成

#### FR-02: 自定义目录配置和 AI 检测

- [ ] T015 [P] [FR-02] 实现预设模板选择在 wiki_generator/core/config_parser.py:apply_structure_template()
- [ ] T016 [P] [FR-02] 实现 AI 检测规则引擎在 wiki_generator/core/project_analyzer.py:ConditionAnalyzer
- [ ] T017 [FR-02] 实现自定义模块分组在 wiki_generator/core/structure_generator.py:apply_custom_structure()
- [ ] T018 [FR-02] 实现配置覆盖 AI 检测在 wiki_generator/core/config_parser.py:override_ai_detection()
- [ ] T019 [FR-02] 编写单元测试 tests/test_project_analyzer.py 验证 AI 检测准确率

### 验收标准

**FR-01 验收**:
- [ ] 生成的目录结构与参考项目一致（docs/{zh|en}/content/）
- [ ] 顶级文档使用数字前缀排序（00-99）
- [ ] 模块目录名称清晰反映功能

**FR-02 验收**:
- [ ] 可以选择"参考项目"、"简化"、"自定义"模板
- [ ] 可以自定义模块分组规则
- [ ] 配置文件格式符合 JSON Schema
- [ ] AI 能准确检测项目特征并生成相应的条件文档（≥80% 准确率）
- [ ] 用户可以覆盖自动检测结果

### 测试方法

```bash
# 测试 FR-01
cd /tmp/test_project
wiki-generator --full --structure reference
ls -R docs/zh/content/  # 验证目录结构

# 测试 FR-02
cat > .claude/wiki-config.json << EOF
{
  "structure_template": "custom",
  "sections": {
    "optional": ["datamodel"]
  }
}
EOF
wiki-generator --full
ls docs/zh/content/04-数据模型/  # 验证条件文档生成
```

---

## Phase 4: FR-03, FR-04 & FR-05 - 文档模板优化

### 目标
实现统一文档格式、完整模板类型、中英文双语支持

### 用户故事
**作为** 技术文档维护者
**我想要** 所有文档格式统一且包含完整文档类型
**以便** 自动生成符合规范的文档

### 任务

#### FR-03: 统一文档格式

- [ ] T020 [P] [FR-03] 实现页头结构在 wiki_generator/core/template_renderer.py:render_header()
- [ ] T021 [P] [FR-03] 实现 `<cite>` 块生成在 wiki_generator/core/template_renderer.py:render_cite_block()
- [ ] T022 [P] [FR-03] 实现目录索引生成在 wiki_generator/core/template_renderer.py:render_toc()
- [ ] T023 [P] [FR-03] 实现 Section sources 生成在 wiki_generator/core/template_renderer.py:render_section_sources()

#### FR-04: 11 种文档类型模板（中文）

- [ ] T024 [P] [FR-04] 创建 wiki_generator/.claude/templates/zh/quickstart.md.template
- [ ] T025 [P] [FR-04] 创建 wiki_generator/.claude/templates/zh/overview.md.template
- [ ] T026 [P] [FR-04] 创建 wiki_generator/.claude/templates/zh/techstack.md.template
- [ ] T027 [P] [FR-04] 创建 wiki_generator/.claude/templates/zh/architecture.md.template
- [ ] T028 [P] [FR-04] 创建 wiki_generator/.claude/templates/zh/datamodel.md.template
- [ ] T029 [P] [FR-04] 创建 wiki_generator/.claude/templates/zh/corefeatures.md.template
- [ ] T030 [P] [FR-04] 创建 wiki_generator/.claude/templates/zh/development.md.template
- [ ] T031 [P] [FR-04] 创建 wiki_generator/.claude/templates/zh/deployment.md.template
- [ ] T032 [P] [FR-04] 创建 wiki_generator/.claude/templates/zh/testing.md.template
- [ ] T033 [P] [FR-04] 创建 wiki_generator/.claude/templates/zh/troubleshooting.md.template
- [ ] T034 [P] [FR-04] 创建 wiki_generator/.claude/templates/zh/security.md.template

#### FR-04: 11 种文档类型模板（英文）

- [ ] T035 [P] [FR-04] 创建 wiki_generator/.claude/templates/en/quickstart.md.template
- [ ] T036 [P] [FR-04] 创建 wiki_generator/.claude/templates/en/overview.md.template
- [ ] T037 [P] [FR-04] 创建 wiki_generator/.claude/templates/en/techstack.md.template
- [ ] T038 [P] [FR-04] 创建 wiki_generator/.claude/templates/en/architecture.md.template
- [ ] T039 [P] [FR-04] 创建 wiki_generator/.claude/templates/en/datamodel.md.template
- [ ] T040 [P] [FR-04] 创建 wiki_generator/.claude/templates/en/corefeatures.md.template
- [ ] T041 [P] [FR-04] 创建 wiki_generator/.claude/templates/en/development.md.template
- [ ] T042 [P] [FR-04] 创建 wiki_generator/.claude/templates/en/deployment.md.template
- [ ] T043 [P] [FR-04] 创建 wiki_generator/.claude/templates/en/testing.md.template
- [ ] T044 [P] [FR-04] 创建 wiki_generator/.claude/templates/en/troubleshooting.md.template
- [ ] T045 [P] [FR-04] 创建 wiki_generator/.claude/templates/en/security.md.template

#### FR-05: 中英文双语支持

- [ ] T046 [P] [FR-05] 实现语言配置解析在 wiki_generator/core/config_parser.py:parse_language_config()
- [ ] T047 [P] [FR-05] 实现单语言生成在 wiki_generator/core/structure_generator.py:generate_single_language()
- [ ] T048 [P] [FR-05] 实现双语生成在 wiki_generator/core/structure_generator.py:generate_both_languages()
- [ ] T049 [FR-05] 更新 CLI 参数在 wiki_generator/cli.py 支持 --language 参数
- [ ] T050 [FR-05] 编写集成测试 tests/test_bilingual_generation.py

### 验收标准

**FR-03 验收**:
- [ ] 所有模板包含统一页头结构（标题、<cite>、目录、Section sources）
- [ ] 引用文件列表自动从代码分析中提取
- [ ] 目录索引自动根据标题生成
- [ ] Section sources 准确记录来源文件和行号

**FR-04 验收**:
- [ ] 所有 22 个模板文件存在（中英各 11 个）
- [ ] 每个模板包含参考项目的关键章节
- [ ] 模板支持变量替换（{project_name}, {version}, {cite_files} 等）

**FR-05 验收**:
- [ ] `templates/zh/` 包含所有中文模板（11 个）
- [ ] `templates/en/` 包含所有英文模板（11 个）
- [ ] 配置文件可以指定语言：`"language": "zh" | "en" | "both"`
- [ ] 默认只生成配置中指定的一种语言文档
- [ ] 当 `language: "both"` 时，同时生成 `docs/zh/` 和 `docs/en/` 两个目录

### 测试方法

```bash
# 测试 FR-03
wiki-generator --full
grep -c "<cite>" docs/zh/content/*.md  # 验证所有文档包含 cite 块
grep -c "## 目录" docs/zh/content/*.md  # 验证所有文档包含目录

# 测试 FR-04
ls wiki_generator/.claude/templates/zh/ | wc -l  # 应该输出 11
ls wiki_generator/.claude/templates/en/ | wc -l  # 应该输出 11

# 测试 FR-05
cat > .claude/wiki-config.json << EOF
{"language": "both"}
EOF
wiki-generator --full
ls docs/zh/content/ docs/en/content/  # 验证双语目录都存在
```

---

## Phase 5: FR-06 - 交叉引用支持

### 目标
实现文档间自动交叉引用链接生成

### 用户故事
**作为** 文档用户
**我想要** 文档中的引用自动转换为链接
**以便** 快速跳转到相关文档和代码

### 任务

- [ ] T051 [P] [FR-06] 实现文档链接识别在 wiki_generator/core/link_generator.py:extract_doc_links()
- [ ] T052 [P] [FR-06] 实现代码链接识别在 wiki_generator/core/link_generator.py:extract_code_links()
- [ ] T053 [P] [FR-06] 实现锚点链接识别在 wiki_generator/core/link_generator.py:extract_anchor_links()
- [ ] T054 [FR-06] 实现相对路径计算在 wiki_generator/utils/path_utils.py:calculate_relative_path()
- [ ] T055 [FR-06] 实现链接插入在 wiki_generator/core/link_generator.py:insert_links()
- [ ] T056 [FR-06] 实现链接验证在 wiki_generator/core/link_validator.py
- [ ] T057 [FR-06] 编写单元测试 tests/test_link_generator.py

### 验收标准

**FR-06 验收**:
- [ ] 识别文档中的模块引用（如"参见认证模块"）
- [ ] 自动生成正确的相对路径
- [ ] 链接在生成的文档中有效
- [ ] 支持三种链接类型：文档链接、代码链接、锚点链接
- [ ] 链接准确率 ≥ 95%

### 测试方法

```bash
# 测试 FR-06
wiki-generator --full --generate-links
grep -r "\](../" docs/zh/content/ | wc -l  # 统计文档链接数
grep -r "\](file://" docs/zh/content/ | wc -l  # 统计代码链接数
python wiki_generator/core/link_validator.py docs/zh/content/  # 验证链接有效性
```

---

## Phase 6: FR-07 & FR-08 - 配置和迁移支持

### 目标
完善配置系统和提供迁移工具

### 用户故事
**作为** 现有用户
**我想要** 从旧版本平滑迁移到新版本
**以便** 继续使用 Wiki Generator 工具

### 任务

#### FR-07: 配置系统

- [ ] T058 [P] [FR-07] 实现自定义结构配置在 wiki_generator/core/config_parser.py:parse_custom_structure()
- [ ] T059 [P] [FR-07] 实现格式化配置在 wiki_generator/core/config_parser.py:parse_formatting_options()
- [ ] T060 [P] [FR-07] 实现链接配置在 wiki_generator/core/config_parser.py:parse_links_config()
- [ ] T061 [FR-07] 创建配置验证工具在 wiki_generator/tools/validate_config.py
- [ ] T062 [FR-07] 编写配置示例在 docs/config-examples.md

#### FR-08: 迁移支持

- [ ] T063 [P] [FR-08] 实现旧配置检测在 wiki_generator/core/migration.py:detect_old_config()
- [ ] T064 [P] [FR-08] 实现配置迁移在 wiki_generator/core/migration.py:migrate_config()
- [ ] T065 [P] [FR-08] 实现迁移错误消息在 wiki_generator/core/migration.py:format_migration_error()
- [ ] T066 [FR-08] 创建迁移工具在 wiki_generator/tools/migrate_config.py
- [ ] T067 [P] [FR-08] 编写迁移指南在 MIGRATION.md
- [ ] T068 [FR-08] 更新 CLI 在 wiki_generator/cli.py 添加 --migrate 参数

### 验收标准

**FR-07 验收**:
- [ ] 配置文件格式符合 JSON Schema（wiki-config-schema.json）
- [ ] 支持 `structure_template` 选择预设（reference/simple/custom）
- [ ] 支持自定义结构配置（sections.required/optional）
- [ ] 配置验证通过，错误消息清晰

**FR-08 验收**:
- [ ] 提供详细的迁移指南文档（MIGRATION.md）
- [ ] 检测到旧配置时显示清晰的错误消息和迁移步骤
- [ ] 提供配置转换脚本 `migrate_config.py`
- [ ] 文档清楚说明新旧结构的差异和迁移必要性

### 测试方法

```bash
# 测试 FR-07
cat > .claude/wiki-config.json << EOF
{
  "structure_template": "custom",
  "sections": {
    "required": ["quickstart"],
    "optional": ["datamodel"]
  },
  "formatting": {
    "code_block_syntax": true,
    "line_numbers": true
  }
}
EOF
python wiki_generator/tools/validate_config.py .claude/wiki-config.json

# 测试 FR-08
python wiki_generator/tools/migrate_config.py --help
python wiki_generator/tools/migrate_config.py --dry-run
```

---

## Phase 7: 集成与优化

### 目标
确保所有功能协同工作，性能达标

### 任务

- [ ] T069 [P] 实现完整文档生成流程在 wiki_generator/core/generator.py:generate_full_docs()
- [ ] T070 [P] 实现增量更新流程在 wiki_generator/core/generator.py:generate_incremental_docs()
- [ ] T071 [P] 添加性能计时在 wiki_generator/core/generator.py:track_performance()
- [ ] T072 [P] 实现批处理优化在 wiki_generator/core/generator.py:batch_process_files()
- [ ] T073 [P] 实现模板缓存在 wiki_generator/core/template_renderer.py:TemplateCache
- [ ] T074 添加进度显示在 wiki_generator/cli.py:show_progress()
- [ ] T075 编写端到端测试 tests/test_e2e.py
- [ ] T076 性能测试：小型项目（< 100 文件，< 15 秒）
- [ ] T077 性能测试：中型项目（100-500 文件，< 30 秒）
- [ ] T078 性能测试：大型项目（> 500 文件，< 90 秒）

### 验收标准
- ✅ 完整生成功能正常（`wiki-generator --full`）
- ✅ 增量更新功能正常（`wiki-generator --update`）
- ✅ 性能目标达成（< 15/30/90 秒）
- ✅ 所有测试通过

---

## Phase 8: 文档与发布

### 目标
完善用户文档，准备发布

### 任务

- [ ] T079 [P] 更新 README.md 添加新功能说明
- [ ] T080 [P] 更新 QUICK_START.md 包含新功能使用示例
- [ ] T081 [P] 创建 CHANGELOG.md 记录破坏性变更
- [ ] T082 [P] 创建配置参考文档 docs/REFERENCE.md
- [ ] T083 [P] 更新 CLAUDE.md 项目指南
- [ ] T084 用户验收测试：5 分钟文档查找测试
- [ ] T085 用户验收测试：文档格式一致性检查
- [ ] T086 准备发布：版本号更新到 2.0.0（破坏性变更）
- [ ] T087 创建 Git tag 和发布说明

### 验收标准
- ✅ 文档完整清晰
- ✅ 用户验收测试通过
- ✅ 发布准备完成

---

## 依赖关系图

```
Phase 1 (项目设置)
    ↓
Phase 2 (基础设施) ← 必须完成才能开始后续阶段
    ↓
    ├─→ Phase 3 (FR-01 & FR-02: 目录结构)
    ├─→ Phase 4 (FR-03, FR-04 & FR-05: 模板)
    └─→ Phase 5 (FR-06: 交叉引用) ← 依赖 Phase 3
    ↓
Phase 6 (FR-07 & FR-08: 配置和迁移) ← 依赖 Phase 3, 4
    ↓
Phase 7 (集成与优化) ← 依赖所有前面的阶段
    ↓
Phase 8 (文档与发布)
```

---

## 并行执行示例

### Phase 4（模板开发）最大并行度

```bash
# 可以同时启动 11 个进程创建中文模板
process T024 &  # quickstart
process T025 &  # overview
process T026 &  # techstack
...
process T034 &  # security
wait

# 同时启动 11 个进程创建英文模板
process T035 &  # quickstart
process T036 &  # overview
...
process T045 &  # security
wait
```

**预计时间节省**: 串行 22 个模板 × 30 分钟 = 11 小时 → 并行 2 小时（节省 82%）

---

## 任务统计

| Phase | 任务数 | 预计时间 | 并行机会 |
|-------|--------|----------|----------|
| Phase 1: 项目设置 | 5 | 0.5 天 | 3 个 [P] 任务 |
| Phase 2: 基础设施 | 4 | 1 天 | 无（有依赖） |
| Phase 3: FR-01 & FR-02 | 10 | 1.5 天 | 4 个 [P] 任务 |
| Phase 4: FR-03, FR-04, FR-05 | 31 | 5 天 | 27 个 [P] 任务 |
| Phase 5: FR-06 | 7 | 2 天 | 3 个 [P] 任务 |
| Phase 6: FR-07 & FR-08 | 11 | 2 天 | 7 个 [P] 任务 |
| Phase 7: 集成与优化 | 10 | 3 天 | 5 个 [P] 任务 |
| Phase 8: 文档与发布 | 9 | 1 天 | 5 个 [P] 任务 |
| **总计** | **87** | **16 天** | **54 个 [P] 任务** |

**预计完成时间**:
- 串行执行：16 天
- 并行执行（50% 并行度）：8-10 天
- 符合计划目标：15 天（留有缓冲）

---

## MVP 快速通道

如果需要快速交付 MVP（只包含 FR-01 到 FR-05），执行以下任务：

**关键路径**（16 个任务）:
1. T001-T005: Phase 1（项目设置）
2. T006-T009: Phase 2（基础设施）
3. T010-T014: FR-01（目录结构）
4. T015-T019: FR-02（配置和 AI 检测）
5. T020-T023: FR-03（统一格式）
6. T024-T034: FR-04（中文模板，可并行）
7. T046-T050: FR-05（双语支持）

**预计 MVP 时间**: 8 天（并行执行）

---

## 格式验证

✅ **所有任务遵循 checklist 格式**:
- ✅ 以 `- [ ]` 开头（复选框）
- ✅ 包含任务 ID（T001-T087）
- ✅ 包含 [P] 标记（54 个可并行任务）
- ✅ 包含功能标签（FR-01 到 FR-08）
- ✅ 包含明确的文件路径

✅ **组织结构符合要求**:
- ✅ 按 Phase 组织（8 个阶段）
- ✅ 每个功能需求独立验收
- ✅ 依赖关系清晰
- ✅ 并行执行示例明确

---

**任务列表版本**: 1.0.0
**创建日期**: 2025-01-04
**状态**: ✅ 就绪，可执行
