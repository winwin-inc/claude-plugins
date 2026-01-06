# 接口契约：构建配置

**类型**: 构建系统配置
**版本**: 1.0.0
**创建日期**: 2025-01-04

---

## 1. 概述

定义 `pyproject.toml` 中 hatchling 构建系统的完整配置契约，确保包正确构建和分发。

---

## 2. 构建系统配置

### 2.1 Build System 配置

**位置**: `pyproject.toml` → `[build-system]`

**契约**：
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**字段说明**：

| 字段 | 类型 | 必填 | 值 | 描述 |
|------|------|------|-----|------|
| `requires` | list[string] | 是 | `["hatchling"]` | 构建依赖 |
| `build-backend` | string | 是 | `"hatchling.build"` | 构建后端 |

**验证规则**：
- ✅ `requires` 必须包含 `hatchling`
- ✅ `build-backend` 必须是 `hatchling.build`
- ✅ 不得使用其他构建后端（setuptools、flit 等）

---

### 2.2 Wheel 构建目标配置

**位置**: `pyproject.toml` → `[tool.hatch.build.targets.wheel]`

**契约**：
```toml
[tool.hatch.build.targets.wheel]
packages = ["wiki_generator"]
include = [
    "wiki_generator/**/*.py",
    ".claude/commands/wiki-generate.md",
    ".claude/templates/**",
    ".claude/*.json",
    ".claude/*.md",
]
```

**字段说明**：

| 字段 | 类型 | 必填 | 描述 | 验证规则 |
|------|------|------|------|----------|
| `packages` | list[string] | 是 | 要打包的包目录列表 | 每个目录必须存在且包含 `__init__.py` |
| `include` | list[string] | 是 | 包含的文件模式列表 | 每个模式必须匹配至少一个文件 |

**包含模式说明**：

| 模式 | 描述 | 匹配示例 |
|------|------|----------|
| `wiki_generator/**/*.py` | 所有 Python 模块 | `wiki_generator/cli.py`, `wiki_generator/core/installer.py` |
| `.claude/commands/wiki-generate.md` | Wiki 命令文件 | `.claude/commands/wiki-generate.md` |
| `.claude/templates/**` | 所有模板文件（递归） | `.claude/templates/overview.md.template` |
| `.claude/*.json` | 根目录 JSON 文件 | `.claude/wiki-config.json` |
| `.claude/*.md` | 根目录 Markdown 文件 | `.claude/README.md`, `.claude/BEST-PRACTICES.md` |

**验证规则**：
- ✅ `packages` 必须是 `["wiki_generator"]`
- ✅ `include` 必须包含所有 `.claude` 相关文件
- ✅ 模式使用 `/` 作为路径分隔符（跨平台兼容）
- ✅ `**` 表示递归匹配

---

### 2.3 命令行入口点配置

**位置**: `pyproject.toml` → `[project.scripts]`

**契约**：
```toml
[project.scripts]
wiki-generator = "wiki_generator.cli:cli"
```

**字段说明**：

| 字段 | 类型 | 必填 | 描述 | 验证规则 |
|------|------|------|------|----------|
| `wiki-generator` | string | 是 | 命令行工具名 | 格式：`module:function` |
| (value) | string | 是 | 入口点引用 | `wiki_generator.cli:cli` |

**入口点格式**：
- **模块部分**: `wiki_generator.cli` → 相对于包根目录的模块路径
- **函数部分**: `cli` → 模块中的可调用对象名称

**验证规则**：
- ✅ 命令行工具名必须使用连字符：`wiki-generator`
- ✅ 入口点模块必须存在：`wiki_generator/cli.py`
- ✅ 入口点函数必须存在且可调用
- ✅ 模块使用点号分隔符
- ✅ 函数使用冒号分隔符

**命令调用示例**：
```bash
# 安装后可通过以下方式调用
wiki-generator
wiki-generator --help
wiki-generator --version
```

---

### 2.4 项目元数据配置

**位置**: `pyproject.toml` → `[project]`

**契约**：
```toml
[project]
name = "wiki-generator"
version = "1.0.0"
description = "Wiki Generator 安装工具 - 安装 wiki-generate 命令和模板到 Claude Code 项目"
readme = "README.md"
requires-python = ">=3.8"
license = { text = "MIT" }
authors = [
    { name = "Claude Plugins Team" }
]
keywords = ["claude-code", "cli", "wiki", "generator", "installer"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Build Tools",
]

dependencies = [
    "click>=8.0.0",
    "pyyaml>=6.0",
    "requests>=2.28.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.8.0",
]

[project.urls]
Homepage = "https://github.com/winwin-inc/claude-plugins"
Documentation = "https://github.com/winwin-inc/claude-plugins/blob/main/README.md"
Repository = "https://github.com/winwin-inc/claude-plugins"
Issues = "https://github.com/winwin-inc/claude-plugins/issues"
```

**关键字段验证**：

