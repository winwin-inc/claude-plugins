# 快速开始: Wiki Generator CLI 安装工具

**功能版本**: 1.0.0
**创建日期**: 2026-01-04

---

## 概述

Wiki Generator CLI 是一个轻量级的 Python 命令行工具，用于将 Claude Code 自定义 Wiki 命令和模板安装到项目中。通过 `uvx wiki-generator` 命令，一键完成所有安装配置。

---

## 前置要求

### 系统要求

- **Python**: 3.11 或更高版本
- **操作系统**: Linux、macOS、Windows (WSL)
- **网络**: 访问 PyPI（用于 `uvx` 下载包）
- **权限**: 当前目录的写入权限

### 安装 uv（如果未安装）

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或使用 pip
pip install uv
```

---

## 安装步骤

### 方式 1: 使用 uvx（推荐）

```bash
# 在你的项目目录中运行
cd /path/to/your/project

# 一键安装
uvx wiki-generator
```

**说明**:
- `uvx` 会自动下载并运行最新版本
- 无需预先安装工具
- 适合一次性使用或快速测试

### 方式 2: 使用 pip 安装

```bash
# 安装到当前环境
pip install wiki-generator

# 运行安装命令
wiki-generator
```

**说明**:
- 适合本地开发和调试
- 可以修改源代码
- 需要定期手动更新

---

## 配置文件

安装完成后，会在项目根目录生成 `wiki-config.json` 配置文件：

```json
{
  "output_dir": "docs",
  "exclude_patterns": ["node_modules", "dist", ".git"],
  "quality_threshold": 80,
  "diagrams_enabled": true,
  "diagrams_detail_level": "medium"
}
```

### 配置字段说明

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `output_dir` | Wiki 文档输出目录 | `"docs"` |
| `exclude_patterns` | 排除的文件/目录模式 | `["node_modules", "dist", ".git"]` |
| `quality_threshold` | 文档质量分数阈值（0-100） | `80` |
| `diagrams_enabled` | 是否生成 Mermaid 图表 | `true` |
| `diagrams_detail_level` | 图表细节级别 | `"medium"` |

### 自定义配置

```bash
# 编辑配置文件
nano wiki-config.json

# 或使用任何文本编辑器
vim wiki-config.json
code wiki-config.json
```

**示例自定义**:
```json
{
  "output_dir": "zh/content",
  "exclude_patterns": ["node_modules", "dist", ".git", "__pycache__", "tests"],
  "quality_threshold": 85,
  "diagrams_enabled": true,
  "diagrams_detail_level": "high"
}
```

---

## 命令选项

### 基本用法

```bash
# 查看帮助
wiki-generator --help

# 显示版本
wiki-generator --version

# Dry-run 模式（查看将要安装的文件）
wiki-generator --dry-run

# 强制覆盖已存在文件
wiki-generator --force

# 安装到自定义目录
wiki-generator --target-dir /path/to/project

# 详细输出模式
wiki-generator --verbose
```

### 选项组合

```bash
# Dry-run + 详细模式
wiki-generator --dry-run --verbose

# 强制覆盖 + 详细模式
wiki-generator --force --verbose

# 安装到自定义目录 + 强制覆盖
wiki-generator -d /path/to/project -f
```

---

## 验证安装

### 检查文件结构

```bash
# 检查 .claude/ 目录
ls -la .claude/

# 应该包含：
# .claude/commands/       - Claude Code 自定义命令
# .claude/templates/      - Wiki 文档模板
# .claude/backups/        - 备份目录

# 检查配置文件
cat wiki-config.json
```

### 测试 Claude Code 命令

```bash
# 在 Claude Code 中运行斜杠命令
/wiki-overview

# 应该生成项目概览文档
```

---

## 常见使用场景

### 场景 1: 新项目初始化

```bash
# 1. 创建新项目
mkdir my-new-project
cd my-new-project

# 2. 初始化 Git 仓库
git init

# 3. 安装 Wiki Generator
uvx wiki-generator

# 4. 生成初始 Wiki 文档
/wiki-overview
/wiki-module src/services

# 5. 提交到 Git
git add .
git commit -m "docs: 初始化 Wiki 文档"
```

### 场景 2: 更新 Wiki 命令

```bash
# 检查当前版本
wiki-generator --version

# 更新到最新版本
pip install --upgrade wiki-generator

# 重新安装（覆盖已存在文件）
wiki-generator --force
```

### 场景 3: 多项目配置

```bash
# 项目 A：输出到 docs/
cd /path/to/project-a
wiki-generator
# 输出文档到 docs/ 目录

# 项目 B：输出到 zh/content/
cd /path/to/project-b
wiki-generator
# 编辑 wiki-config.json，修改 output_dir 为 "zh/content"
```

---

## 故障排除

### 问题 1: 权限不足

**错误信息**:
```
错误: 目录 '/path/to/project' 无写入权限
```

**解决方案**:
```bash
# 检查目录权限
ls -ld /path/to/project

# 修改权限
chmod u+w /path/to/project

# 或使用 sudo（不推荐）
sudo wiki-generator
```

### 问题 2: 文件已存在

**错误信息**:
```
错误: wiki-config.json 已存在
提示: 使用 --force 选项覆盖
```

**解决方案**:
```bash
# 方式 1: 保留现有配置
# 不做任何操作，现有配置将被保留

# 方式 2: 覆盖现有配置
wiki-generator --force

# 方式 3: 手动备份后覆盖
cp wiki-config.json wiki-config.json.backup
wiki-generator --force
```

### 问题 3: uvx 未找到

**错误信息**:
```
bash: uvx: command not found
```

**解决方案**:
```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 重新加载 shell 配置
source ~/.bashrc  # 或 ~/.zshrc

# 验证安装
uvx --version
```

### 问题 4: Python 版本过低

**错误信息**:
```
错误: 需要 Python 3.11 或更高版本
当前版本: 3.10.12
```

**解决方案**:
```bash
# 使用 pyenv 安装 Python 3.11+
pyenv install 3.11.7
pyenv global 3.11.7

# 或使用 conda
conda create -n py311 python=3.11
conda activate py311

# 验证版本
python --version
```

---

## 下一步

安装完成后，可以：

1. **生成项目概览**: 运行 `/wiki-overview` 生成项目概览文档
2. **生成模块文档**: 运行 `/wiki-module src/services` 为特定模块生成文档
3. **自定义配置**: 编辑 `wiki-config.json` 调整输出目录和质量阈值
4. **查看最佳实践**: 阅读 `.claude/BEST-PRACTICES.md` 了解如何编写高质量文档

---

## 相关资源

- [项目规范](../spec.md)
- [实施计划](./plan.md)
- [API 契约](./contracts/api-contracts.md)
- [数据模型](./data-model.md)
- [项目 README](../../README-WIKI-GENERATOR.md)

---

**快速开始版本**: 1.0.0
**最后更新**: 2026-01-04
