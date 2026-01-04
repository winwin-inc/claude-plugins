# 实施计划：优化 Wiki 文档结构和模板

**功能编号**: 004
**功能名称**: optimize-wiki-docs
**创建日期**: 2025-01-04
**状态**: 草稿
**版本**: 1.0.0

---

## 技术上下文

### 现有系统

**当前实现**:
- CLI 工具：`wiki-generator` 命令（位于 `wiki_generator/cli.py`）
- 模板目录：`wiki_generator/.claude/templates/`（6 个模板）
- 配置文件：`.claude/wiki-config.json`
- 输出目录：`docs/`（扁平结构）

**技术栈**:
- 语言：Python 3.8+
- CLI 框架：Click
- 包管理：uv / pip
- 构建工具：hatchling

### 待实现功能

**核心需求**（来自 spec.md）:
1. **分层目录结构**：`docs/{zh|en}/content/{00-文档名.md}`
2. **统一文档格式**：`<cite>`、目录、Section sources
3. **11 种文档类型**：快速开始、项目概述、技术栈、架构、数据模型、核心功能、开发指南、部署指南、测试策略、故障排除、安全考虑
4. **中英文双语**：两套模板（`templates/zh/` 和 `templates/en/`）
5. **交叉引用**：自动生成文档间链接
6. **配置驱动**：语言、结构模板、条件文档
7. **AI 自动检测**：判断条件文档生成
8. **迁移支持**：破坏性变更，提供迁移工具

### 技术决策需求

- **目录生成逻辑**：如何创建分层目录结构？
- **模板变量系统**：如何支持变量替换？
- **链接生成算法**：如何识别和生成交叉引用？
- **AI 检测逻辑**：如何分析代码库判断条件文档？
- **配置解析**：如何验证和处理配置文件？
- **性能优化**：如何满足分级性能目标（<15/30/90 秒）？

### 集成点

- **现有 CLI**：需要扩展 `cli.py` 支持新模板和结构
- **配置系统**：扩展现有 `wiki-config.json` schema
- **模板系统**：从 6 个模板扩展到 22 个（中英各 11 个）
- **输出路径**：从 `docs/` 改为 `docs/{zh|en}/content/`

### 依赖项

- **参考项目**：`/home/yewenbin/work/tools/dingtalk-notable-connect/.qoder/repowiki`
- **现有模板**：`wiki_generator/.claude/templates/*.template`
- **配置文件**：`.claude/wiki-config.json`
- **CLI 入口**：`wiki_generator/cli:cli`

---

## 宪章合规检查

### 核心原则评估

| 原则 | 评估 | 说明 |
|------|------|------|
| 中文优先 | ✅ Compliant | 所有交互、注释、文档使用简体中文 |
| 代码优先 | ✅ Compliant | 本功能是元项目工具，为其他项目生成文档 |
| 工具定位 | ✅ Compliant | 专注于工具化，生成高质量文档 |
| 命令一致性 | ✅ Compliant | 使用 `/wiki.*` 格式（已有） |
| 文档质量 | ✅ Compliant | 质量分数 ≥80 分，包含示例和图表 |
| 增量更新 | ⚠️ Partial | 完全覆盖策略与"保留手动编辑"冲突 |
| AI 辅助 | ✅ Compliant | AI 生成，用户验证 |
| 性能预期 | ✅ Compliant | 满足分级性能目标 |

### ⚠️ 冲突与例外

**冲突项**: **原则 6（增量更新原则）**
- **原则要求**: "更新时必须保留手动编辑的内容"
- **功能澄清**: "文档覆盖策略：完全覆盖，不保留手动修改"
- **冲突原因**: 用户选择了完全覆盖策略（澄清问题 Q2: Option B）

**理由**:
- 根据澄清会话记录，用户明确选择了"完全覆盖策略"
- 适用场景是"文档完全由 AI 生成和管理"的项目
- 用户可以通过其他方式（分支、复制）保留手动编辑
- 这符合"代码优先原则"：AI 生成的文档不是手动维护的

