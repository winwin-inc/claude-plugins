# 研究文档：包结构和打包配置修复

**功能**: fix-package-structure
**创建日期**: 2025-01-04
**状态**: ✅ 完成

---

## 1. Python 包命名最佳实践

### 决策：使用 `wiki_generator` 作为包名

**理由**：
- 符合 PEP 8 规范：模块名使用小写字母和下划线
- 避免使用 `src` 作为包名（`src` 通常是布局约定，不是包名）
- 包名应具有描述性，清晰表达包的用途
- 避免与标准库或流行包冲突

**技术参考**：
- [PEP 8 -- Style Guide for Python Code](https://peps.python.org/pep-0008/#package-and-module-names)
- [Python Packaging User Guide](https://packaging.python.org/en/latest/guides/structuring-a-project/)

**替代方案考虑**：
- `wiki_generator` ✅ 已采用（符合规范）
- `wikiGenerator` ❌ 拒绝（驼峰命名不符合 Python 规范）
- `wiki-generator` ❌ 拒绝（连字符不能用作包名）

---

## 2. Python 包数据文件包含最佳实践

### 决策：使用 hatchling 的 `include` 配置

**理由**：
- Hatchling 是现代 Python 构建工具，支持简洁的配置
- 使用 `include` 模式匹配可以精确控制打包内容
- 支持通配符模式（`**`）递归包含目录

**技术参考**：
- [Hatchling Documentation - Build Targets](https://hatch.pypa.io/latest/config/build/)
- [Python Packaging Guide - Package Data](https://packaging.python.org/en/latest/guides/including-data-files/)

**配置方案**：
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

**替代方案考虑**：
- `MANIFEST.in` 文件 ❌ 拒绝（过时，hatchling 不推荐）
- `package-data` in `setup.py` ❌ 拒绝（setuptools 方式，不适用于 hatchling）
- `include` in hatchling ✅ 已采用（现代、简洁）

---

## 3. 运行时访问包数据文件最佳实践

### 决策：使用 `importlib.resources` (Python 3.9+) 和 `pkg_resources` 回退 (Python 3.8)

**理由**：
- `importlib.resources` 是 Python 3.9+ 的标准库，无需额外依赖
- `pkg_resources` (setuptools) 是 Python 3.8 的兼容方案
- 支持从已安装的包中读取数据文件（包括 wheel 安装）
- 跨平台兼容（Windows、macOS、Linux）

**技术参考**：
- [importlib.resources 文档](https://docs.python.org/3.9/library/importlib.html#module-importlib.resources)
- [setuptools - pkg_resources](https://setuptools.pypa.io/en/latest/pkg_resources.html)
- [Python Packaging Guide - Data Files](https://packaging.python.org/en/latest/guides/using-data-files/)

**实现方案**：

```python
# Python 3.9+ 推荐
from importlib.resources import files

claude_dir = files('wiki_generator') / '.claude'

# Python 3.8 兼容
try:
    from importlib.resources import files
except ImportError:
    from pkg_resources import resource_filename
    claude_dir = Path(resource_filename('wiki_generator', '.claude'))
```

**替代方案考虑**：
- `__file__` 相对路径 ❌ 拒绝（wheel 安装后不可靠）
- `pkg_resources` ✅ 已采用（Python 3.8 兼容）
- `importlib.resources` ✅ 已采用（Python 3.9+ 现代方案）

---

## 4. Hatchling 构建配置最佳实践

### 决策：使用 `[tool.hatch.build.targets.wheel]` 配置

**理由**：
- Hatchling 是推荐的现代构建后端
- 配置清晰简洁
- 与 uv 工具链完美集成
- 支持最新的包分发标准

**技术参考**：
- [Hatchling Documentation](https://hatch.pypa.io/latest/)
- [uv - Project Configuration](https://github.com/astral-sh/uv?tab=readme-ov-file#project-configuration)

**关键配置项**：
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["wiki_generator"]
include = [
    "wiki_generator/**/*.py",
    ".claude/commands/wiki-generate.md",
    ".claude/templates/**",
    ".claude/*.json",
    ".claude/*.md",
]

[project.scripts]
wiki-generator = "wiki_generator.cli:cli"
```

**替代方案考虑**：
- `setuptools` ❌ 拒绝（配置复杂，维护成本高）
- `flit` ❌ 拒绝（功能相对受限）
- `poetry` ❌ 拒绝（不兼容 uv 工具链）
- `hatchling` ✅ 已采用（现代、简洁、uv 推荐）

---

## 5. 包数据文件放置位置最佳实践

### 决策：将 `.claude` 目录放在项目根目录，作为包数据包含

**理由**：
- 数据文件与代码分离，结构清晰
- 符合 Python 包数据文件约定
- 方便用户直接访问和修改（开发模式）
- 打包时自动包含到 wheel 中

**技术参考**：
- [Python Packaging Guide - Project Layout](https://packaging.python.org/en/latest/guides/structuring-a-project/#src-layout)
- [Hatchling - Non-Python Files](https://hatch.pypa.io/latest/how-to/config/_build/#including-non-python-files)

**目录结构**：
```
repo-wiki/
├── wiki_generator/          # 包源代码
│   ├── __init__.py
│   ├── cli.py
│   ├── core/
│   ├── utils/
│   └── models/
├── .claude/                 # 数据文件（打包时包含）
│   ├── commands/
│   ├── templates/
│   ├── wiki-config.json
│   ├── README.md
│   └── BEST-PRACTICES.md
├── pyproject.toml
└── README.md
```

**替代方案考虑**：
- 放在 `wiki_generator/.claude/` ❌ 择绝（数据应与代码分离）
- 放在项目根目录 `.claude/` ✅ 已采用（清晰的关注点分离）

---

## 6. 跨平台路径处理最佳实践

### 决策：使用 `pathlib.Path` 处理所有路径操作

**理由**：
- `pathlib` 是 Python 3.4+ 的标准库
- 自动处理 Windows/Linux/macOS 路径分隔符差异
- 面向对象 API，代码更简洁
- 与 `importlib.resources` 集成良好

**技术参考**：
- [pathlib 文档](https://docs.python.org/3/library/pathlib.html)
- [Cross-platform pathlib patterns](https://realpython.com/python-pathlib/)

**实现示例**：
```python
from pathlib import Path
from importlib.resources import files

claude_dir = files('wiki_generator') / '.claude'
commands_dir = claude_dir / 'commands'

# 跨平台路径操作
source_file = commands_dir / 'wiki-generate.md'
target_dir = Path.cwd() / '.claude' / 'commands'
```

**替代方案考虑**：
- `os.path` ❌ 拒绝（过时，API 不一致）
- `pathlib.Path` ✅ 已采用（现代、跨平台）

---

## 7. 构建验证最佳实践

### 决策：使用 `unzip -l` 检查 wheel 内容

**理由**：
- 简单直接，无需额外工具
- 可以验证所有文件是否正确打包
- 支持在 CI/CD 中自动化检查

**验证脚本**：
```bash
# 清理旧构建
rm -rf dist/ build/ *.egg-info

# 构建包
uv build

# 检查 wheel 内容
unzip -l dist/wiki_generator-1.0.0-py3-none-any.whl | grep -E "\.py$|\.claude/|\.md$|\.json$"

# 验证关键文件存在
unzip -l dist/*.whl | grep "wiki_generator/__init__.py"
unzip -l dist/*.whl | grep ".claude/commands/wiki-generate.md"
unzip -l dist/*.whl | grep ".claude/templates/"
```

**技术参考**：
- [Python Packaging Guide - Build and Distribute](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/)

---

## 8. 版本兼容性测试最佳实践

### 决策：使用 `tox` 或手动多版本测试

**理由**：
- 确保在 Python 3.8、3.9、3.10、3.11、3.12 上都能正常工作
- `uv` 可以方便地切换 Python 版本进行测试
- 验证 `importlib.resources` 和 `pkg_resources` 的回退逻辑

**测试脚本**：
```bash
# Python 3.8 测试
python3.8 -m venv venv38
source venv38/bin/activate
uv pip install -e .
python -c "import wiki_generator; print('OK')"

# Python 3.9+ 测试
python3.9 -c "import wiki_generator; print('OK')"
python3.10 -c "import wiki_generator; print('OK')"
python3.11 -c "import wiki_generator; print('OK')"
python3.12 -c "import wiki_generator; print('OK')"
```

---

## 9. 总结：技术决策矩阵

| 决策点 | 选择 | 理由 | 参考 |
|--------|------|------|------|
| 包名 | `wiki_generator` | 符合 PEP 8 规范 | PEP 8 |
| 构建后端 | `hatchling` | 现代、简洁、uv 推荐 | Hatchling 文档 |
| 数据文件包含 | `include` 配置 | 精确控制打包内容 | Hatchling 文档 |
| 数据文件访问 | `importlib.resources` + `pkg_resources` 回退 | 跨版本兼容 | Python 文档 |
| 路径处理 | `pathlib.Path` | 跨平台、现代 API | pathlib 文档 |
| 数据文件位置 | 项目根目录 `.claude/` | 代码与数据分离 | Packaging Guide |
| 构建验证 | `unzip -l` | 简单直接 | Packaging Guide |
| 版本测试 | `uv` + 多版本 Python | 确保兼容性 | uv 文档 |

---

## 10. 待解决问题

### 无未解决问题

✅ 所有关键技术决策已完成，可以进入实施阶段。

---

**文档状态**: ✅ 研究完成
**下一步**: 创建数据模型和接口契约
**创建日期**: 2025-01-04
