# API 契约: Wiki Generator CLI 安装工具

**功能版本**: 1.0.0
**创建日期**: 2026-01-04
**接口类型**: Python CLI（内部函数）

---

## 核心函数契约

### 1. install_cli_files()

安装 Claude Code 命令文件到目标目录。

**函数签名**:
```python
def install_cli_files(
    target_dir: str = ".",
    force: bool = False,
    dry_run: bool = False,
    verbose: bool = False
) -> list[InstalledFile]:
    """安装 .claude/ 目录到目标目录

    Args:
        target_dir: 目标目录路径（默认: 当前目录）
        force: 强制覆盖已存在文件（默认: False）
        dry_run: 显示将要安装的文件，不实际复制（默认: False）
        verbose: 显示详细输出（默认: False）

    Returns:
        list[InstalledFile]: 已安装的文件列表

    Raises:
        PermissionError: 目标目录无写入权限
        OSError: 文件复制失败
        RollbackError: 回滚失败（严重错误）

    Side Effects:
        - 创建 .claude/ 目录和子目录
        - 复制命令和模板文件
        - 可能备份已存在的文件
        - 在 dry_run 模式下不修改文件系统
    """
```

**前置条件**:
- `target_dir` 必须是有效的目录路径
- 必须有 `target_dir` 的写入权限

**后置条件**:
- `.claude/commands/` 目录存在（除非 dry_run=True）
- 所有必需的文件已复制（除非 dry_run=True）
- 如果失败，已安装的文件已回滚

**异常处理**:
- **PermissionError**: 提前检查权限，在修改任何文件前抛出
- **OSError**: 捕获并记录错误，执行回滚，重新抛出
- **RollbackError**: 仅当回滚本身失败时抛出（严重情况）

**性能约束**:
- 复制 < 100 个文件
- 执行时间 < 5 秒（不包括 `uvx` 启动时间）

---

### 2. generate_config()

生成或验证 `wiki-config.json` 配置文件。

**函数签名**:
```python
def generate_config(
    target_dir: str = ".",
    overwrite: bool = False
) -> WikiConfig:
    """生成 wiki-config.json 配置文件

    Args:
        target_dir: 目标目录路径（默认: 当前目录）
        overwrite: 是否覆盖已存在的配置（默认: False）

    Returns:
        WikiConfig: 生成的配置对象

    Raises:
        ValueError: 配置文件已存在且 overwrite=False
        ValidationError: 现有配置文件格式无效

    Side Effects:
        - 创建 wiki-config.json 文件
        - 备份已存在的配置（如果 overwrite=True）
    """
```

**前置条件**:
- `target_dir` 必须是有效路径
- 如果 `wiki-config.json` 已存在，必须 `overwrite=True`

**后置条件**:
- `wiki-config.json` 文件存在且包含有效配置
- 配置包含 5 个必需字段

**默认配置**:
```python
default_config = {
    "output_dir": "docs",
    "exclude_patterns": ["node_modules", "dist", ".git"],
    "quality_threshold": 80,
    "diagrams_enabled": True,
    "diagrams_detail_level": "medium"
}
```

---

### 3. validate_config()

验证配置文件的格式和字段值。

**函数签名**:
```python
def validate_config(config_path: str) -> tuple[bool, list[ValidationError]]:
    """验证 wiki-config.json 配置文件

    Args:
        config_path: 配置文件路径

    Returns:
        tuple[bool, list[ValidationError]]: (是否有效, 错误列表)

    Side Effects:
        - 读取并解析 JSON 文件
        - 无副作用（只读操作）
    """
```

**验证规则**:
1. JSON 格式有效性
2. 必需字段存在性
3. 字段类型正确性
4. 枚举值有效性（`diagrams_detail_level`）
5. 数值范围有效性（`quality_threshold`）

**错误示例**:
```python
# 缺少必需字段
ValidationError(
    field="output_dir",
    message="缺少必需字段 'output_dir'",
    expected="string",
    actual=None
)

# 枚举值无效
ValidationError(
    field="diagrams_detail_level",
    message="diagrams_detail_level 必须是 'low', 'medium', 或 'high'",
    expected="low|medium|high",
    actual="invalid"
)

# 数值超出范围
ValidationError(
    field="quality_threshold",
    message="quality_threshold 必须在 0 到 100 之间",
    expected="0-100",
    actual=150
)
```

---

### 4. rollback_installation()

回滚已安装的文件。

**函数签名**:
```python
def rollback_installation(
    installed_files: list[InstalledFile],
    verbose: bool = False
) -> None:
    """回滚已安装的文件

    Args:
        installed_files: 已安装文件列表（从 install_cli_files 返回）
        verbose: 显示详细输出（默认: False）

    Raises:
        RollbackError: 回滚失败（部分文件无法删除）

    Side Effects:
        - 删除已安装的文件
        - 恢复备份文件（如果有）
    """
```

