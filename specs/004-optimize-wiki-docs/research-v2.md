# 技术研究：优化 Wiki 文档结构和模板

**功能**: optimize-wiki-docs
**版本**: 2.0.0（架构澄清后）
**创建日期**: 2025-01-04

---

## 研究概述

本文档记录了基于架构澄清后的技术研究和决策。所有研究都聚焦于 Python 包的职责：安装、配置验证、迁移工具。

---

## R-01: 模板格式定义

### 问题描述

如何定义模板格式以便 Claude Code `/wiki-generate` 命令能够理解和使用？

### 研究过程

1. **Claude Code 对 Markdown 的理解**
   - Claude 可以理解标准 Markdown 格式
   - 可以识别变量占位符（如 `{variable}`）
   - 可以根据注释和结构理解上下文

2. **变量语法对比**
   - `${variable}`: Shell 风格，可能被误解
   - `{{variable}}`: Jinja2 风格，模板引擎特征明显
   - `{variable}`: 简单、清晰，Claude 易于理解

3. **参考项目模板结构**
   - 统一的页头结构（`<cite>`、目录）
   - Section sources 标记
   - 清晰的章节层次

### 技术决策

**选择的格式**: 标准 Markdown + `{variable}` 占位符

**模板结构**:
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

**Claude 指导注释**（在每个模板顶部）:
```markdown
<!--
Wiki 文档模板

使用说明：
1. {variable} 是需要替换的变量占位符
2. cite_files: 文件引用列表，格式为 "- [文件名](file://相对路径)"
3. toc: 目录索引，格式为 "1. [章节名](#锚点)"
4. section_sources: 章节来源，格式为 "- [文件名](file://路径#L行号)"
-->
```

### 实施建议

- 模板文件使用 `.md.template` 扩展名
- 模板顶部必须包含 Claude 指导注释
- 变量名使用小写和下划线（如 `section1_title`）
- 复杂变量使用嵌套结构（如 `sections[0].title`）

---

## R-02: 配置文件 Schema 设计

### 问题描述

如何设计配置文件 JSON Schema 以支持验证？

### 研究过程

1. **JSON Schema Draft 7 规范**
   - 标准的 JSON 验证语言
   - 广泛的工具支持
   - 清晰的错误消息

2. **验证库选择**
   - `jsonschema`: 轻量级，纯 Python，无额外依赖
   - `pydantic`: 功能强大，但有依赖
   - 自定义验证: 开发成本高

3. **配置文件结构分析**
   - 需要支持语言选择
   - 需要支持结构模板
   - 需要支持章节配置

### 技术决策

**Schema 版本**: JSON Schema Draft 7

**验证库**: `jsonschema`

**配置结构**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["language"],
  "properties": {
    "output_dir": {
      "type": "string",
      "default": "docs"
    },
    "language": {
      "type": "string",
      "enum": ["zh", "en", "both"],
      "default": "zh"
    },
    "structure_template": {
      "type": "string",
      "enum": ["reference", "simple", "custom"],
      "default": "reference"
    },
    "include_sources": {
      "type": "boolean",
      "default": true
    },
    "generate_toc": {
      "type": "boolean",
      "default": true
    },
    "sections": {
      "type": "object",
      "properties": {
        "required": {
          "type": "array",
          "items": {"type": "string"}
        },
        "optional": {
          "type": "array",
          "items": {"type": "string"}
        }
      }
    }
  }
}
```

### 实施建议

**验证器实现**:
```python
from jsonschema import validate, ValidationError
import json

def validate_config(config_path: Path) -> ValidationResult:
    """验证配置文件"""
    schema_path = Path(__file__).parent / "schema" / "wiki-config-schema.json"
    schema = json.loads(schema_path.read_text())

    try:
        config = json.loads(config_path.read_text())
        validate(instance=config, schema=schema)
        return ValidationResult(is_valid=True, errors=[], warnings=[])
    except FileNotFoundError:
        return ValidationResult(
            is_valid=False,
            errors=[f"配置文件不存在: {config_path}"],
            warnings=[]
        )
    except json.JSONDecodeError as e:
        return ValidationResult(
            is_valid=False,
            errors=[f"配置文件格式错误: {e.msg}"],
            warnings=[]
        )
    except ValidationError as e:
        field = " -> ".join(str(p) for p in e.path)
        return ValidationResult(
            is_valid=False,
            errors=[f"字段 '{field}': {e.message}"],
            warnings=[]
        )