**批准**: ✅ **批准此例外**
- 批准理由：用户明确需求，有明确的适用场景和用户责任说明
- 缓解措施：在文档中明确说明覆盖策略，提醒用户如需保留手动编辑应使用其他方式

---

## Phase 0: 研究与技术决策

### 研究任务

#### R-01: 分层目录结构生成逻辑
**问题**: 如何实现 `docs/{zh|en}/content/{00-文档名.md}` 结构？

**研究内容**:
1. Python 标准库 `pathlib` 创建目录的最佳实践
2. 数字前缀排序实现（00-99）
3. 文档命名规范（中文文件名处理）
4. 目录存在性检查和冲突处理

**决策**:
- 使用 `pathlib.Path.mkdir(parents=True, exist_ok=True)`
- 使用 `str(i).zfill(2)` 生成数字前缀
- 中文文件名直接使用（现代文件系统支持）
- 检测冲突并提示用户

#### R-02: 模板变量系统设计
**问题**: 如何实现模板变量替换？

**研究内容**:
1. Jinja2 vs string.Template vs 自制替换
2. 变量语法设计（`{variable}` vs `{{variable}}`）
3. 嵌套变量和条件逻辑
4. 性能对比（小规模模板）

**决策**:
- **选择**: Python 标准库 `string.Template`
- **语法**: `{variable}` （与规范一致）
- **性能**: 对小规模模板足够快，无额外依赖
- **扩展**: 自定义 `safe_substitute()` 方法处理缺失变量

#### R-03: 交叉引用链接生成算法
**问题**: 如何自动识别和生成文档间链接？

**研究内容**:
1. 文档内容解析（正则 vs NLP）
2. 模块名识别模式
3. 相对路径计算
4. Markdown 链接格式

**决策**:
- **识别方法**: 基于正则表达式的模式匹配
  - 模块引用：`/(?:模块|module|功能)[：:]\s*([^\n]+)/`
  - 文件引用：`/`([a-zA-Z0-9_./-]+\.(py|js|ts|md))`/
  - 函数引用：`/`([a-zA-Z_][a-zA-Z0-9_]*\(\))`/
- **路径计算**: 使用 `pathlib.Path.relative_to()` 计算相对路径
- **链接格式**: Markdown 标准链接语法 `[文本](路径)`
- **验证**: 生成后检查文件存在性

#### R-04: AI 检测条件文档逻辑
**问题**: 如何自动判断需要哪些条件文档？

**研究内容**:
1. 代码库扫描策略
2. 技术栈特征识别
3. 规则引擎设计
4. 误报控制

**决策**:
- **检测方法**: 基于关键词和导入语句的模式匹配
- **规则引擎**: 简单的 Python 字典规则系统
  ```python
  conditions = {
      "datamodel": ["sqlalchemy", "django.db", "peewee", " pymongo"],
      "database": ["psycopg2", "pymongo", "mysql"],
      "api": ["fastapi", "flask", "django.rest", "graphql"],
      "testing": ["pytest", "unittest", "nose"],
      "async": ["asyncio", "aiohttp", "trio"]
  }
  ```
- **扫描范围**: `requirements.txt`, `pyproject.toml`, 代码导入语句
- **阈值**: 至少匹配 1 个关键词或 2 个相关导入

#### R-05: 配置文件 Schema 设计
**问题**: 如何验证和处理配置文件？

**研究内容**:
1. JSON Schema 规范
2. 验证库选择（jsonschema vs pydantic）
3. 错误消息设计
4. 默认值处理

**决策**:
- **Schema**: 使用 JSON Schema Draft 7
- **验证库**: `jsonschema` Python 库（轻量级，无额外依赖）
- **错误消息**: 中文错误消息，指出具体字段和期望值
- **默认值**: 在规范中定义，配置缺失时使用默认值
  ```json
  {
    "output_dir": "docs",
    "language": "zh",
    "structure_template": "reference",
    "include_sources": true,
    "generate_toc": true
  }
  ```