**回滚策略**:
1. 按相反顺序删除文件（先删除最后复制的）
2. 如果存在备份文件，先恢复备份再删除
3. 记录所有失败的回滚操作
4. 如果任何回滚失败，抛出 `RollbackError`（包含详细信息）

---

## 命令行接口

### 主命令: wiki-generator

**调用方式**:
```bash
uvx wiki-generator [OPTIONS]
```

**选项**:

| 选项 | 短选项 | 类型 | 默认值 | 说明 |
|------|--------|------|--------|------|
| `--force` | `-f` | flag | `false` | 强制覆盖已存在文件 |
| `--dry-run` | `-n` | flag | `false` | 显示将要安装的文件，不实际复制 |
| `--target-dir` | `-d` | string | `"."` | 目标安装目录 |
| `--verbose` | `-v` | flag | `false` | 显示详细输出 |
| `--version` | `-V` | flag | - | 显示版本信息 |
| `--help` | `-h` | flag | - | 显示帮助信息 |

**退出码**:
- `0`: 成功
- `1`: 一般错误（权限不足、文件冲突等）
- `2`: 回滚失败（严重错误）

---

## 使用示例

### 示例 1: 基本安装

```bash
# 安装到当前目录
uvx wiki-generator

# 预期输出
正在安装 .claude/ 目录...
✓ 创建 .claude/commands/
✓ 创建 .claude/templates/
✓ 生成 wiki-config.json

安装完成！
下一步: 运行 /wiki-overview 生成项目概览文档
```

### 示例 2: Dry-run 模式

```bash
# 查看将要安装的文件
uvx wiki-generator --dry-run

# 预期输出
将要安装的文件:
  .claude/commands/wiki-init.md
  .claude/commands/wiki-overview.md
  .claude/templates/overview.md.template
  ... (共 45 个文件)

使用 --force 选项强制覆盖已存在文件
```

### 示例 3: 强制覆盖

```bash
# 覆盖已存在文件
uvx wiki-generator --force

# 预期输出
警告: .claude/commands/wiki-init.md 已存在，将被覆盖
正在安装 .claude/ 目录...
✓ 覆盖 .claude/commands/wiki-init.md
✓ 创建 .claude/templates/
✓ 保留 wiki-config.json (已存在)

安装完成！
```

### 示例 4: Python API 使用

```python
from wiki_generator.installer import install_cli_files, generate_config

# 安装到自定义目录
installed_files = install_cli_files(
    target_dir="/path/to/project",
    force=True,
    verbose=True
)

print(f"已安装 {len(installed_files)} 个文件")

# 生成配置
config = generate_config(target_dir="/path/to/project", overwrite=True)
print(f"配置文件: output_dir={config.output_dir}")
```

---

## 错误处理

### 错误消息规范

所有用户可见的错误消息必须使用简体中文，格式清晰。

**示例**:

```python
# 权限不足
"错误: 目录 '/path/to/project' 无写入权限"
"提示: 请检查目录权限或使用 sudo 运行"

# 文件冲突
"错误: wiki-config.json 已存在"
"提示: 使用 --force 选项覆盖，或手动删除现有文件"

# 配置文件损坏
"错误: wiki-config.json 格式无效"
"详情: 第 5 行: 期望字符串，找到数字"
"提示: 配置文件已备份为 wiki-config.json.backup"

# 回滚失败
"严重错误: 回滚安装失败"
"详情: 无法删除 .claude/commands/wiki-init.md"
"提示: 请手动检查并删除 .claude/ 目录"
```

---

## 性能契约

| 操作 | 性能目标 | 测量方法 |
|------|---------|---------|
| 启动时间 | < 2 秒 | 从命令执行到第一个输出 |
| 安装时间 | < 5 秒 | 复制所有文件到目标目录 |
| 内存占用 | < 50 MB | 峰值内存使用 |
| 文件数量 | < 100 个 | `.claude/` 目录总文件数 |

---

## 测试契约

### 单元测试（可选）

- `test_validate_config_valid()`: 验证有效配置
- `test_validate_config_missing_field()`: 测试缺少字段
- `test_validate_config_invalid_enum()`: 测试无效枚举值
- `test_validate_config_out_of_range()`: 测试数值超出范围

### 集成测试（必需）

- `test_install_fresh_directory()`: 在空目录安装
- `test_install_existing_files()`: 覆盖已存在文件
- `test_install_permission_denied()`: 权限不足场景
- `test_rollback_on_failure()`: 安装失败回滚
- `test_dry_run_no_changes()`: dry-run 不修改文件系统

---

**API 契约版本**: 1.0.0
**最后更新**: 2026-01-04
