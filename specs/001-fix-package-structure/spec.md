# 功能规范：修复包结构和打包配置

**版本**: 1.0.0
**创建日期**: 2025-01-04
**状态**: 草稿

## 1. 功能概述

### 1.1 简短名称
`fix-package-structure`

### 1.2 功能描述
修复 wiki-generator Python 包的安装路径和打包配置问题。当前 `uv tool install .` 安装后，包结构不正确，导致模块导入路径为 `src` 而非 `wiki_generator`。同时，打包时未包含关键的 `.claude` 目录下的 `commands/wiki-generate.md` 命令文件和 `templates/` 模板目录，导致安装后工具无法正常工作。

### 1.3 业务价值
- **确保安装正确性**：修复后用户安装的工具能够正确导入模块
- **包含所有必需文件**：确保 CLI 命令和模板文件被正确打包
- **提高用户体验**：避免用户安装后遇到导入错误或缺失文件问题
- **符合 Python 打包规范**：使用正确的包命名和结构
- **支持工具分发**：使工具可以通过 PyPI 正确分发和安装

---

## 2. 用户场景与测试

### 2.1 主要用户角色

**角色 1：工具使用者**
- **需求**：通过 `uv tool install wiki-generator` 安装工具后直接使用
- **痛点**：当前安装后遇到模块导入错误，无法运行
- **目标**：安装后工具立即可用，无需手动调整

**角色 2：工具维护者**
- **需求**：构建和分发正确的工具包
- **痛点**：当前打包配置不完整，文件缺失
- **目标**：确保打包后的工具包含所有必需文件

### 2.2 核心用户流程

#### 流程 1：从 PyPI 或本地安装工具

**场景**：开发者发现 wiki-generator 工具，想要安装到自己的环境中

**步骤**：
1. 开发者执行 `uv tool install .`（本地开发）或 `uv tool install wiki-generator`（从 PyPI）
2. uv 工具下载并安装包
3. 安装完成后，执行 `wiki-generator` 命令
4. 工具正常启动并执行安装操作

**预期结果**：
- 包被安装到正确的位置
- 模块可以正确导入（使用 `wiki_generator` 而非 `src`）
- 命令行工具 `wiki-generator` 可用
- 包内包含 `.claude/commands/wiki-generate.md` 和 `.claude/templates/` 目录

**测试场景**：
```bash
# 场景 1：本地安装
uv tool install .
wiki-generator  # 应该成功执行

# 场景 2：验证模块导入
python -c "import wiki_generator; print(wiki_generator.__version__)"  # 应该成功

# 场景 3：验证包含文件
# 检查安装位置包含 .claude 目录
python -c "import wiki_generator; import os; print(os.listdir(os.path.dirname(wiki_generator.__file__)))"
# 应该看到 .claude 目录
```

#### 流程 2：运行工具安装 Claude Code 命令

**场景**：用户在自己的项目目录中运行 wiki-generator 工具来安装命令

**步骤**：
1. 用户在项目目录执行 `wiki-generator`
2. 工具从包内读取 `.claude/` 目录内容
3. 复制 `commands/wiki-generate.md` 和 `templates/` 到当前项目
4. 显示安装成功消息

**预期结果**：
- 工具成功读取包内的 `.claude` 目录
- 所有文件被正确复制到用户项目
- 命令安装后立即可用

**测试场景**：
```bash
# 在测试项目中运行
cd /tmp/test-project
wiki-generator
# 验证 .claude/commands/wiki-generate.md 存在
# 验证 .claude/templates/ 目录存在且包含所有模板文件
```

---

## 3. 功能需求

### 3.1 包结构需求

#### 需求 1：重命名包目录

**描述**：将 `src/` 目录重命名为 `wiki_generator/`，使其符合 Python 包命名规范

**当前状态**：
```
repo-wiki/
├── src/
│   ├── cli.py
│   ├── core/
│   ├── utils/
│   └── models/
└── pyproject.toml  # packages = ["src"]
```

**目标状态**：
```
repo-wiki/
├── wiki_generator/
│   ├── __init__.py
│   ├── cli.py
│   ├── core/
│   ├── utils/
│   └── models/
└── pyproject.toml  # packages = ["wiki_generator"]
```

