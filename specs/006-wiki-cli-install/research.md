# Research Report: Wiki Generator CLI 安装工具优化

**功能版本**: 1.0.0
**创建日期**: 2026-01-04
**状态**: 完成

---

## 研究目标

解决技术未知项，验证技术可行性，为设计阶段提供决策支持。

---

## Research Task 001: Python CLI 安装工具最佳实践

### 研究问题

1. 如何通过 `uvx` 命令实现轻量级 Python 工具的分发？
2. 如何设计跨平台的文件复制和回滚机制？
3. 如何生成带注释的 JSON 配置文件？

### 研究方法

- 分析现有的 `cli.py` 实现
- 调研 Python CLI 工具的最佳实践
- 研究文件操作和错误处理模式

### 研究发现

#### 1. uvx 命令分发机制

**uvx 的优势**：
- 无需预先安装包，直接从 PyPI 运行
- 自动管理虚拟环境
- 支持任意 Python 版本要求（如 Python 3.11+）

**实现方式**：
```python
# pyproject.toml 配置
[project.scripts]
wiki-generator = "wiki_generator.installer:main"

# 用户运行
uvx wiki-generator
```

**决策**：使用 `uvx` 作为主要分发方式，保留 `pip install -e .` 作为备选。

**理由**：
- `uvx` 零安装，用户体验最佳
- `pip install -e .` 用于开发者本地调试
- 符合现代 Python 工具分发趋势

#### 2. 跨平台文件复制和回滚机制

**文件复制策略**：

**方案对比**：

| 方案 | 优点 | 缺点 | 评分 |
|------|------|------|------|
| **shutil.copy2**（选择） | Python 标准库，保留元数据 | 不能自动创建目录 | ⭐⭐⭐⭐⭐ |
| shutil.copytree | 递归复制目录 | 无法覆盖单个文件 | ⭐⭐⭐ |
| rsync 命令 | 功能强大 | 依赖外部工具 | ⭐⭐⭐⭐ |

**决策**：使用 `shutil.copy2` + `os.makedirs` 组合。

**理由**：
- 纯 Python 实现，无外部依赖
- 跨平台兼容（Linux/macOS/Windows）
- 保留文件元数据（修改时间等）

**回滚机制**：

```python
installed_files = []  # 跟踪已安装的文件

try:
    # 安装文件
    for src, dst in file_mapping:
        shutil.copy2(src, dst)
        installed_files.append(dst)
except Exception as e:
    # 回滚：删除已安装的文件
    for file in installed_files:
        if os.path.exists(file):
            os.remove(file)
    raise
```

**决策**：使用文件列表跟踪 + 异常处理回滚。

**理由**：
- 简单可靠，易于理解
- 不需要复杂的快照机制
- 符合"避免过度工程"原则

#### 3. JSON 配置文件生成

**JSON 注释问题**：

标准 JSON 不支持注释，但可以通过以下方式解决：

**方案对比**：

| 方案 | 优点 | 缺点 | 评分 |
|------|------|------|------|
| **JSONC（带注释的 JSON）** | VS Code 等工具原生支持 | 非标准格式 | ⭐⭐⭐⭐⭐ |
| JSON5 | 功能完整 | 需要额外库 | ⭐⭐⭐⭐ |
| 单独的 README 说明 | 标准 JSON | 分散信息 | ⭐⭐⭐ |

**决策**：使用 JSONC 格式（带 // 注释），配置文件使用 `.jsonc` 扩展名或说明注释会被工具忽略。

**实现**：
```python
import json

config = {
    "output_dir": "docs",
    "exclude_patterns": ["node_modules", "dist", ".git"],
    # ... 其他字段
}

# 写入带注释的 JSON
with open("wiki-config.json", "w", encoding="utf-8") as f:
    f.write("{\n")
    f.write('  // Wiki Generator 配置文件\n')
    f.write('  // 生成时间: 2026-01-04\n')
    f.write("\n")
    json.dump(config, f, indent=2, ensure_ascii=False)
    f.write("\n")
```

**优化方案**：使用 `json.dumps()` 生成标准 JSON，在文件开头添加块注释（某些 JSON 解析器可接受）。

**最终决策**：生成标准 JSON，在配置文件中添加 `_comment` 字段或在顶部添加描述性注释（某些工具会忽略）。

---

## Research Task 002: 配置文件字段设计

### 研究问题

1. 如何设计合理的默认配置值？
2. 如何验证配置文件的有效性？

### 研究发现

#### 默认配置值设计

**参考现有配置**（从 CLAUDE.md 提取）：
```json
{
  "output_dir": "docs",
  "exclude_patterns": ["node_modules", "dist", ".git"],
  "template_dir": ".claude/templates",
  "quality_threshold": 80,
  "diagrams": {
    "enabled": true,
    "detail_level": "medium"
  }
}
```