```

**依赖添加**:
```toml
# pyproject.toml
[project.dependencies]
jsonschema = "^4.20"
```

---

## R-03: 文件安装机制

### 问题描述

如何将 `.claude/` 目录从 Python 包复制到用户项目？

### 研究过程

1. **Python 包数据文件打包**
   - `package_data`: 包含在包内，安装后可访问
   - `data_files`: 安装到系统目录
   - 选择：`package_data`（更适合工具包）

2. **文件复制逻辑**
   - `shutil.copytree()`: 递归复制目录
   - `pathlib.Path`: 现代路径处理
   - 权限保持：`shutil.copy2()`

3. **用户交互**
   - 检测已存在的 `.claude/` 目录
   - 提示用户确认覆盖
   - 支持强制覆盖选项

### 技术决策

**打包方式**: `package_data`

**pyproject.toml 配置**:
```toml
[tool.hatch.build.targets.wheel]
packages = ["wiki_generator"]

[tool.hatch.build]
include = [
  "wiki_generator/.claude/**/*",
  "wiki_generator/**/*.py",
]
```

**安装逻辑**:
```python
import shutil
from pathlib import Path
from typing import Optional

def install_claude_files(
    target_dir: Path,
    force: bool = False,
    verbose: bool = False
) -> InstallResult:
    """
    安装 .claude/ 目录到用户项目

    Args:
        target_dir: 用户项目根目录
        force: 强制覆盖已存在的文件
        verbose: 显示详细输出

    Returns:
        InstallResult: 安装结果
    """
    # 获取源目录
    source_dir = Path(__file__).parent / ".claude"
    if not source_dir.exists():
        return InstallResult(
            success=False,
            error=f"源目录不存在: {source_dir}"
        )

    # 目标目录
    target_claude_dir = target_dir / ".claude"

    # 检查是否已存在
    if target_claude_dir.exists():
        if not force:
            # 提示用户
            response = input(f".claude/ 目录已存在，是否覆盖？[y/N]: ")
            if response.lower() != 'y':
                return InstallResult(
                    success=False,
                    error="用户取消安装",
                    skipped=True
                )
        # 备份现有目录
        backup_dir = target_dir / ".claude.backup"
        shutil.move(str(target_claude_dir), str(backup_dir))
        if verbose:
            print(f"✅ 已备份现有目录到: {backup_dir}")

    # 复制文件
    try:
        shutil.copytree(
            source_dir,
            target_claude_dir,
            dirs_exist_ok=force,
            copy_function=shutil.copy2  # 保持元数据
        )
        return InstallResult(
            success=True,
            installed_files=list_files(target_claude_dir),
            message=f"✅ 成功安装到: {target_claude_dir}"
        )
    except Exception as e:
        return InstallResult(
            success=False,
            error=f"安装失败: {e}"
        )

def list_files(directory: Path) -> list[str]:
    """列出目录中的所有文件"""
    files = []
    for item in directory.rglob("*"):
        if item.is_file():
            files.append(str(item.relative_to(directory)))
    return files
```

### 实施建议

- 使用 `pathlib` 而不是 `os.path`（更现代）
- 实现备份机制避免数据丢失
- 支持干运行模式（`--dry-run`）
- 显示安装进度（使用 `rich` 或简单进度条）

---

## R-04: 配置验证实现

### 问题描述

如何实现用户友好的配置文件验证？

### 研究过程（已在 R-02 中涵盖）

详见 R-02 的技术决策和实施建议。

### CLI 集成

```python
import click
from pathlib import Path

@click.command()
@click.option(
    '--config',
    type=click.Path(exists=True),
    default='.claude/wiki-config.json',
    help='配置文件路径'
)
def validate(config):
    """验证配置文件"""
    config_path = Path(config)
    result = validate_config(config_path)

    if result.is_valid:
        click.echo("✅ 配置文件验证通过")
        if result.warnings:
            click.echo("\n⚠️  警告:")
            for warning in result.warnings:
                click.echo(f"  - {warning}")
    else:
        click.echo("❌ 配置文件验证失败", err=True)
        for error in result.errors:
            click.echo(f"  - {error}", err=True)
        raise click.Abort(1)
