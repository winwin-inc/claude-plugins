# 验证 .claude 目录位置修复

## 修复内容

已将 `.claude/` 目录从项目根目录移到 `wiki_generator/` 包内。

### 目录结构变更

```
修改前:
repo-wiki/
├── .claude/              # ❌ 在项目根目录
│   ├── commands/
│   └── templates/
└── wiki_generator/

修改后:
repo-wiki/
└── wiki_generator/
    ├── .claude/          # ✅ 在包内
    │   ├── commands/
    │   └── templates/
    ├── core/
    ├── models/
    └── utils/
```

### 打包后的目录结构

```
安装位置: .../site-packages/wiki_generator/

wiki_generator/
├── __init__.py
├── cli.py
├── __main__.py
├── .claude/              # ✅ .claude 现在在这里
│   ├── commands/
│   │   └── wiki-generate.md
│   ├── templates/
│   │   ├── overview.md.template
│   │   └── ...
│   ├── BEST-PRACTICES.md
│   ├── README.md
│   └── wiki-config.json
├── core/
├── models/
└── utils/
```

---

## 测试步骤

### 1. 验证当前代码（开发模式）

```bash
cd /home/yewenbin/work/ai/claude/repo-wiki

python3 -c "
import sys
sys.path.insert(0, '.')
from wiki_generator.cli import get_package_claude_dir
claude_dir = get_package_claude_dir()
print(f'✓ .claude 目录: {claude_dir}')
print(f'✓ 目录存在: {claude_dir.exists()}')
print(f'✓ commands/ 存在: {(claude_dir / \"commands\").exists()}')
print(f'✓ templates/ 存在: {(claude_dir / \"templates\").exists()}')
"
```

**预期输出**:
```
✓ .claude 目录: /home/yewenbin/work/ai/claude/repo-wiki/wiki_generator/.claude
✓ 目录存在: True
✓ commands/ 存在: True
✓ templates/ 存在: True
```

### 2. 构建 wheel 包

```bash
# 清理旧构建
rm -rf dist/ build/ *.egg-info

# 构建
uv build
```

**预期输出**:
```
Built wheel: dist/wiki_generator-1.0.0-py3-none-any.whl
```

### 3. 验证 wheel 内容

```bash
# 方法 1: 使用测试脚本
python3 test_build.py

# 方法 2: 手动检查
unzip -l dist/*.whl | grep ".claude"
```

**预期结果**:
```
wiki_generator/.claude/README.md
wiki_generator/.claude/BEST-PRACTICES.md
wiki_generator/.claude/wiki-config.json
wiki_generator/.claude/commands/wiki-generate.md
wiki_generator/.claude/templates/overview.md.template
wiki_generator/.claude/templates/module.md.template
...
```

**关键点**: 路径应该是 `wiki_generator/.claude/`，而不是 `.claude/`

### 4. 安装并测试

```bash
# 重新安装
uv tool install . --force

# 测试版本命令
wiki-generator --version
```

**预期输出**:
```
wiki-generator version 1.0.0
```

### 5. 测试文件复制功能

```bash
# 创建测试项目
cd /tmp
rm -rf test-project
mkdir test-project && cd test-project
git init

# 运行安装命令
wiki-generator

# 验证文件已复制
ls -la .claude/
ls -la .claude/commands/
cat .claude/commands/wiki-generate.md | head -10
```

**预期结果**:
```
.claude/
├── commands/
│   └── wiki-generate.md
├── templates/
│   ├── overview.md.template
│   └── ...
├── BEST-PRACTICES.md
├── README.md
└── wiki-config.json
```

---

## 关键改进

### 代码简化

**修改前**（复杂）:
```python
# 包数据文件访问（跨 Python 版本兼容）
try:
    from importlib.resources import files as _files
    def _get_package_data(path: str) -> Path:
        return Path(str(_files('wiki_generator') / path))
except ImportError:
    from pkg_resources import resource_filename
    def _get_package_data(path: str) -> Path:
        return Path(resource_filename('wiki_generator', path))

def get_package_claude_dir():
    # 双路径访问逻辑
    try:
        claude_dir = _get_package_data('.claude')
        if claude_dir.exists():
            return claude_dir
    except Exception:
        pass

    project_root = Path(__file__).parent.parent.resolve()
    claude_dir = project_root / ".claude"
    ...
```

**修改后**（简洁）:
```python
def get_package_claude_dir():
    """获取 wiki-generator 包内的 .claude/ 目录路径"""
    package_dir = Path(__file__).parent.resolve()
    claude_dir = package_dir / ".claude"
    return claude_dir
```

### 配置简化

**修改前**:
```toml
[tool.hatch.build]
include = [
    "wiki_generator/**/*.py",
    ".claude/**/*",
]

[tool.hatch.build.targets.wheel]
packages = ["wiki_generator"]
```

**修改后**:
```toml
[tool.hatch.build.targets.wheel]
packages = ["wiki_generator"]
```

**原因**: `.claude/` 现在在 `wiki_generator/` 内部，会自动包含在包中。

---

## 优势

1. **路径一致性**: 开发模式和安装模式路径相同
2. **代码简化**: 不需要复杂的双路径逻辑
3. **配置简化**: 不需要特殊的 include 配置
4. **符合惯例**: 包内资源文件通常放在包目录内
5. **易于维护**: 结构更清晰，更容易理解

---

## Git 提交

```
8e40c7b fix: 将 .claude 目录移到 wiki_generator 包内
```

**文件变更**:
- 9 个文件移动（.claude → wiki_generator/.claude）
- 3 个文件修改（README.md, pyproject.toml, cli.py）
- 新增: 0
- 删除: 0

---

**验证日期**: 2025-01-04
**提交版本**: 8e40c7b