**变更内容**：
- 将 `src/` 目录重命名为 `wiki_generator/`
- 添加 `wiki_generator/__init__.py` 文件
- 更新 `pyproject.toml` 中的包配置
- 更新 `pyproject.toml` 中的入口点路径
- 更新 `pyproject.toml` 中的 ruff 配置路径

**验收标准**：
- 目录重命名完成
- `__init__.py` 文件存在且包含版本信息
- `import wiki_generator` 成功
- `wiki-generator` 命令行工具可以调用

#### 需求 2：包含 .claude 目录到包中

**描述**：确保打包时包含 `.claude` 目录下的所有必需文件

**当前状态**：
```
[tool.hatch.build.targets.wheel]
packages = ["src"]
```

**目标状态**：
```
[tool.hatch.build.targets.wheel]
packages = ["wiki_generator"]
include = [
    "wiki_generator/**/*.py",
    ".claude/commands/wiki-generate.md",
    ".claude/templates/**",
    ".claude/wiki-config.json",
    ".claude/README.md",
    ".claude/BEST-PRACTICES.md",
]
```

**包含的文件清单**：
1. `.claude/commands/wiki-generate.md` - Wiki 生成命令文件
2. `.claude/templates/*.md.template` - 所有模板文件
3. `.claude/wiki-config.json` - 配置示例
4. `.claude/README.md` - 文档
5. `.claude/BEST-PRACTICES.md` - 最佳实践

**验收标准**：
- 安装后的包中包含 `.claude` 目录
- `commands/wiki-generate.md` 文件存在
- `templates/` 目录包含所有 7 个模板文件
- 配置和文档文件存在

#### 需求 3：修复包数据访问路径

**描述**：更新 CLI 代码，使其能够正确访问包内的 `.claude` 目录

**变更内容**：
- 在 `cli.py` 中使用 `importlib.resources` 或 `pkg_resources` 访问包内数据文件
- 确保代码可以从已安装的包中读取 `.claude` 目录内容

**实现方式**：
```python
# 使用 importlib.resources (Python 3.9+)
from importlib.resources import files

claude_dir = files('wiki_generator') / '.claude'

# 或使用 pkg_resources (兼容性更好)
import pkg_resources
claude_dir = pkg_resources.resource_filename('wiki_generator', '.claude')
```

**验收标准**：
- 安装后的工具能够读取包内的 `.claude` 目录
- 文件复制操作正常工作
- 无路径相关错误

### 3.2 配置文件更新需求

#### 需求 4：更新 pyproject.toml

**描述**：完整更新 `pyproject.toml` 文件以反映新的包结构

**变更项**：
1. **包路径**：
   ```toml
   [tool.hatch.build.targets.wheel]
   packages = ["wiki_generator"]
   ```

2. **包含文件**：
   ```toml
   [tool.hatch.build.targets.wheel]
   include = [
       "wiki_generator/**/*.py",
       ".claude/commands/wiki-generate.md",
       ".claude/templates/**",
       ".claude/*.json",
       ".claude/*.md",
   ]
   ```

3. **入口点**：
   ```toml
   [project.scripts]
   wiki-generator = "wiki_generator.cli:cli"
   ```

4. **Ruff 配置**：
   ```toml
   [tool.ruff]
   src = ["wiki_generator"]
   ```

**验收标准**：
- 配置文件格式正确
- 所有路径引用更新
- 构建工具能够正确识别配置

### 3.3 构建和测试需求

#### 需求 5：验证构建输出

**描述**：确保构建后的 wheel 包包含所有必需文件

**验证步骤**：
1. 清理旧的构建产物：`rm -rf dist/ build/ *.egg-info`
2. 构建包：`uv build`
3. 检查 wheel 内容：`unzip -l dist/wiki_generator-1.0.0-py3-none-any.whl`
4. 验证文件列表包含：
   - `wiki_generator/` 目录及所有 `.py` 文件
   - `.claude/commands/wiki-generate.md`
   - `.claude/templates/` 及所有模板文件
   - 其他配置和文档文件

**验收标准**：
- Wheel 文件成功生成
- 包含所有预期的 Python 模块
- 包含所有 `.claude` 目录下的文件