#### R-06: 性能优化策略
**问题**: 如何满足分级性能目标？

**研究内容**:
1. 文件 I/O 批处理
2. 模板渲染缓存
3. 并行处理可能性
4. 大型项目优化

**决策**:
- **I/O 优化**: 批量读取文件，减少系统调用
- **缓存**: 缓存模板编译结果（`string.Template`）
- **并行**: 暂不使用（增加复杂度，单线程已满足性能目标）
- **大型项目**: 分批处理（每批 50 个文件），显示进度条

---

## Phase 1: 设计与契约

### 数据模型

#### 实体：文档配置（WikiConfig）

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
    name: str
    template: str
    order: int
    subsections: Optional[List[str]] = None

@dataclass
class FormattingConfig:
    code_block_syntax: bool = True
    line_numbers: bool = True
    section_sources: bool = True

@dataclass
class LinksConfig:
    auto_generate: bool = True
    validate: bool = True

@dataclass
class WikiConfig:
    output_dir: str = "docs"
    language: Language = Language.ZH
    structure_template: StructureTemplate = StructureTemplate.REFERENCE
    required_sections: List[str] = None
    optional_sections: List[str] = None
    custom_structure: List[SectionConfig] = None
    include_sources: bool = True
    generate_toc: bool = True
    formatting: FormattingConfig = None
    links: LinksConfig = None
```

#### 实体：文档元数据（DocumentMetadata）

```python
@dataclass
class DocumentMetadata:
    title: str
    template_name: str
    language: Language
    order: int
    cite_files: List[str]
    sections: List[Dict[str, str]]
    section_sources: Dict[str, List[str]]
    output_path: Path
```

#### 实体：项目分析结果（ProjectAnalysis）

```python
@dataclass
class ProjectInfo:
    name: str
    type: str  # "web", "cli", "lib"
    language: str  # "python", "javascript", etc.
    file_count: int
    line_count: int
    scale: str  # "small", "medium", "large"

@dataclass
class ConditionDocs:
    datamodel: bool = False
    database: bool = False
    api: bool = False
    testing: bool = False
    async_features: bool = False
```

### API 契约

#### 输入契约：配置文件

**文件**: `.claude/wiki-config.json`

**Schema**: `contracts/wiki-config-schema.json`

```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["output_dir", "language"],
    "properties": {
        "output_dir": {
            "type": "string",
            "description": "文档输出目录"
        },
        "language": {
            "type": "string",
            "enum": ["zh", "en", "both"],
            "description": "文档语言"
        },
        "structure_template": {
            "type": "string",
            "enum": ["reference", "simple", "custom"],
            "description": "目录结构模板"
        },
        "sections": {
            "type": "object",
            "properties": {
                "required": {
                    "type": "array",
                    "items": { "type": "string" }
                },
                "optional": {
                    "type": "array",
                    "items": { "type": "string" }
                }
            }
        },
        "include_sources": {
            "type": "boolean",
            "description": "是否包含 Section sources"
        },
        "generate_toc": {
            "type": "boolean",
            "description": "是否生成目录索引"
        }
    }
}
```

#### 输出契约：文档结构

**目录结构**:
```
docs/
├── {language}/            # zh 或 en
│   └── content/
│       ├── 00-quickstart.md
│       ├── 01-overview.md
│       ├── 02-techstack.md
│       ├── 03-architecture/
│       │   └── system-design.md
│       ├── 04-datamodel/   # 条件文档
│       │   └── database-schema.md
│       └── ...
└── .wiki-meta.json        # 元数据（可选）
```

**文件格式**: Markdown (.md)

**必需元数据**:
- 文档标题（H1）
- `<cite>` 块：引用文件列表
- `## 目录`：目录索引
- Section sources：章节来源

