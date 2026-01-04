# 快速开始指南：包结构和打包配置修复

**功能**: fix-package-structure
**创建日期**: 2025-01-04
**预计时间**: 30 分钟

---

## 1. 概述

本指南将帮助你修复 wiki-generator Python 包的安装路径和打包配置问题。修复后，用户可以正确安装和使用工具。

**主要变更**：
- ✅ 将 `src/` 目录重命名为 `wiki_generator/`
- ✅ 更新 `pyproject.toml` 打包配置
- ✅ 修复 CLI 中的包数据文件访问路径

---

## 2. 前置条件

### 2.1 环境要求

- Python 3.8+ (推荐 3.10+)
- Git
- uv (最新版本)

**检查环境**：
```bash
# 检查 Python 版本
python --version
# 应该输出: Python 3.8.x 或更高

# 检查 Git
git --version
# 应该输出: git version 2.x.x

# 检查 uv
uv --version
# 应该输出: uv 0.x.x
```

### 2.2 安装 uv（如果未安装）

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或使用 pip
pip install uv
```

---

## 3. 快速修复流程

### 步骤 1：确认当前状态

```bash
# 查看项目结构
ls -la

# 应该看到:
# src/
# pyproject.toml
# .claude/
```

**当前问题验证**：
```bash
# 构建当前包
uv build

# 检查 wheel 内容（应该看到问题）
unzip -l dist/*.whl | grep -E "^.*\.py$|^.*\.claude/"
# 应该看到: src/ 目录，而不是 wiki_generator/
# 应该看不到: .claude/ 目录（未打包）
```

---

### 步骤 2：重命名包目录

```bash
# 重命名 src/ 为 wiki_generator/
mv src wiki_generator

# 创建 __init__.py
cat > wiki_generator/__init__.py << 'EOF'
"""
Wiki Generator - 安装 wiki-generate 命令和模板到 Claude Code 项目

这个包提供了一个命令行工具，用于将 Claude Code 自定义命令和模板
安装到项目中。
"""

__version__ = "1.0.0"
__author__ = "Repo Wiki Generator Team"
__all__ = ["__version__"]
EOF

# 验证
ls -la wiki_generator/
# 应该看到: __init__.py, cli.py, core/, utils/, models/
```

---

### 步骤 3：更新 pyproject.toml

**打开 `pyproject.toml` 并进行以下修改**：

#### 3.1 更新包路径

**修改前**：
```toml
[tool.hatch.build.targets.wheel]
packages = ["src"]
```

**修改后**：
```toml
[tool.hatch.build.targets.wheel]
packages = ["wiki_generator"]
```

#### 3.2 添加包含文件配置

**在 `[tool.hatch.build.targets.wheel]` 部分添加**：
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

#### 3.3 更新入口点

**修改前**：
```toml
[project.scripts]
wiki-generator = "src.cli:cli"
```

**修改后**：
```toml
[project.scripts]
wiki-generator = "wiki_generator.cli:cli"
```

#### 3.4 更新 Ruff 配置

**修改前**：
```toml
[tool.ruff]
src = ["src"]
```

**修改后**：
```toml
[tool.ruff]
src = ["wiki_generator"]
```

**保存文件**。

---

### 步骤 4：修复 CLI 中的数据文件访问

**打开 `wiki_generator/cli.py` 并更新数据文件访问代码**：

**在文件顶部添加**：
```python
from pathlib import Path

# 包数据文件访问（跨 Python 版本兼容）
try:
    # Python 3.9+
    from importlib.resources import files as _files
    def _get_package_data(path: str) -> Path:
        return Path(str(_files('wiki_generator') / path))
except ImportError:
    # Python 3.8
    from pkg_resources import resource_filename
    def _get_package_data(path: str) -> Path:
        return Path(resource_filename('wiki_generator', path))
```

**更新 `claude_dir` 获取方式**：
```python
# 修改前（如果有）
# claude_dir = Path(__file__).parent.parent / ".claude"

# 修改后
claude_dir = _get_package_data('.claude')
```

**保存文件**。

---

### 步骤 5：清理和重新构建

```bash
# 清理旧的构建产物
rm -rf dist/ build/ *.egg-info

# 重新构建
uv build

# 应该看到:
# Built wheel: dist/wiki_generator-1.0.0-py3-none-any.whl
```

---

### 步骤 6：验证构建结果

```bash
# 检查 wheel 内容
WHEEL=$(ls dist/*.whl)
unzip -l $WHEEL | grep -E "wiki_generator|\.claude/"

# 应该看到:
# wiki_generator/
# wiki_generator/__init__.py
# wiki_generator/cli.py
# .claude/
# .claude/commands/wiki-generate.md
# .claude/templates/
# ...

# 验证关键文件
unzip -l $WHEEL | grep "wiki_generator/__init__.py"
# 应该看到该文件

unzip -l $WHEEL | grep ".claude/commands/wiki-generate.md"
# 应该看到该文件

unzip -l $WHEEL | grep ".claude/templates/"
# 应该看到模板目录
```

---

### 步骤 7：测试本地安装

```bash
# 创建测试环境
python -m venv test_venv
source test_venv/bin/activate  # Windows: test_venv\Scripts\activate

# 安装包
uv pip install dist/*.whl

# 测试模块导入
python -c "import wiki_generator; print(f'✓ 版本: {wiki_generator.__version__}')"
# 应该看到: ✓ 版本: 1.0.0

# 测试命令行工具
wiki-generator --version
# 应该看到: wiki-generator version 1.0.0

# 创建测试项目
cd /tmp
mkdir test-project && cd test-project
git init
wiki-generator

# 验证安装
ls -la .claude/
# 应该看到: commands/, templates/, wiki-config.json, README.md, BEST-PRACTICES.md

# 清理
deactivate
rm -rf test_venv /tmp/test-project
```

---

### 步骤 8：提交变更

```bash
# 查看变更
git status

# 添加变更文件
git add -A

# 提交
git commit -m "fix: 修复包结构和打包配置

主要变更:
- 将 src/ 目录重命名为 wiki_generator/
- 创建 wiki_generator/__init__.py
- 更新 pyproject.toml 打包配置
  - 包路径: src -> wiki_generator
  - 添加 .claude 目录到打包配置
  - 更新入口点: src.cli:cli -> wiki_generator.cli:cli
  - 更新 ruff 配置: src -> wiki_generator
- 修复 cli.py 中的包数据文件访问路径
  - 使用 importlib.resources (Python 3.9+)
  - 使用 pkg_resources 回退 (Python 3.8)

测试:
- ✓ 模块导入成功
- ✓ 命令行工具可用
- ✓ 包内 .claude 目录可访问
- ✓ 文件复制功能正常

修复问题:
- 修复后模块导入路径为 wiki_generator（而非 src）
- 打包时包含 .claude 目录下的所有文件
"

# 推送（如果需要）
git push origin 1-fix-package-structure
```

---

## 4. 验证清单

完成修复后，使用以下清单验证所有变更：

### 4.1 目录结构

- [ ] `wiki_generator/` 目录存在（替代 `src/`）
- [ ] `wiki_generator/__init__.py` 文件存在且包含版本信息
- [ ] `.claude/` 目录包含所有必需文件

### 4.2 配置文件

- [ ] `pyproject.toml` 中 `packages = ["wiki_generator"]`
- [ ] `pyproject.toml` 中 `include` 包含 `.claude/**`
- [ ] `pyproject.toml` 中入口点为 `wiki_generator.cli:cli`
- [ ] `pyproject.toml` 中 `src = ["wiki_generator"]`

### 4.3 构建验证

- [ ] `uv build` 成功构建 wheel
- [ ] `unzip -l dist/*.whl` 显示 `wiki_generator/` 目录
- [ ] `unzip -l dist/*.whl` 显示 `.claude/` 目录
- [ ] `wiki_generator/__init__.py` 在 wheel 中存在

### 4.4 安装测试

- [ ] `import wiki_generator` 成功
- [ ] `wiki-generator --version` 输出版本号
- [ ] `wiki-generator` 命令可以复制文件到测试项目
- [ ] 复制的 `.claude/` 目录包含所有模板文件

---

## 5. 常见问题

### Q1: 构建失败，提示 "package not found"

**原因**: `wiki_generator/` 目录不存在或没有 `__init__.py`

**解决方案**:
```bash
# 确保目录存在
ls -la wiki_generator/

# 创建 __init__.py
touch wiki_generator/__init__.py

# 重新构建
uv build
```

---

### Q2: wheel 中没有 .claude 目录

**原因**: `pyproject.toml` 中的 `include` 配置不正确

**解决方案**:
```bash
# 检查配置
grep -A 5 "\[tool.hatch.build.targets.wheel\]" pyproject.toml

# 确保 include 包含 .claude 文件
# include = [
#     "wiki_generator/**/*.py",
#     ".claude/commands/wiki-generate.md",
#     ".claude/templates/**",
#     ".claude/*.json",
#     ".claude/*.md",
# ]
```

---

### Q3: 安装后提示 "No module named 'wiki_generator'"

**原因**: 入口点配置不正确或包未正确安装

**解决方案**:
```bash
# 检查入口点配置
grep "\[project.scripts\]" -A 2 pyproject.toml
# 应该看到: wiki-generator = "wiki_generator.cli:cli"

