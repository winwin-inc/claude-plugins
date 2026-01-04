# API Contracts: Wiki 文档生成

**版本**: 1.0.0
**创建日期**: 2025-01-04
**功能**: [spec.md](spec.md)

---

## 1. 配置验证 API

### 1.1 验证配置文件

**接口**: `ConfigValidator.validate(config_path: Path) -> ValidationResult`

**描述**: 验证 `.claude/wiki-config.json` 配置文件是否符合 schema

**请求**:
```python
from pathlib import Path

config_path = Path(".claude/wiki-config.json")
validator = ConfigValidator()
result = validator.validate(config_path)
```

**响应**:
```python
@dataclass
class ValidationResult:
    is_valid: bool              # 是否通过验证
    errors: List[str]           # 错误列表
    warnings: List[str]         # 警告列表
    config: WikiConfig          # 解析后的配置对象
```

**错误示例**:
```json
{
  "is_valid": false,
  "errors": [
    "language: 必须是 'zh', 'en', 或 'both' 之一",
    "structure_template='custom' 时 sections 字段必需"
  ],
  "warnings": [
    "未指定 sections.optional，将使用默认值"
  ],
  "config": null
}
```

---

## 2. 项目分析 API

### 2.1 分析项目信息

**接口**: `ProjectAnalyzer.analyze(project_root: Path) -> ProjectInfo`

**描述**: 分析项目代码库，提取项目信息

**请求**:
```python
analyzer = ProjectAnalyzer(
    project_root=Path("/path/to/project"),
    exclude_patterns=["node_modules", "dist", ".git"]
)
project_info = analyzer.analyze()
```

**响应**:
```python
@dataclass
class ProjectInfo:
    name: str                  # "my-project"
    version: str               # "1.0.0"
    description: str           # "项目描述"
    language: str              # "Python"
    tech_stack: List[str]      # ["FastAPI", "SQLAlchemy", "PostgreSQL"]
    file_count: int            # 150
    line_count: int            # 15000
    project_type: str          # "web"
```

### 2.2 检测条件文档

**接口**: `ProjectAnalyzer.analyze_conditions() -> ConditionDocs`

**描述**: 根据项目特征判断需要哪些条件文档

**请求**:
```python
analyzer = ProjectAnalyzer(project_root=Path("/path/to/project"))
conditions = analyzer.analyze_conditions()
```

**响应**:
```python
@dataclass
class ConditionDocs:
    datamodel: bool            # True（检测到 SQLAlchemy）
    database: bool             # True（检测到 psycopg2）
    api: bool                  # True（检测到 FastAPI）
    ui: bool                   # False（未检测到前端代码）
    async_tasks: bool          # False（未检测到 Celery）
    auth: bool                 # True（检测到 login 模块）
```

**检测规则权重**:
- 关键词匹配: 1 分
- Import 语句: 2 分
- 文件名匹配: 3 分
- 阈值: ≥ 1 分

---

## 3. 文档结构生成 API

### 3.1 生成文档结构

**接口**: `StructureGenerator.generate(config: WikiConfig, project_info: ProjectInfo, conditions: ConditionDocs) -> DocumentStructure`

**描述**: 根据配置和项目信息生成文档目录结构

**请求**:
```python
generator = StructureGenerator()
structure = generator.generate(
    config=wiki_config,
    project_info=project_info,
    conditions=conditions
)
```

**响应**:
```python
@dataclass
class DocumentStructure:
    base_dir: str              # "docs"
    language_dirs: List[str]   # ["zh"]
    content_dir: str           # "content"
    documents: List[DocumentMetadata]
    modules: List[ModuleInfo]
```

**示例结构**:
```json
{
  "base_dir": "docs",
  "language_dirs": ["zh"],
  "content_dir": "content",
  "documents": [
    {
      "title": "快速开始",
      "file_name": "00-快速开始.md",
      "order": 0,
      "template": "quickstart",
      "path": "docs/zh/content/00-快速开始.md"
    }
  ],
  "modules": [
    {
      "name": "核心功能",
      "path": "docs/zh/content/核心功能",
      "documents": ["认证模块.md", "数据处理.md"]
    }
  ]
}
```