```

### 使用示例

```bash
# 验证默认配置
wiki-generator --validate

# 验证指定配置
wiki-generator --validate --config /path/to/config.json

# 初始化后自动验证
wiki-generator --init --validate
```

---

## R-05: 迁移工具实现

### 问题描述

如何实现配置文件从旧版本到新版本的迁移？

### 研究过程

1. **版本管理**
   - 在配置文件中添加 `$version` 字段
   - 记录配置格式版本号

2. **迁移规则**
   - 字段重命名
   - 字段添加
   - 字段删除
   - 值格式转换

3. **安全性**
   - 自动备份
   - 迁移前验证
   - 回滚支持

### 技术决策

**迁移规则定义**:
```python
MIGRATIONS = {
    "1.0": {  # 从版本 1.0 迁移到 2.0
        "add_fields": {
            "language": "zh",
            "structure_template": "reference"
        },
        "rename_fields": {
            "lang": "language",
            "output": "output_dir"
        },
        "remove_fields": ["deprecated_option"],
        "transform_fields": {
            "verbose": lambda x: True if x else False
        }
    }
}
```

**迁移实现**:
```python
def migrate_config(
    config_path: Path,
    target_version: str = "2.0",
    backup: bool = True
) -> MigrationResult:
    """
    迁移配置文件到目标版本

    Args:
        config_path: 配置文件路径
        target_version: 目标版本
        backup: 是否备份原文件

    Returns:
        MigrationResult: 迁移结果
    """
    # 读取配置
    config = json.loads(config_path.read_text())
    current_version = config.get("$version", "1.0")

    # 检查是否需要迁移
    if current_version == target_version:
        return MigrationResult(
            success=True,
            message=f"配置已是最新版本 {target_version}",
            changes=[]
        )

    # 备份
    if backup:
        backup_path = config_path.with_suffix('.json.backup')
        shutil.copy2(config_path, backup_path)

    # 执行迁移
    changes = []
    for version, rules in MIGRATIONS.items():
        if version >= current_version and version < target_version:
            # 添加字段
            for field, value in rules.get("add_fields", {}).items():
                if field not in config:
                    config[field] = value
                    changes.append(f"添加字段: {field} = {value}")

            # 重命名字段
            for old_name, new_name in rules.get("rename_fields", {}).items():
                if old_name in config:
                    config[new_name] = config.pop(old_name)
                    changes.append(f"重命名字段: {old_name} -> {new_name}")

            # 删除字段
            for field in rules.get("remove_fields", []):
                if field in config:
                    del config[field]
                    changes.append(f"删除字段: {field}")

            # 转换字段
            for field, transform in rules.get("transform_fields", {}).items():
                if field in config:
                    old_value = config[field]
                    config[field] = transform(old_value)
                    changes.append(f"转换字段: {field} ({old_value} -> {config[field]})")

    # 更新版本号
    config["$version"] = target_version
    changes.append(f"更新版本: {current_version} -> {target_version}")

    # 写回文件
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False))

    return MigrationResult(
        success=True,
        changes=changes,
        backup_path=str(backup_path) if backup else None,
        message=f"✅ 成功迁移到版本 {target_version}"
    )
```

### CLI 集成

```python
@click.command()
@click.option('--backup/--no-backup', default=True, help='是否备份原文件')
def migrate(backup):
    """迁移配置文件到最新版本"""
    config_path = Path('.claude/wiki-config.json')

    if not config_path.exists():
        click.echo("❌ 配置文件不存在", err=True)
        raise click.Abort(1)

    result = migrate_config(config_path, backup=backup)

    if result.success:
        click.echo(result.message)
        if result.changes:
            click.echo("\n变更:")
            for change in result.changes:
                click.echo(f"  - {change}")
        if result.backup_path:
            click.echo(f"\n备份: {result.backup_path}")
    else:
        click.echo(f"❌ 迁移失败: {result.error}", err=True)
        raise click.Abort(1)
