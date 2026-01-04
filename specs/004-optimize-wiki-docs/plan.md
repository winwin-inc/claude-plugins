# 实施计划：优化 Wiki 文档结构和模板

**功能编号**: 004
**功能名称**: optimize-wiki-docs
**创建日期**: 2025-01-04
**最后更新**: 2025-01-04（架构澄清后重写）
**状态**: 草稿
**版本**: 2.0.0

---

## 技术上下文

### 架构边界（基于澄清会话）

**关键决策**（Session 2025-01-04 澄清）:
- **Python 包职责**: 安装 Claude Code 命令、提供模板、配置验证、迁移工具
- **Claude Code 命令职责**: 文档生成逻辑（AI 分析、内容生成、链接插入）
- **职责分离**: 避免重复，Python 包快速安装（<5秒），文档生成由 AI 处理

### 现有系统

**当前实现**:
- Python 包：`wiki-generator` CLI 工具（位于 `wiki_generator/cli.py`）
- 安装机制：通过 `uv tool install wiki-generator` 安装
- 模板目录：`wiki_generator/.claude/templates/`（6 个模板）
- 配置文件：`.claude/wiki-config.json`
- 输出目录：`docs/`（扁平结构）

**技术栈**:
- 语言：Python 3.11+
- CLI 框架：Click
- 包管理：uv / pip
- 构建工具：hatchling

### 待实现功能

**Python 包职责**（明确范围）:
1. **安装 Claude Code 命令**：复制 `.claude/commands/wiki-generate.md` 到用户项目
2. **提供默认模板**：22 个模板文件（中英各 11 个）作为 `.claude/templates/` 分发
3. **配置验证**：JSON Schema 验证工具（`--validate`）
4. **初始化工具**：创建配置文件和目录结构（`--init`）
5. **迁移工具**：配置格式迁移（`--migrate`）

**Claude Code 命令职责**（不在本实施范围内）:
- AI 分析代码库
- 根据模板生成文档内容
- 生成交叉引用链接
- 实现条件文档检测

### 技术决策需求

基于新的职责划分，需要决策：
- **模板格式**: 如何定义模板结构以便 Claude Code 理解？
- **配置 Schema**: 如何验证配置文件？
- **安装流程**: 如何复制文件到用户项目？
- **迁移策略**: 如何处理旧配置？

### 集成点

- **Python 包 CLI**：`wiki-generator --init`, `--validate`, `--migrate`
- **Claude Code 命令**：`/wiki-generate`（读取配置和模板，生成文档）
- **配置系统**：`.claude/wiki-config.json`（共享）
- **模板系统**：`.claude/templates/`（共享）

### 依赖项

- **参考项目**：`/home/yewenbin/work/tools/dingtalk-notable-connect/.qoder/repowiki`
- **现有模板**：`wiki_generator/.claude/templates/*.md.template`
- **配置文件**：`.claude/wiki-config.json`
- **JSON Schema**: `jsonschema` 库用于验证

---

## 宪章合规检查

### 核心原则评估

| 原则 | 评估 | 说明 |
|------|------|------|
| 中文优先 | ✅ Compliant | 所有交互、注释、文档使用简体中文 |
| 代码优先 | ✅ Compliant | 本功能是元项目工具，只为其他项目生成文档 |
| 工具定位 | ✅ Compliant | 专注于工具化（安装、验证、迁移） |
| 命名一致性 | ✅ Compliant | 使用 `wiki-generator` 包名，命令为 `/wiki-generate` |
| 文档质量 | ✅ Compliant | 模板质量分数 ≥80 分，包含示例和格式规范 |
| 增量更新 | ⚠️ N/A | 本功能不涉及文档更新（由 Claude Code 命令处理） |
| AI 辅助 | ✅ Compliant | Python 包提供工具，AI 生成由 Claude Code 处理 |
| 性能预期 | ✅ Compliant | Python 包安装 < 5秒，文档生成性能由 Claude Code 保证 |

### ✅ 合规总结

所有适用原则均合规。职责清晰分离，Python 包专注于工具化，文档生成由 Claude Code AI 处理。

---

## Phase 0: 研究与技术决策

### 研究任务

#### R-01: 模板格式定义
**问题**: 如何定义模板格式以便 Claude Code 理解和使用？

**研究内容**:
1. Claude Code 对 Markdown 模板的理解方式
2. 模板变量语法设计（`${variable}` vs `{{variable}}` vs `{variable}`）
3. 模板结构约定（章节标题、变量位置）
4. 参考项目的模板结构提取

**决策**:
- **格式**: 标准 Markdown + 变量占位符
- **变量语法**: `{variable_name}` （简单、清晰、Claude 易理解）
- **结构约定**:
  ```markdown
  # {title}

  <cite>
  **本文档中引用的文件**
  {cite_files}
  </cite>

  ## 目录
  {toc}

  ## {section1_title}
  {section1_content}

  **Section sources**
  {section1_sources}
  ```