---

## 4. 模板渲染 API

### 4.1 渲染单个文档

**接口**: `TemplateRenderer.render(template_name: str, variables: Dict[str, Any]) -> str`

**描述**: 使用模板和变量生成 Markdown 文档

**请求**:
```python
renderer = TemplateRenderer(template_dir=Path(".claude/templates/zh"))

variables = {
    "project_name": "my-project",
    "version": "1.0.0",
    "cite_files": ["README.md", "src/main.py"],
    "sections": [
        {
            "title": "简介",
            "anchor": "简介",
            "content": "这是项目简介...",
            "sources": ["README.md#L1-L10"]
        }
    ]
}

doc_content = renderer.render("quickstart.md.template", variables)
```

**响应**:
```markdown
# 快速开始

<cite>
**本文档中引用的文件**
- [README.md](file://README.md)
- [src/main.py](file://src/main.py)
</cite>

## 目录
1. [简介](#简介)

## 简介
这是项目简介...

**Section sources**
- [README.md](file://README.md#L1-L10)
```

### 4.2 批量渲染文档

**接口**: `TemplateRenderer.render_batch(documents: List[DocumentMetadata]) -> Dict[str, str]`

**描述**: 批量渲染多个文档（性能优化）

**请求**:
```python
documents = [doc1, doc2, doc3, ...]
results = renderer.render_batch(documents, batch_size=50)
```

**响应**:
```python
{
  "docs/zh/content/00-快速开始.md": "# 快速开始\n...",
  "docs/zh/content/01-项目概述.md": "# 项目概述\n...",
  "docs/zh/content/02-技术栈与依赖.md": "# 技术栈与依赖\n..."
}
```

---

## 5. 链接生成 API

### 5.1 生成交叉引用链接

**接口**: `LinkGenerator.generate_links(document: str, structure: DocumentStructure) -> List[LinkReference]`

**描述**: 识别文档中的引用并生成链接

**请求**:
```python
generator = LinkGenerator()

doc_content = """
参见 [认证模块] 了解详情。
更多信息参考 [README.md](file://README.md)。
"""

links = generator.generate_links(
    document="docs/zh/content/01-项目概述.md",
    content=doc_content,
    structure=doc_structure
)
```

**响应**:
```python
[
    LinkReference(
        source_doc="docs/zh/content/01-项目概述.md",
        target_type="doc",
        target_path="docs/zh/content/核心功能/认证模块.md",
        link_text="认证模块",
        line_number=10
    ),
    LinkReference(
        source_doc="docs/zh/content/01-项目概述.md",
        target_type="code",
        target_path="README.md",
        link_text="README.md",
        line_number=11
    )
]
```

### 5.2 验证链接

**接口**: `LinkValidator.validate_links(links: List[LinkReference]) -> LinkValidationResult`

**描述**: 验证生成的链接是否有效

**请求**:
```python
validator = LinkValidator()
result = validator.validate_links(links)
```

**响应**:
```python
@dataclass
class LinkValidationResult:
    total_links: int           # 100
    valid_links: int           # 95
    invalid_links: List[str]   # ["docs/zh/content/缺失文档.md"]
    accuracy_rate: float       # 0.95
```

---

## 6. 文档写入 API

### 6.1 写入文档文件

**接口**: `DocumentWriter.write(structure: DocumentStructure, contents: Dict[str, str]) -> WriteResult`

**描述**: 将生成的文档内容写入文件系统

**请求**:
```python
writer = DocumentWriter()

contents = {
    "docs/zh/content/00-快速开始.md": "# 快速开始\n...",
    "docs/zh/content/01-项目概述.md": "# 项目概述\n..."
}

result = writer.write(structure, contents, overwrite=True)
```

**响应**:
```python
@dataclass
class WriteResult:
    success: bool              # True
    written_files: List[str]   # ["docs/zh/content/00-快速开始.md", ...]
    failed_files: List[str]    # []
    directories_created: List[str]  # ["docs/zh/content", ...]
    execution_time: float      # 12.5（秒）
```