```

---

## R-06: 模板分发策略

### 问题描述

22 个模板文件如何打包、分发和更新？

### 研究过程

1. **目录结构**
   - 按语言分类（`templates/zh/`, `templates/en/`）
   - 每个语言 11 个模板
   - Schema 文件单独目录

2. **版本管理**
   - 记录模板版本号
   - 检测用户修改
   - 支持增量更新

3. **更新机制**
   - 检测新版本
   - 保留用户自定义
   - 合并冲突处理

### 技术决策

**目录结构**:
```
wiki_generator/.claude/
├── templates/
│   ├── zh/
│   │   ├── quickstart.md.template
│   │   ├── overview.md.template
│   │   ├── techstack.md.template
│   │   ├── architecture.md.template
│   │   ├── datamodel.md.template
│   │   ├── corefeatures.md.template
│   │   ├── development.md.template
│   │   ├── deployment.md.template
│   │   ├── testing.md.template
│   │   ├── troubleshooting.md.template
│   │   └── security.md.template
│   └── en/
│       ├── quickstart.md.template
│       ├── overview.md.template
│       ├── techstack.md.template
│       ├── architecture.md.template
│       ├── datamodel.md.template
│       ├── corefeatures.md.template
│       ├── development.md.template
│       ├── deployment.md.template
│       ├── testing.md.template
│       ├── troubleshooting.md.template
│       └── security.md.template
├── schema/
│   └── wiki-config-schema.json
├── commands/
│   └── wiki-generate.md
└── README.md
```

**版本管理**:
```python
TEMPLATE_VERSION = "2.0.0"

def get_template_version() -> str:
    """获取当前模板版本"""
    return TEMPLATE_VERSION

def record_template_version(target_dir: Path):
    """记录安装的模板版本"""
    version_file = target_dir / ".claude" / ".template-version"
    version_file.write_text(get_template_version())

def get_installed_version(target_dir: Path) -> Optional[str]:
    """获取已安装的模板版本"""
    version_file = target_dir / ".claude" / ".template-version"
    if version_file.exists():
        return version_file.read_text().strip()
    return None
```

**更新检测**:
```python
def check_template_updates(target_dir: Path) -> UpdateStatus:
    """检查模板更新"""
    installed_version = get_installed_version(target_dir)
    current_version = get_template_version()

    if installed_version is None:
        return UpdateStatus(
            available=True,
            current_version=None,
            latest_version=current_version,
            message="未检测到已安装的模板"
        )

    if installed_version != current_version:
        return UpdateStatus(
            available=True,
            current_version=installed_version,
            latest_version=current_version,
            message=f"有新版本可用: {installed_version} -> {current_version}"
        )

    return UpdateStatus(
        available=False,
        current_version=installed_version,
        latest_version=current_version,
        message="模板已是最新版本"
    )
```

**用户修改检测**:
```python
def detect_user_modifications(target_dir: Path) -> List[str]:
    """检测用户修改的模板"""
    templates_dir = target_dir / ".claude" / "templates"
    modified = []

    # 计算模板文件的哈希值
    for template_file in templates_dir.rglob("*.template"):
        # 对比默认内容和当前内容
        # （实际实现需要存储默认哈希值）
        pass

    return modified
```

### 实施建议

1. **版本文件**: 使用 `.template-version` 记录版本
2. **哈希验证**: 计算模板文件哈希值检测修改
3. **更新策略**:
   - 未修改的文件：直接覆盖
   - 已修改的文件：提示用户，保留旧版本为 `.old`
4. **更新命令**: `wiki-generator --update-templates`（可选）

---

## 总结

### 关键技术决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 模板格式 | Markdown + `{variable}` | Claude 易于理解，简单清晰 |
| 配置验证 | `jsonschema` | 轻量级，无额外依赖 |
| 文件安装 | `shutil.copytree` + `pathlib` | 标准库，跨平台兼容 |
| 迁移策略 | 版本化迁移规则 | 安全，可回滚 |
| 模板分发 | `package_data` + 版本管理 | 标准打包方式 |

### 依赖添加

```toml
[project.dependencies]
jsonschema = "^4.20"
```

### 性能目标

- 配置验证: < 1 秒
- 文件安装: < 3 秒（22 个模板文件）
- 配置迁移: < 2 秒

---

**研究版本**: 2.0.0
**创建日期**: 2025-01-04
**状态**: ✅ 所有研究完成，决策明确