### 快速开始（Quickstart）

#### 安装新模板

```bash
# 1. 确保在项目根目录
cd /path/to/your/project

# 2. 安装 wiki-generator 工具（如果尚未安装）
uv tool install wiki-generator

# 3. 创建配置文件
cat > .claude/wiki-config.json << EOF
{
  "output_dir": "docs",
  "language": "zh",
  "structure_template": "reference",
  "include_sources": true,
  "generate_toc": true
}
EOF

# 4. 生成文档
wiki-generator --full

# 5. 查看生成的文档
ls -lh docs/zh/content/
```

#### 增量更新文档

```bash
# 修改代码后
vim src/auth/login.py

# 更新对应文档
wiki-generator --update

# 查看变更报告
cat docs/.wiki-update-report.md
```

#### 迁移旧配置

```bash
# 运行迁移工具
wiki-generator --migrate

# 检查迁移报告
cat docs/.wiki-migration-report.md

# 验证新配置
cat .claude/wiki-config.json
```

---

## Phase 2: 任务分解

### 阶段划分

#### Phase 1: 模板开发（5 天）

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

3. 实现页头结构（`<cite>`、目录、Section sources）
4. 添加变量替换支持

**依赖**: 无

**输出**:
- 22 个模板文件
- 模板变量系统
- 单元测试

#### Phase 2: 目录结构逻辑（3 天）

**任务**:
1. 实现分层目录生成
   - `docs/{zh|en}/content/` 目录创建
   - 数字前缀排序（00-99）
2. 实现自定义结构配置
3. 实现 AI 检测条件文档
4. 配置文件解析和验证

**依赖**: Phase 1（模板）

**输出**:
- 目录生成模块
- 配置解析模块
- AI 检测模块
- 集成测试

#### Phase 3: 交叉引用（2 天）

**任务**:
1. 实现链接识别算法
2. 实现相对路径计算
3. 实现三种链接类型（文档、代码、锚点）
4. 链接验证工具

**依赖**: Phase 2（目录结构）

**输出**:
- 链接生成模块
- 链接验证工具
- 单元测试

#### Phase 4: 配置和兼容（2 天）

**任务**:
1. 实现配置文件解析
2. 实现迁移工具（`wiki-generator --migrate`）
3. 实现错误消息和迁移指引
4. 向后兼容性测试

**依赖**: Phase 1（模板）

**输出**:
- 配置解析模块
- 迁移工具
- 迁移指南文档
- 集成测试

#### Phase 5: 测试和优化（3 天）

**任务**:
1. 单元测试（所有模块）
2. 集成测试（端到端）
3. 性能测试（小型/中型/大型）
4. 用户验收测试
5. 文档完善

**依赖**: 所有前面的阶段

**输出**:
- 测试套件
- 性能报告
- 用户手册
- 发布版本

---

## 里程碑与交付物

### M1: 所有模板创建完成（Day 5）
- ✅ 22 个模板文件（中英各 11 个）
- ✅ 模板变量系统
- ✅ 单元测试通过

### M2: 目录结构生成工作（Day 8）
- ✅ 分层目录正确生成
- ✅ 配置解析正常
- ✅ AI 检测准确

### M3: 交叉引用功能完成（Day 10）
- ✅ 链接自动生成
- ✅ 三种链接类型支持
- ✅ 链接验证通过

### M4: 配置和迁移完成（Day 12）
- ✅ 配置文件支持
- ✅ 迁移工具可用
- ✅ 迁移指南清晰

### M5: 所有测试通过，发布（Day 15）
- ✅ 所有测试通过
- ✅ 性能目标达成
- ✅ 文档完善
- ✅ 版本发布

---

## 实施计划版本

**版本**: 1.0.0
**创建日期**: 2025-01-04
**最后更新**: 2025-01-04
**负责人**: Repo Wiki Generator 项目团队

**状态**: ✅ Phase 0-2 完成，待执行 Phase 3-5
