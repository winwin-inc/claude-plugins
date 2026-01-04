# 包结构修复测试指南

**功能编号**: 003
**功能名称**: fix-package-structure
**测试日期**: 2025-01-04

---

## 📋 测试概述

本测试指南用于验证包结构修复是否成功，确保：

1. ✅ 包名从 `src` 改为 `wiki_generator`
2. ✅ `.claude` 目录正确包含在 wheel 包中
3. ✅ 模块可以正确导入
4. ✅ 命令行工具正常工作
5. ✅ 文件复制功能正常

---

## 🔧 环境要求

### 必需工具
- Python 3.8+
- uv (Python 包管理器)

### 安装 uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# 或
pip install uv
```

---

## 🧪 测试步骤

### 第一步：清理并构建

```bash
cd /home/yewenbin/work/ai/claude/repo-wiki

# 清理旧的构建产物
rm -rf dist/ build/ *.egg-info

# 重新构建 wheel 包
uv build
```

**预期结果**:
```
Built wheel: dist/wiki_generator-1.0.0-py3-none-any.whl
```

**验证命令**:
```bash
ls -lh dist/
# 应该看到 wiki_generator-1.0.0-py3-none-any.whl
```

---

### 第二步：验证 wheel 内容

```bash
# 查看 wheel 包内容
unzip -l dist/*.whl
```

**关键文件检查**:
```bash
# 检查包初始化文件
unzip -l dist/*.whl | grep "wiki_generator/__init__.py"

# 检查 .claude 命令文件
unzip -l dist/*.whl | grep ".claude/commands/wiki-generate.md"

# 检查模板目录
unzip -l dist/*.whl | grep ".claude/templates/"

# 检查配置文件
unzip -l dist/*.whl | grep ".claude/wiki-config.json"
```

**预期结果**:
```
wiki_generator/__init__.py
wiki_generator/cli.py
wiki_generator/utils/*.py
.claude/commands/wiki-generate.md
.claude/templates/*.md.template
.claude/wiki-config.json
.claude/README.md
```

---

### 第三步：重新安装工具

```bash
# 强制重新安装
uv tool install . --force
```

**预期结果**:
```
Installed wiki-generator v1.0.0
```

**验证安装位置**:
```bash
which wiki-generator
# 应显示: ~/.local/bin/wiki-generator 或类似路径
```

---

### 第四步：测试模块导入

```bash
python3 -c "import wiki_generator; print(wiki_generator.__version__)"
```

**预期结果**:
```
1.0.0
```

**测试详细导入**:
```bash
python3 << 'EOF'
import wiki_generator
from wiki_generator.cli import get_package_claude_dir
from wiki_generator.utils.formatter import format_success

print(f"✓ 模块版本: {wiki_generator.__version__}")
print(f"✓ 模块导入成功")

claude_dir = get_package_claude_dir()
print(f"✓ .claude 目录: {claude_dir}")
print(f"✓ 目录存在: {claude_dir.exists()}")
EOF
```

**预期结果**:
```
✓ 模块版本: 1.0.0
✓ 模块导入成功
✓ .claude 目录: /path/to/.claude
✓ 目录存在: True
```

---

### 第五步：测试命令行工具

```bash
# 测试版本命令
wiki-generator --version
```

**预期结果**:
```
wiki-generator version 1.0.0
```

**测试帮助命令**:
```bash
wiki-generator --help
```

**预期结果**:
```
Wiki Generator 安装工具

将 wiki-generator 项目中的 .claude/ 目录复制到你的项目目录，
实现 Claude Code 自定义命令和模板的快速安装。

默认情况下，文件会被复制到当前工作目录。

Usage: wiki-generator [OPTIONS]

Options:
  -t, --target PATH  目标项目目录（默认为当前工作目录）
  -o, --overwrite    覆盖已存在的文件
  -n, --dry-run      预览操作，不实际复制文件
  --version          Show the version and exit.
  --help             Show this message and exit.
```

---

### 第六步：测试文件复制功能

```bash
# 创建测试项目
cd /tmp
rm -rf test-project
mkdir test-project && cd test-project

# 初始化 git 仓库（某些功能可能需要）
git init

# 预览模式（不实际复制）
wiki-generator --dry-run
```

**预期结果**:
```
目标目录: /tmp/test-project
源目录: /path/to/wiki_generator/.claude
将创建新的 .claude/ 目录

将要复制的内容：
  📄 wiki-generate.md (xxx B)
  📁 templates/ (xxx B)

⚠️ 预览模式：未实际复制文件
ℹ️ 移除 --dry-run 选项以执行实际安装
```

**实际安装**:
```bash
# 实际执行安装
wiki-generator
```

**验证文件**:
```bash
# 检查文件是否复制成功
ls -la .claude/
ls -la .claude/commands/
ls -la .claude/templates/

# 检查关键文件内容
cat .claude/commands/wiki-generate.md | head -20
```

**预期结果**:
```
.claude/
├── commands/
│   └── wiki-generate.md
├── templates/
│   ├── overview.md.template
│   ├── module.md.template
│   └── ...
├── wiki-config.json
├── README.md
└── BEST-PRACTICES.md
```

---

### 第七步：清理测试环境

```bash
# 返回项目目录
cd /home/yewenbin/work/ai/claude/repo-wiki

# 清理测试项目
rm -rf /tmp/test-project
```

---

## ✅ 成功标准

所有测试必须满足以下标准：

| 测试项 | 标准 | 状态 |
|--------|------|------|
| 包构建 | 成功生成 wheel 文件 | ⬜ |
| 包内容 | 包含所有必需文件 | ⬜ |
| 模块导入 | 成功导入，无错误 | ⬜ |
| 版本号 | 正确显示 1.0.0 | ⬜ |
| 命令行工具 | 可执行，帮助信息正确 | ⬜ |
| 文件复制 | 成功复制到测试项目 | ⬜ |

---

## 🐛 常见问题

### 问题 1: uv 命令未找到
**错误**: `/bin/bash: uv: command not found`

**解决**:
```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 重新加载 shell 配置
source ~/.bashrc  # 或 source ~/.zshrc
```

---

### 问题 2: 构建失败，找不到包
**错误**: `Package 'wiki_generator' not found`

**解决**:
```bash
# 检查目录结构
ls -la wiki_generator/
# 应该看到 __init__.py, cli.py 等

# 检查 __init__.py 内容
cat wiki_generator/__init__.py
# 应该包含 __version__ = "1.0.0"
```

---

### 问题 3: wheel 中缺少 .claude 目录
**错误**: wheel 包中没有 `.claude/` 文件

**解决**:
```bash
# 检查 pyproject.toml 配置
grep -A 10 "\[tool.hatch.build.targets.wheel\]" pyproject.toml

# 确保 include 配置正确
# include = [
#     "wiki_generator/**/*.py",
#     ".claude/commands/wiki-generate.md",
#     ".claude/templates/**",
#     ".claude/*.json",
#     ".claude/*.md",
# ]
```

---

### 问题 4: 模块导入失败
**错误**: `No module named 'wiki_generator'`

**解决**:
```bash
# 检查安装状态
uv tool list | grep wiki-generator