- **Claude 提示**: 在模板顶部添加注释，指导 Claude 如何填充变量

#### R-02: 配置文件 Schema 设计
**问题**: 如何设计配置文件 Schema 以支持验证？

**研究内容**:
1. JSON Schema Draft 7 规范
2. 配置文件结构（参考现有配置）
3. 验证库选择（jsonschema vs pydantic）
4. 错误消息设计

**决策**:
- **Schema**: JSON Schema Draft 7
- **验证库**: `jsonschema`（轻量级，无额外依赖）
- **配置结构**:
  ```json
  {
    "output_dir": "docs",
    "language": "zh",
    "structure_template": "reference",
    "include_sources": true,
    "generate_toc": true,
    "sections": {
      "required": ["quickstart", "overview", ...],
      "optional": ["datamodel", "corefeatures"]
    }
  }
  ```
- **错误消息**: 中文错误消息，指出具体字段和期望值

#### R-03: 文件安装机制
**问题**: 如何将 `.claude/` 目录复制到用户项目？

**研究内容**:
1. Python 包数据文件打包（`package_data` vs `data_files`）
2. Click 命令的文件复制逻辑
3. 路径处理（`pathlib`）
4. 权限处理

**决策**:
- **打包方式**: 使用 `package_data` 在 `wiki_generator/.claude/`
- **复制逻辑**:
  ```python
  def install_claude_files(target_dir: Path):
      source = Path(__file__).parent / ".claude"
      target = target_dir / ".claude"
      if target.exists():
          confirm_overwrite()
      shutil.copytree(source, target, dirs_exist_ok=True)
  ```
- **路径处理**: 使用 `pathlib.Path`，跨平台兼容
- **权限**: 保持源文件权限，使用 `shutil.copy2`

#### R-04: 配置验证实现
**问题**: 如何实现配置文件验证？

**研究内容**:
1. `jsonschema` 库的使用方法
2. 自定义错误消息
3. CLI 集成（Click）
4. 验证报告格式

**决策**:
- **实现**:
  ```python
  from jsonschema import validate, ValidationError

  def validate_config(config_path: Path) -> ValidationResult:
      schema = load_schema("wiki-config-schema.json")
      config = json.loads(config_path.read_text())
      try:
          validate(instance=config, schema=schema)
          return ValidationResult(is_valid=True, errors=[])
      except ValidationError as e:
          return ValidationResult(
              is_valid=False,
              errors=[format_error_chinese(e)]
          )
  ```
- **CLI 集成**:
  ```bash
  wiki-generator --validate          # 验证当前目录配置
  wiki-generator --init --validate   # 初始化后验证
  ```

#### R-05: 迁移工具实现
**问题**: 如何实现配置迁移工具？

**研究内容**:
1. 旧配置格式识别
2. 迁移规则定义
3. 备份机制
4. 迁移报告生成

**决策**:
- **旧配置检测**: 检查缺少必需字段或版本号
- **迁移规则**:
  ```python
  MIGRATION_RULES = {
      "1.0": {
          "add_fields": ["language", "structure_template"],
          "rename_fields": {"lang": "language"},
          "remove_fields": ["deprecated_field"]
      }
  }
  ```
- **备份**: 自动备份为 `.claude/wiki-config.json.backup`
- **报告**: 生成 `.claude/migration-report.md`

#### R-06: 模板分发策略
**问题**: 22 个模板文件如何分发和更新？

**研究内容**:
1. 模板文件组织（`templates/zh/`, `templates/en/`）
2. 版本管理（模板版本号）
3. 用户自定义模板的保护
4. 模板更新机制

**决策**:
- **目录结构**:
  ```
  wiki_generator/.claude/
  ├── templates/
  │   ├── zh/
  │   │   ├── quickstart.md.template
  │   │   ├── overview.md.template
  │   │   └── ...
  │   └── en/
  │       ├── quickstart.md.template
  │       └── ...
  ├── schema/
  │   └── wiki-config-schema.json
  └── README.md
  ```
- **版本管理**: 在 `--init` 时记录模板版本到 `.claude/.template-version`
- **自定义保护**: 检测用户修改，更新时提示
- **更新机制**: `wiki-generator --update-templates`（可选功能）

---

## Phase 1: 设计与合约

### 数据模型

#### 实体：WikiConfig（配置文件）

```python
from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum

class Language(str, Enum):
    ZH = "zh"
    EN = "en"
    BOTH = "both"

class StructureTemplate(str, Enum):
    REFERENCE = "reference"
    SIMPLE = "simple"
    CUSTOM = "custom"

@dataclass
class SectionConfig:
    required: List[str]
    optional: List[str]

@dataclass
class WikiConfig:
    output_dir: str = "docs"
    language: Language = Language.ZH
    structure_template: StructureTemplate = StructureTemplate.REFERENCE
    include_sources: bool = True
    generate_toc: bool = True
    sections: Optional[SectionConfig] = None
```

#### 实体：TemplateManifest（模板清单）