**优化后的扁平结构**（简化版）：
```json
{
  "output_dir": "docs",
  "exclude_patterns": ["node_modules", "dist", ".git"],
  "quality_threshold": 80,
  "diagrams_enabled": true,
  "diagrams_detail_level": "medium"
}
```

**决策**：使用扁平结构（5 个字段），避免嵌套。

**理由**：
- 简化配置，易于理解和修改
- 减少嵌套层级，符合"保持简单"原则
- 所有字段都是必需的，无可选嵌套对象

#### 配置验证

**验证策略**：
1. JSON 格式验证（`json.load()`）
2. 字段类型验证（字符串、数组、整数、布尔值）
3. 枚举值验证（`diagrams_detail_level` 只能是 "low"/"medium"/"high"）

**实现**：
```python
from typing import Literal

def validate_config(config: dict) -> bool:
    """验证配置文件格式和字段值"""
    required_fields = {
        "output_dir": str,
        "exclude_patterns": list,
        "quality_threshold": int,
        "diagrams_enabled": bool,
        "diagrams_detail_level": str
    }

    # 检查必需字段
    for field, field_type in required_fields.items():
        if field not in config:
            return False
        if not isinstance(config[field], field_type):
            return False

    # 验证枚举值
    if config["diagrams_detail_level"] not in ["low", "medium", "high"]:
        return False

    # 验证范围
    if not (0 <= config["quality_threshold"] <= 100):
        return False

    return True
```

---

## Research Task 003: 符号链接处理策略

### 研究问题

如何在跨平台环境下正确处理符号链接？

### 研究发现

**平台差异**：
- Linux/macOS：支持符号链接（`symlink`）
- Windows：支持符号链接（需要管理员权限或开发者模式）或快捷方式（`.lnk`）

**处理策略**：

| 方案 | 描述 | 评分 |
|------|------|------|
| **保留符号链接** | 使用 `shutil.copy2(follow_symlinks=False)` | ⭐⭐⭐⭐⭐ |
| 展开符号链接 | 复制链接指向的实际文件 | ⭐⭐⭐ |
| 跳过符号链接 | 遇到符号链接时警告并跳过 | ⭐⭐ |

**决策**：使用 `follow_symlinks=False` 保留符号链接。

**理由**：
- 符号链接在 `.claude/` 目录中可能是预期的（例如模板链接）
- 保留链接结构，减少磁盘占用
- `shutil.copy2` 默认行为（不跟随链接）

**实现**：
```python
def copy_file_with_symlinks(src, dst):
    """复制文件，保留符号链接"""
    try:
        shutil.copy2(src, dst, follow_symlinks=False)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.remove(dst)
            shutil.copy2(src, dst, follow_symlinks=False)
        else:
            raise
```

---

## 总结和决策

### 技术选型总结

| 决策点 | 选择方案 | 理由 |
|--------|---------|------|
| 分发方式 | `uvx wiki-generator` | 零安装，现代 Python 最佳实践 |
| 文件复制 | `shutil.copy2` + `os.makedirs` | Python 标准库，跨平台 |
| 回滚机制 | 文件列表跟踪 + 异常处理 | 简单可靠 |
| 配置格式 | 标准 JSON（5 个扁平字段） | 简洁，易于验证 |
| 符号链接 | 保留链接（`follow_symlinks=False`） | 减少磁盘占用，保持结构 |

### 风险评估

| 风险 | 影响 | 缓解措施 | 残余风险 |
|------|------|----------|----------|
| Windows 符号链接兼容性 | 中 | 测试 WSL 环境，提供降级选项 | 低 |
| JSON 配置损坏 | 中 | 备份现有配置，验证 JSON 格式 | 低 |
| 文件权限问题 | 低 | 预检查权限，提前报错 | 低 |

### 后续工作

基于研究结果，下一阶段（Phase 1: 设计和契约）将：

1. **生成数据模型**：
   - `WikiConfig`（配置文件实体）
   - `InstalledFile`（已安装文件跟踪）
   - `ValidationError`（验证错误）

2. **生成 API 契约**：
   - `install_cli_files()` - 安装 CLI 文件
   - `generate_config()` - 生成配置文件
   - `validate_config()` - 验证配置
   - `rollback_installation()` - 回滚安装

3. **生成快速开始文档**：
   - 安装步骤
   - 配置说明
   - 使用示例

---

**研究报告版本**: 1.0.0
**完成日期**: 2026-01-04
**状态**: ✅ 完成 - 所有技术问题已解决