| 字段 | 必填 | 验证规则 |
|------|------|----------|
| `name` | 是 | 必须是 `wiki-generator`（PyPI 包名） |
| `version` | 是 | 必须符合 PEP 440 规范 |
| `requires-python` | 是 | 必须是 `>=3.8` |
| `dependencies` | 是 | 必须包含所有运行时依赖 |
| `license` | 是 | 必须指定许可证 |

---

### 2.5 Ruff 配置

**位置**: `pyproject.toml` → `[tool.ruff]`

**契约**：
```toml
[tool.ruff]
line-length = 100
target-version = "py38"
src = ["wiki_generator"]
```

**字段说明**：

| 字段 | 类型 | 必填 | 值 | 描述 |
|------|------|------|-----|------|
| `line-length` | integer | 是 | `100` | 最大行长度 |
| `target-version` | string | 是 | `"py38"` | 目标 Python 版本 |
| `src` | list[string] | 是 | `["wiki_generator"]` | 源代码目录 |

**验证规则**：
- ✅ `src` 必须是 `["wiki_generator"]`（不再是 `["src"]`）
- ✅ `target-version` 必须是 `"py38"` 或更高
- ✅ `line-length` 必须是 `100`

---

## 3. 构建输出契约

### 3.1 Wheel 文件命名

**契约**：
```
wiki_generator-{version}-py3-none-any.whl
```

**示例**：
```
wiki_generator-1.0.0-py3-none-any.whl
```

**命名规则**：
- 包名：`wiki_generator`（下划线）
- 版本：`1.0.0`
- Python 标签：`py3`（纯 Python）
- ABI 标签：`none`（无 ABI 依赖）
- 平台标签：`any`（跨平台）

---

### 3.2 Wheel 内容结构

**契约**：
```
wiki_generator-1.0.0.data/
├── purelib/
│   ├── wiki_generator/
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── cli.py
│   │   ├── core/
│   │   ├── models/
│   │   └── utils/
│   └── .claude/
│       ├── commands/
│       │   └── wiki-generate.md
│       ├── templates/
│       │   ├── api.md.template
│       │   ├── architecture.md.template
│       │   ├── development.md.template
│       │   ├── index.md.template
│       │   ├── module.md.template
│       │   ├── overview.md.template
│       │   └── wiki-config.json.template
│       ├── wiki-config.json
│       ├── README.md
│       └── BEST-PRACTICES.md
└── scripts/
    └── wiki-generator  # 或 wiki-generator.exe (Windows)

wiki_generator-1.0.0.dist-info/
├── METADATA
├── WHEEL
├── RECORD
└── entry_points.txt
```

**关键文件验证**：

| 文件 | 必需 | 验证 |
|------|------|------|
| `wiki_generator/__init__.py` | ✅ | 存在且包含版本信息 |
| `wiki_generator/cli.py` | ✅ | 存在且可导入 |
| `.claude/commands/wiki-generate.md` | ✅ | 存在且非空 |
| `.claude/templates/*.md.template` | ✅ | 至少 7 个模板文件 |
| `.claude/wiki-config.json` | ✅ | 存在且格式正确 |
| `scripts/wiki-generator` | ✅ | 存在且可执行（Unix） |
| `entry_points.txt` | ✅ | 包含 `wiki-generator` 入口点 |

---

### 3.3 METADATA 文件契约

**位置**: `*.dist-info/METADATA`

**关键元数据**：
```
Name: wiki-generator
Version: 1.0.0
Summary: Wiki Generator 安装工具 - 安装 wiki-generate 命令和模板到 Claude Code 项目
Requires-Python: >=3.8
License: MIT

Entry-Points:
  [console_scripts]
  wiki-generator = wiki_generator.cli:cli

Requires-Dist:
  click>=8.0.0
  pyyaml>=6.0
  requests>=2.28.0
```

**验证规则**：
- ✅ `Name` 必须是 `wiki-generator`
- ✅ `Requires-Python` 必须包含 `>=3.8`
- ✅ `Entry-Points` 必须包含 `wiki-generator = wiki_generator.cli:cli`
- ✅ `Requires-Dist` 必须包含所有依赖

---

## 4. 实施验证契约

### 4.1 构建验证脚本

**脚本位置**: `scripts/verify-build.sh`