---

## 7. 错误处理

### 7.1 错误响应格式

所有 API 错误遵循统一格式：

```python
@dataclass
class WikiGeneratorError(Exception):
    code: str                  # 错误代码
    message: str               # 错误消息
    details: Dict[str, Any]    # 详细信息
```

**错误代码**:
- `CONFIG_INVALID`: 配置文件无效
- `TEMPLATE_NOT_FOUND`: 模板文件不存在
- `PROJECT_ANALYSIS_FAILED`: 项目分析失败
- `LINK_GENERATION_FAILED`: 链接生成失败
- `FILE_WRITE_FAILED`: 文件写入失败

### 7.2 错误示例

```json
{
  "code": "TEMPLATE_NOT_FOUND",
  "message": "找不到模板文件",
  "details": {
    "template_name": "quickstart.md.template",
    "searched_paths": [
      ".claude/templates/zh/quickstart.md.template",
      ".claude/templates/en/quickstart.md.template"
    ]
  }
}
```

---

## 8. 性能要求

### 8.1 响应时间要求

根据 [spec.md](spec.md) 第 5.1 节：

| 项目规模 | 文件数 | 代码行数 | 目标时间 |
|---------|--------|---------|---------|
| 小型 | < 100 | < 10K | < 15 秒 |
| 中型 | 100-500 | 10K-50K | < 30 秒 |
| 大型 | > 500 | > 50K | < 90 秒 |

### 8.2 性能优化策略

- **批处理**: 使用 `render_batch()` 一次性处理多个文档
- **模板缓存**: 启用 `cache_templates=true` 避免重复读取
- **并发限制**: 当前使用单线程（`max_workers=1`），确保稳定性

---

## 9. 使用示例

### 9.1 完整流程

```python
from pathlib import Path
from wiki_generator import (
    ConfigValidator,
    ProjectAnalyzer,
    StructureGenerator,
    TemplateRenderer,
    LinkGenerator,
    DocumentWriter
)

# 1. 验证配置
validator = ConfigValidator()
config_result = validator.validate(Path(".claude/wiki-config.json"))
if not config_result.is_valid:
    print(f"配置错误: {config_result.errors}")
    exit(1)

# 2. 分析项目
analyzer = ProjectAnalyzer(Path("."))
project_info = analyzer.analyze()
conditions = analyzer.analyze_conditions()

# 3. 生成文档结构
structure_gen = StructureGenerator()
structure = structure_gen.generate(
    config=config_result.config,
    project_info=project_info,
    conditions=conditions
)

# 4. 渲染模板
renderer = TemplateRenderer()
contents = renderer.render_batch(structure.documents)

# 5. 生成链接
link_gen = LinkGenerator()
for doc_path, content in contents.items():
    links = link_gen.generate_links(doc_path, content, structure)
    updated_content = link_gen.insert_links(content, links)
    contents[doc_path] = updated_content

# 6. 写入文件
writer = DocumentWriter()
result = writer.write(structure, contents, overwrite=True)

print(f"✅ 成功生成 {len(result.written_files)} 个文档")
print(f"⏱️  执行时间: {result.execution_time:.2f} 秒")
```

---

## 10. 版本兼容性

### 10.1 API 版本策略

- 当前版本: `1.0.0`
- 破坏性变更: 通过主版本号标识（如 `2.0.0`）
- 向后兼容: 次版本号增加新功能（如 `1.1.0`）
- Bug 修复: 修订版本号增加（如 `1.0.1`）

### 10.2 迁移支持

由于采用破坏性变更策略（参考 [spec.md](spec.md) FR-08），提供以下迁移支持：

1. **配置迁移工具**: `migrate-config.py`
2. **迁移指南文档**: `MIGRATION.md`
3. **版本检测**: 自动检测旧配置并提供迁移指引

---

**状态**: 草稿 - 待审查
**下一步**: 实现各 API 接口