# 重新安装
uv pip install --force-reinstall dist/*.whl
```

---

### Q4: CLI 运行时提示 ".claude 目录不存在"

**原因**: 包数据文件访问代码不正确

**解决方案**:
```bash
# 检查 cli.py 中的数据访问代码
grep "_get_package_data" wiki_generator/cli.py

# 确保使用了正确的函数:
# try:
#     from importlib.resources import files
#     claude_dir = Path(str(files('wiki_generator') / '.claude'))
# except ImportError:
#     from pkg_resources import resource_filename
#     claude_dir = Path(resource_filename('wiki_generator', '.claude'))
```

---

### Q5: 如何回滚变更？

**使用 Git 回滚**:
```bash
# 查看提交历史
git log --oneline

# 回滚到上一个版本
git reset --hard HEAD~1

# 或回滚特定文件
git checkout HEAD~1 -- pyproject.toml
```

---

## 6. 下一步

修复完成后，你可以：

1. **测试功能**: 在多个项目中测试 `wiki-generator` 命令
2. **发布到 PyPI**: 将修复后的包发布到 Python Package Index
3. **更新文档**: 更新 README 和用户文档
4. **创建版本标签**: `git tag v1.0.1`

---

## 7. 参考资源

- [Python 打包用户指南](https://packaging.python.org/)
- [Hatchling 文档](https://hatch.pypa.io/latest/)
- [uv 文档](https://github.com/astral-sh/uv)
- [importlib.resources 文档](https://docs.python.org/3/library/importlib.html#module-importlib.resources)

---

**指南版本**: 1.0.0
**最后更新**: 2025-01-04
**预计完成时间**: 30 分钟