#### 需求 6：测试安装和运行

**描述**：完整测试从安装到运行的流程

**测试步骤**：
1. 在虚拟环境中安装：`uv tool install .`
2. 测试命令行工具：`wiki-generator --help`
3. 测试模块导入：`python -c "import wiki_generator"`
4. 在测试目录运行：`cd /tmp/test && wiki-generator`
5. 验证文件复制：检查 `.claude/` 目录是否正确创建

**验收标准**：
- 安装过程无错误
- 命令行工具可用
- 模块导入成功
- 文件复制功能正常

---

## 4. 成功标准

### 4.1 可量化指标

| 指标 | 目标值 | 测量方式 |
|------|--------|----------|
| 包结构正确性 | 100% | 模块导入路径验证 |
| 文件包含完整性 | 100% | wheel 内容检查 |
| 安装成功率 | 100% | 在干净环境中安装测试 |
| 功能可用性 | 100% | 命令行工具执行测试 |

### 4.2 质量标准

**包结构质量**：
- 符合 Python 包命名规范
- 使用有意义的包名而非 `src`
- 模块可正确导入

**文件完整性**：
- 所有必需文件被包含在包中
- 文件路径正确
- 无缺失文件

**功能可用性**：
- 安装后工具立即可用
- 所有命令功能正常
- 文件复制操作成功

### 4.3 兼容性标准

**Python 版本兼容**：
- Python 3.8+
- 使用 `importlib.resources` (3.9+) 或 `pkg_resources` (3.8)

**平台兼容**：
- Linux
- macOS
- Windows

**工具兼容**：
- uv (最新版本)
- pip (可选)

---

## 5. 关键实体

### 5.1 包结构实体

**实体名称**: `wiki_generator` package

**属性**:
- 包名：wiki_generator
- 版本：1.0.0
- 主模块：cli.py
- 子模块：core, utils, models
- 数据目录：.claude

**关系**:
- package ← 包含 → modules
- package ← 包含 → data_files
- package ← 提供 → cli_command

### 5.2 数据文件实体

**实体名称**: `.claude` directory resources

