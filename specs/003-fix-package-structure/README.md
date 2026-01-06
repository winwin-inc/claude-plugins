# 修复包结构和打包配置

**功能编号**: 001
**功能名称**: fix-package-structure
**状态**: 🟡 规范完成
**创建日期**: 2025-01-04
**最后更新**: 2025-01-04

---

## 📋 功能概述

修复 wiki-generator Python 包的安装路径和打包配置问题，确保 `uv tool install .` 安装后：
1. 包模块名从 `src` 改为正确的 `wiki_generator`
2. 打包时包含 `.claude` 目录下的所有必需文件（命令和模板）

## 🎯 业务价值

- ✅ **确保安装正确性**：修复模块导入路径问题
- ✅ **包含所有必需文件**：CLI 命令和模板文件正确打包
- ✅ **提高用户体验**：避免安装后导入错误或文件缺失
- ✅ **符合 Python 规范**：使用正确的包命名和结构
- ✅ **支持工具分发**：可通过 PyPI 正确分发和安装

## 📊 成功指标

| 指标 | 目标值 | 当前状态 |
|------|--------|----------|
| 包结构正确性 | 100% | 🟡 待实现 |
| 文件包含完整性 | 100% | 🟡 待实现 |
| 安装成功率 | 100% | 🟡 待实现 |
| 功能可用性 | 100% | 🟡 待实现 |

## 📁 相关文档

- [功能规范](spec.md) - 详细的功能需求和验收标准
- [质量检查清单](checklists/requirements.md) - 规范质量验证结果
- [pyproject.toml](../../pyproject.toml) - 需要更新的配置文件

## 🔧 核心变更

### 1. 包结构重组
```
src/ → wiki_generator/
├── __init__.py  (新增)
├── cli.py
├── core/
├── utils/
└── models/
```

### 2. 打包配置更新
- 包路径：`src` → `wiki_generator`
- 包含文件：添加 `.claude/` 目录下的所有文件
- 入口点：`src.cli:cli` → `wiki_generator.cli:cli`

### 3. 数据文件访问
- 更新 `cli.py` 使用 `importlib.resources` 或 `pkg_resources`
- 确保可从已安装的包中读取 `.claude` 目录

## 📅 实施进度

### 阶段 1：规范制定 ✅
- [x] 创建功能规范
- [x] 质量检查通过
- [x] 明确验收标准

### 阶段 2：实施计划 ⏳
- [ ] 创建详细任务列表
- [ ] 分配实施优先级

### 阶段 3：实施 ⏳
- [ ] 重命名包目录
- [ ] 更新配置文件
- [ ] 修复数据文件访问路径
- [ ] 构建和测试

### 阶段 4：验证 ⏳
- [ ] 本地安装测试
- [ ] 功能完整性测试
- [ ] 多平台兼容性测试

## 🚀 快速开始

### 测试当前问题
```bash
# 安装当前版本
uv tool install .

# 测试模块导入（会失败）
python -c "import wiki_generator"  # ImportError: No module named 'wiki_generator'

# 测试命令行工具（可能失败或文件缺失）
wiki-generator
```

### 实施修复后
```bash
# 重新安装
uv tool install .

# 测试模块导入（应该成功）
python -c "import wiki_generator; print(wiki_generator.__version__)"

# 测试命令行工具
wiki-generator --help

# 测试完整功能
cd /tmp/test-project
wiki-generator  # 应该成功安装 .claude 目录
```

## 🔗 依赖关系

### 前置条件
- Python 3.8+ 环境
- uv 工具已安装
- Git 仓库访问权限

### 相关功能
- 无（独立的基础设施修复）

### 影响范围
- 影响：pyproject.toml, 包目录结构, cli.py
- 不影响：.claude 目录内容，现有功能逻辑

## 📝 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| 1.0.0 | 2025-01-04 | 创建功能规范 | Claude Plugins Team |

---

**最后更新**: 2025-01-04
**维护者**: Repo Wiki Generator 项目团队