```python
@dataclass
class TemplateInfo:
    name: str
    language: str
    path: str
    version: str

@dataclass
class TemplateManifest:
    templates: List[TemplateInfo]
    version: str
    installed_date: str
```

#### 实体：ValidationResult（验证结果）

```python
@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
```

#### 实体：MigrationResult（迁移结果）

```python
@dataclass
class MigrationResult:
    success: bool
    backup_path: Optional[str]
    changes: List[str]
    errors: List[str]
```

### API 契约

#### CLI 命令接口

**命令**: `wiki-generator`

**子命令**:
1. `--init` - 初始化项目配置
2. `--validate` - 验证配置文件
3. `--migrate` - 迁移旧配置
4. `--version` - 显示版本信息

#### 输入契约：配置文件

**文件**: `.claude/wiki-config.json`

**Schema**: `wiki-config-schema.json`

#### 输出契约：安装的文件结构

**目标目录**: 用户的 `.claude/`

**结构**:
```
.claude/
├── commands/
│   └── wiki-generate.md         # Claude Code 命令
├── templates/
│   ├── zh/                      # 中文模板
│   │   ├── quickstart.md.template
│   │   ├── overview.md.template
│   │   └── ... (11 个)
│   └── en/                      # 英文模板
│       ├── quickstart.md.template
│       └── ... (11 个)
├── schema/
│   └── wiki-config-schema.json  # JSON Schema
├── wiki-config.json             # 配置文件（--init 创建）
└── .template-version            # 模板版本号
```

---

## Phase 2: 任务分解

### 阶段划分

#### Phase 1: 模板创建（3 天）

**任务**:
1. 创建中文模板（11 个）
   - `templates/zh/quickstart.md.template`
   - `templates/zh/overview.md.template`
   - `templates/zh/techstack.md.template`
   - `templates/zh/architecture.md.template`
   - `templates/zh/datamodel.md.template`
   - `templates/zh/corefeatures.md.template`
   - `templates/zh/development.md.template`
   - `templates/zh/deployment.md.template`
   - `templates/zh/testing.md.template`
   - `templates/zh/troubleshooting.md.template`
   - `templates/zh/security.md.template`

2. 创建英文模板（11 个）
   - 对应的 `templates/en/*.template`

3. 实现统一的页头结构（`<cite>`、目录、Section sources）
4. 添加变量占位符（`{variable}`）

**依赖**: 无

**输出**:
- 22 个模板文件
- 模板格式规范文档

#### Phase 2: 配置系统（2 天）

**任务**:
1. 设计配置文件 Schema
2. 创建 `wiki-config-schema.json`
3. 实现配置验证模块
4. 实现配置初始化（`--init`）

**依赖**: Phase 1（模板）

**输出**:
- JSON Schema 文件
- 配置验证模块
- 初始化命令

#### Phase 3: 安装和迁移（2 天）

**任务**:
1. 实现文件安装逻辑（复制 `.claude/` 到用户项目）
2. 实现迁移工具（`--migrate`）
3. 实现版本管理
4. 编写安装和迁移文档

**依赖**: Phase 2（配置）

**输出**:
- 安装模块
- 迁移工具
- 用户文档

#### Phase 4: CLI 集成（1 天）

**任务**:
1. 实现 `wiki-generator` CLI 命令
2. 集成所有子命令（`--init`, `--validate`, `--migrate`）
3. 添加错误处理和用户友好的消息
4. 编写 CLI 使用文档

**依赖**: Phase 1-3

**输出**:
- 完整的 CLI 工具
- 使用文档

#### Phase 5: 测试和文档（2 天）

**任务**:
1. 单元测试（所有模块）
2. 集成测试（安装、验证、迁移流程）
3. 用户文档
4. 发布准备

**依赖**: 所有前面的阶段

**输出**:
- 测试套件
- 用户文档
- 发布版本

---

## 里程碑与交付物

### M1: 模板创建完成（Day 3）
- ✅ 22 个模板文件（中英各 11 个）
- ✅ 模板格式规范
- ✅ 变量占位符定义

### M2: 配置系统完成（Day 5）
- ✅ JSON Schema 定义
- ✅ 配置验证工具
- ✅ 初始化命令

### M3: 安装和迁移完成（Day 7）
- ✅ 文件安装逻辑
- ✅ 迁移工具
- ✅ 版本管理

### M4: CLI 集成完成（Day 8）
- ✅ 完整的 CLI 工具
- ✅ 所有子命令
- ✅ 错误处理

### M5: 测试和发布完成（Day 10）
- ✅ 所有测试通过
- ✅ 文档完善
- ✅ 版本发布

---

## 实施计划版本

**版本**: 2.0.0（架构澄清后重写）
**创建日期**: 2025-01-04
**最后更新**: 2025-01-04
**负责人**: Repo Wiki Generator 项目团队

**状态**: ✅ Phase 0 完成，待执行 Phase 1-5

**总预计时间**: 10 个工作日（比原计划减少 5 天，因为职责更清晰）