**契约**：
```bash
#!/bin/bash
set -e

echo "🔍 验证构建配置..."

# 检查 pyproject.toml 格式
python -c "import tomli; tomli.load(open('pyproject.toml'))"
echo "✓ TOML 格式正确"

# 检查包名配置
grep -q 'packages = \["wiki_generator"\]' pyproject.toml
echo "✓ 包名配置正确"

# 检查入口点配置
grep -q 'wiki-generator = "wiki_generator.cli:cli"' pyproject.toml
echo "✓ 入口点配置正确"

# 清理旧构建
rm -rf dist/ build/ *.egg-info
echo "✓ 清理旧构建"

# 构建包
uv build
echo "✓ 包构建成功"

# 检查 wheel 文件
WHEEL=$(ls dist/*.whl)
if [ -z "$WHEEL" ]; then
    echo "❌ wheel 文件未生成"
    exit 1
fi
echo "✓ wheel 文件已生成: $WHEEL"

# 验证关键文件存在
unzip -l "$WHEEL" | grep -q "wiki_generator/__init__.py"
echo "✓ __init__.py 已打包"

unzip -l "$WHEEL" | grep -q ".claude/commands/wiki-generate.md"
echo "✓ 命令文件已打包"

unzip -l "$WHEEL" | grep -q ".claude/templates/"
echo "✓ 模板目录已打包"

# 检查入口点
unzip -l "$WHEEL" | grep -q "entry_points.txt"
echo "✓ 入口点文件已打包"

echo ""
echo "✅ 所有验证通过"
```

---

### 4.2 安装测试契约

**测试位置**: `scripts/test-install.sh`

**契约**：
```bash
#!/bin/bash
set -e

echo "🧪 测试包安装..."

# 创建测试环境
TEST_VENV=$(mktemp -d)
python -m venv "$TEST_VENV"
source "$TEST_VENV/bin/activate"

# 安装包
pip install dist/*.whl --quiet
echo "✓ 包安装成功"

# 测试模块导入
python -c "import wiki_generator; print(f'✓ 模块导入成功: {wiki_generator.__version__}')"

# 测试命令行工具
wiki-generator --version
echo "✓ 命令行工具可用"

# 测试数据文件访问
python -c "
from pathlib import Path
try:
    from importlib.resources import files
    claude_dir = files('wiki_generator') / '.claude'
    print(f'✓ 数据目录可访问: {claude_dir}')
except ImportError:
    from pkg_resources import resource_filename
    claude_dir = Path(resource_filename('wiki_generator', '.claude'))
    print(f'✓ 数据目录可访问: {claude_dir}')
"

# 清理
deactivate
rm -rf "$TEST_VENV"

echo ""
echo "✅ 所有测试通过"
```

---

## 5. 合规性检查清单

### 5.1 构建前检查

- [ ] `pyproject.toml` 格式正确（TOML 语法）
- [ ] `packages = ["wiki_generator"]` 已配置
- [ ] `include` 包含所有 `.claude` 文件
- [ ] `wiki-generator = "wiki_generator.cli:cli"` 入口点已配置
- [ ] `src = ["wiki_generator"]` Ruff 配置已更新

### 5.2 构建后检查

- [ ] `dist/*.whl` 文件已生成
- [ ] 文件名符合命名规范
- [ ] `wiki_generator/__init__.py` 存在于 wheel 中
- [ ] `.claude/commands/wiki-generate.md` 存在
- [ ] `.claude/templates/` 目录存在且包含 7 个模板
- [ ] `entry_points.txt` 包含正确入口点

### 5.3 安装后检查

- [ ] `import wiki_generator` 成功
- [ ] `wiki-generator` 命令可用
- [ ] 数据文件可从包内访问
- [ ] 版本号正确显示

---

## 6. 错误处理契约

### 6.1 构建错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `TOML syntax error` | `pyproject.toml` 格式错误 | 检查 TOML 语法 |
| `package not found` | `wiki_generator/` 目录不存在 | 创建目录和 `__init__.py` |
| `entry point not found` | `cli:cli` 函数不存在 | 检查 `wiki_generator/cli.py` |
| `no files matched` | `include` 模式不匹配文件 | 检查文件路径和模式 |

### 6.2 安装错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `ModuleNotFoundError` | 模块导入失败 | 检查包名和模块路径 |
| `No module named 'wiki_generator'` | 包未正确安装 | 重新构建和安装 |
| `command not found` | 入口点未注册 | 检查 `[project.scripts]` 配置 |
| `FileNotFoundError` | 数据文件缺失 | 检查 `include` 配置 |

---

## 7. 版本兼容性契约

### 7.1 Python 版本支持

| Python 版本 | 支持状态 | 数据文件访问方式 |
|-------------|----------|-------------------|
| 3.8 | ✅ 支持 | `pkg_resources` |
| 3.9 | ✅ 支持 | `importlib.resources` |
| 3.10 | ✅ 支持 | `importlib.resources` |
| 3.11 | ✅ 支持 | `importlib.resources` |
| 3.12 | ✅ 支持 | `importlib.resources` |

### 7.2 平台支持

| 平台 | 支持状态 | 注意事项 |
|------|----------|----------|
| Linux | ✅ 完全支持 | 无 |
| macOS | ✅ 完全支持 | 无 |
| Windows | ✅ 完全支持 | 路径使用 `pathlib` |

---

## 8. 总结

✅ **配置完整性**：所有必需的构建配置已定义
✅ **验证契约**：提供了完整的验证脚本
✅ **错误处理**：定义了常见错误和解决方案
✅ **兼容性**：确保跨平台和跨 Python 版本支持

---

**契约版本**: 1.0.0
**最后更新**: 2025-01-04
