# Quick Start: 自动文档大纲提取开发指南

**功能版本**: 1.0.0
**创建日期**: 2026-01-04
**目标读者**: 开发者

---

## 开发环境设置

### 前置要求

- Python 3.8+
- Git
- Make（可选）
- Claude Code（用于测试）

### 环境初始化

```bash
# 克隆仓库
git clone https://github.com/winwin-inc/claude-plugins.git
cd claude-plugins

# 切换到功能分支
git checkout 5-auto-doc-outline

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装开发依赖
uv pip install -e ".[dev]"
```

### 验证安装

```bash
# 运行测试
pytest tests/test_v2/ -v

# 检查代码质量
ruff check wiki_generator/
```

---

## 代码结构概览

### 新增文件

```
wiki_generator/
├── core/
│   ├── module_scanner.py       # 业务模块扫描器（新增）
│   ├── tech_detector.py         # 技术栈检测器（新增）
│   └── info_extractor.py        # 项目信息提取器（新增）
├── models/
│   └── auto_outline_models.py   # 自动大纲数据模型（新增）
└── .claude/
    └── commands/
        └── wiki-generate.md      # 集成所有新功能（修改）
```

### 修改文件

```
wiki_generator/
├── models/
│   └── config_models.py         # 添加新的数据模型
└── .claude/
    └── commands/
        └── wiki-generate.md      # 集成新功能
```

---

## 核心功能使用流程

### 1. 技术栈检测

```bash
# 在项目根目录运行
wiki-generator --detect-tech-stack

# 或在 wiki-generate.md 中调用
detect_tech_stack "$(pwd)"
```

**输出示例**：
```
检测到的技术栈:
- FastAPI (后端框架)
- SQLAlchemy (ORM)
- pytest (测试框架)
```

### 2. 业务模块识别

```bash
# 识别所有业务模块
wiki-generator --identify-modules

# 识别特定类型的模块
wiki-generator --identify-modules --type service
```

**输出示例**：
```
检测到的业务模块 (5 个):
- 用户管理服务 (medium, 2 层)
- 数据库服务 (small, 1 层)
- 缓存服务 (small, 1 层)
- API 路由 (large, 3 层)
- 数据模型 (medium, 2 层)
```

### 3. 生成文档

```bash
# 在 Claude Code 中运行
/wiki-generate --full
```

**生成文档**：
- 必需文档（10 个）
- 条件文档（根据技术栈）
- 业务模块文档（根据检测到的模块）

---

## 开发工作流

### 1. 单元测试编写

```bash
# 创建测试文件
touch tests/test_v2/test_auto_outline.py

# 编写测试用例
def test_detect_tech_stack():
    """测试技术栈检测"""
    project_path = Path("/path/to/fastapi/project")
    tech_stack = detect_tech_stack(project_path)

    assert "fastapi" in tech_stack
    assert "sqlalchemy" in tech_stack

# 运行测试
pytest tests/test_v2/test_auto_outline.py -v
```

### 2. 集成测试编写

```bash
# 创建集成测试文件
touch tests/test_v2/integration/test_auto_outline_integration.py

# 编写端到端测试
def test_full_workflow():
    """测试完整文档生成流程"""
    # 1. 技术栈检测
    tech_stack = detect_tech_stack(test_project)
    assert len(tech_stack) > 0

    # 2. 业务模块识别
    modules = identify_business_modules(test_project, "service")
    assert len(modules) > 0

    # 3. 文档生成
    config = DocumentConfig(...)
    outline = generate_document_outline(config, modules)
    assert len(outline["business_module_documents"]) > 0

# 运行集成测试
pytest tests/test_v2/integration/test_auto_outline_integration.py -v
```

### 3. 代码提交规范

```bash
# 格式化代码
ruff format wiki_generator/

# 检查代码
ruff check wiki_generator/

# 提交变更
git add .
git commit -m "✨ feat: 实现业务模块识别功能

- 添加 module_scanner.py 模块
- 实现 identify_business_modules() 函数
- 支持服务层、页面层、API 层、模型层识别
- 添加单元测试和集成测试

测试覆盖: 85%
性能目标: < 30 秒（大型项目）

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## 调试技巧

### 启用详细日志

```bash
# 在 wiki-generate.md 中设置
set -x  # 启用 Bash 调试模式

# 或使用 --verbose 选项
/wiki-generate --full --verbose
```

### 查看中间结果

```bash
# 查看技术栈检测结果
cat .cache/wiki-generator/tech_stack.json

# 查看业务模块结构
cat .cache/wiki-generator/modules.json

# 查看文档大纲
cat docs/outline.json
```

### 性能分析

```bash
# 使用 time 命令测量执行时间
time /wiki-generate --full

# 使用 Bash 内置 time
export BASH_TIME_FORMAT="%E"
time wiki-generator --detect-tech-stack
```

---

## 常见问题

### Q: 技术栈检测不准确？

**A**: 检查以下几点：
1. 是否排除了测试文件和目录？
2. 是否使用了多源验证（导入 + 配置文件）？
3. 是否应用了阈值过滤？

### Q: 业务模块识别遗漏？

**A**: 尝试以下方法：
1. 检查项目是否遵循标准目录结构
2. 使用 `--scan-depth` 增加扫描深度
3. 在 `wiki-config.json` 中手动指定扫描路径

### Q: 文档生成时间过长？

**A**: 优化策略：
1. 启用缓存（`--enable-cache`）
2. 限制生成的文档数量（`--max-modules 50`）
3. 增加并行度（`--parallel-workers 4`）

---

## 相关文档

- [功能规范](spec.md) - 完整的功能需求
- [实施计划](plan.md) - 详细的实施步骤
- [研究报告](research.md) - 技术决策和最佳实践
- [数据模型](data-model.md) - 核心数据实体
- [API 契约](contracts/api-contracts.md) - 内部 API 定义

---

**快速开始版本**: 1.0.0
**最后更新**: 2026-01-04
**状态**: ✅ 完成