# 重新安装
uv tool install . --force

# 验证安装位置
which wiki-generator
```

---

### 问题 5: CLI 找不到 .claude 目录
**错误**: `找不到 .claude/ 目录：/path/to/wiki_generator/.claude`

**解决**:
```bash
# 检查安装的包内容
python3 -c "
import wiki_generator
from wiki_generator.cli import get_package_claude_dir
print(get_package_claude_dir())
"

# 如果仍然失败，重新构建和安装
rm -rf dist/ build/ *.egg-info
uv build
uv tool install . --force
```

---

## 📊 测试报告模板

完成测试后，请填写以下报告：

```markdown
## 测试报告

**测试日期**: YYYY-MM-DD
**测试人员**: [姓名]
**环境信息**: Python X.X.X, uv X.X.X

### 测试结果

| 测试项 | 状态 | 备注 |
|--------|------|------|
| 包构建 | ✅/❌ | |
| 包内容 | ✅/❌ | |
| 模块导入 | ✅/❌ | |
| 版本号 | ✅/❌ | |
| 命令行工具 | ✅/❌ | |
| 文件复制 | ✅/❌ | |

### 遇到的问题
[记录测试过程中遇到的问题]

### 建议和反馈
[记录任何建议或反馈]
```

---

**测试指南版本**: 1.0.0
**创建日期**: 2025-01-04
**最后更新**: 2025-01-04