**属性**:
- 路径：.claude/
- 命令文件：commands/wiki-generate.md
- 模板目录：templates/*.md.template (7 个文件)
- 配置文件：wiki-config.json
- 文档文件：README.md, BEST-PRACTICES.md

**关系**:
- data_files ← 被使用 → cli_tool
- data_files ← 被复制 → user_project

---

## 6. 假设与约束

### 6.1 假设

1. **环境假设**：
   - 用户已安装 Python 3.8+
   - 用户已安装 uv 工具
   - 用户有写入当前目录的权限

2. **工具假设**：
   - 使用 hatchling 作为构建后端
   - 使用 uv 作为包管理工具
   - 包通过 PyPI 或本地 wheel 分发

3. **代码假设**：
   - 现有代码逻辑无需修改，只需调整路径
   - `.claude` 目录结构不变

### 6.2 约束

1. **命名约束**：
   - 包名必须使用 `wiki_generator`（下划线分隔）
   - 命令行工具名使用 `wiki-generator`（连字符分隔）

2. **结构约束**：
   - 必须包含 `.claude` 目录下的所有文件
   - 不能改变文件相对路径结构

3. **兼容性约束**：
   - 必须支持 Python 3.8+
   - 必须跨平台兼容

4. **性能约束**：
   - 构建时间 < 30 秒
   - 安装时间 < 60 秒

### 6.3 依赖关系

1. **构建依赖**：
   - hatchling >= 1.0.0
   - uv (用于构建和测试)

2. **运行时依赖**：
   - Python 3.8+
   - click >= 8.0.0
   - pyyaml >= 6.0
   - requests >= 2.28.0

---

## 7. 边界与排除

### 7.1 功能边界

**包含**：
- 包目录重命名
- 打包配置更新
- 数据文件访问路径修复
- 构建和安装测试

**不包含**：
- CLI 逻辑修改（除非路径访问相关）
- 新功能开发
- `.claude` 目录结构变更
- 模板文件内容修改

### 7.2 技术边界

**支持**：
- 使用 hatchling 构建系统
- 使用 uv 工具链
- 标准Python包结构

**不支持**：
- 其他构建系统（setuptools、poetry等）
- 修改 Python 版本要求
- 改变依赖库

---

## 8. 风险与缓解

### 8.1 技术风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| 数据文件访问不兼容 | 高 | 低 | 使用兼容性库（pkg_resources） |
| 打包后文件缺失 | 高 | 中 | 严格测试 wheel 内容 |
| 路径引用错误 | 中 | 中 | 全面测试所有代码路径 |

### 8.2 兼容性风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| Python 3.8 兼容性 | 中 | 低 | 测试 Python 3.8 环境 |
| Windows 路径问题 | 中 | 低 | 使用 pathlib 处理路径 |
| 权限问题 | 低 | 低 | 文档说明权限要求 |

---

## 9. 变更影响分析

### 9.1 影响范围

**影响文件**：
1. `pyproject.toml` - 主要配置文件
2. `src/` → `wiki_generator/` - 目录重命名
3. `wiki_generator/__init__.py` - 新增文件
4. `wiki_generator/cli.py` - 可能需要更新路径访问

**不影响**：
- `.claude/` 目录内容
- 现有功能和逻辑
- 文档文件（除非引用了 `src` 路径）

### 9.2 迁移路径

**升级路径**：
1. 重命名目录
2. 更新配置
3. 重新构建
4. 测试安装

**回滚策略**：
- Git 保留旧版本
- 可通过 Git revert 快速回退

---

## 10. 实施检查清单

### 10.1 实施前检查

- [ ] 备份当前代码状态
- [ ] 确认 Git 工作区干净
- [ ] 创建功能分支

### 10.2 实施步骤

- [ ] 步骤 1：重命名 `src/` 为 `wiki_generator/`
- [ ] 步骤 2：创建 `wiki_generator/__init__.py`
- [ ] 步骤 3：更新 `pyproject.toml` 包配置
- [ ] 步骤 4：更新 `pyproject.toml` 包含文件列表
- [ ] 步骤 5：更新 `cli.py` 中的数据文件访问路径
- [ ] 步骤 6：清理构建产物 `rm -rf dist/ build/`
- [ ] 步骤 7：重新构建 `uv build`
- [ ] 步骤 8：检查 wheel 内容
- [ ] 步骤 9：测试本地安装 `uv tool install .`
- [ ] 步骤 10：测试命令行工具 `wiki-generator`
- [ ] 步骤 11：测试文件复制功能
- [ ] 步骤 12：验证所有测试通过

### 10.3 实施后验证

- [ ] 模块导入测试：`python -c "import wiki_generator"`
- [ ] 命令行工具测试：`wiki-generator --help`
- [ ] Wheel 内容检查：确认包含所有文件
- [ ] 完整功能测试：在测试目录运行工具
- [ ] 多平台测试：Linux、macOS、Windows（如可能）

---

## 11. 附录

### 11.1 术语表

| 术语 | 定义 |
|------|------|
| 包目录 (package directory) | Python 包的根目录，包含 `__init__.py` |
| 数据文件 (package data) | 包内包含的非 Python 代码文件 |
| wheel | Python 分发格式，`.whl` 文件 |
| 入口点 (entry point) | 命令行工具与 Python 函数的映射 |
| uv | 现代 Python 包管理工具 |
| hatchling | Python 构建后端 |

### 11.2 参考资料

- [Python 打包用户指南](https://packaging.python.org/)
- [Hatchling 文档](https://hatch.pypa.io/latest/)
- [uv 文档](https://github.com/astral-sh/uv)
- [项目 CLAUDE.md](CLAUDE.md)

### 11.3 相关文件

- [pyproject.toml](../pyproject.toml) - 需要更新的配置文件
- [src/cli.py](../src/cli.py) - 需要更新路径的 CLI 入口
- [.claude/](../.claude/) - 需要包含的数据目录

---

**文档状态**: ✅ 规范完成
**下一步**: 执行实施步骤或创建详细任务列表
**创建日期**: 2025-01-04
**最后更新**: 2025-01-04
**作者**: Repo Wiki Generator 项目团队
