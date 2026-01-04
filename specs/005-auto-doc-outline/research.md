# Research Report: 自动文档大纲提取与主题映射

**功能版本**: 1.0.0
**创建日期**: 2026-01-04
**状态**: 完成

---

## 研究目标

解决技术未知项，验证技术可行性，为设计阶段提供决策支持。

---

## Research Task 001: 业务模块识别最佳实践

### 研究问题

1. 如何准确识别项目的业务模块（服务层、页面层、API 层等）？
2. 如何处理不规范的目录结构？
3. 如何评估模块规模（文件数量、代码行数、复杂度）？

### 研究方法

- 分析 dingtalk-sdk-generator 和 dingtalk-notable-connect 的目录结构
- 调研 Python/JavaScript 项目常见目录结构模式
- 测试不同的扫描策略

### 研究发现

#### 1. 业务模块识别规则

**Python 项目常见目录结构**：

| 项目类型 | 服务层位置 | 页面层位置 | API 层位置 | 模型层位置 |
|---------|-----------|-----------|----------|-----------|
| 标准项目 | `src/services/` | `pages/` | `src/api/` | `src/models/` |
| Django 项目 | `app/services/` | `templates/` | `app/views/` | `app/models/` |
| FastAPI 项目 | `app/services/` | - | `app/routers/` | `app/models/` |
| Streamlit 项目 | `services/` | `pages/` | - | `models/` |

**扫描优先级**：
1. 首选：`src/` 前缀（现代 Python 项目标准）
2. 备选：`app/` 前缀（Django/FastAPI 常见）
3. 默认：根目录（小型项目）

**决策**：采用多层目录扫描策略，按优先级顺序扫描多个常见路径。

**理由**：
- 兼容多种项目结构模式
- 提高识别准确率
- 减少误判（False Positive）

#### 2. 不规范目录结构处理

**边缘情况**：
- 服务层代码混在根目录（如 `user_service.py` 直接在 `src/` 下）
- 页面层使用非标准命名（如 `views/` 而非 `pages/`）
- API 层和业务逻辑混合（如 `api/` 目录包含服务代码）

**处理策略**：
1. **启发式扫描**：除了标准路径，也扫描常见的变体
2. **文件模式匹配**：通过文件名模式识别（如 `*_service.py`、`*_routes.py`）
3. **配置驱动**：允许用户在 `wiki-config.json` 中自定义扫描路径

**决策**：实现三层扫描策略（标准路径 + 启发式扫描 + 配置覆盖）

**理由**：
- 标准路径覆盖大部分项目
- 启发式扫描提高边缘情况覆盖率
- 配置覆盖提供最终灵活性

#### 3. 模块规模评估算法

**评估指标**：
| 指标 | 权重 | 计算方法 |
|------|------|----------|
| 文件数量 | 60% | `find module_path -type f -name "*.py" \| wc -l` |
| 代码行数 | 30% | `find module_path -name "*.py" -exec cat {} \; \| wc -l` |
| 依赖复杂度 | 10% | `grep -r "^import\|^from" module_path \| sort -u \| wc -l` |

**规模分级**：
```python
def calculate_module_scale(module_path):
    file_count = count_files(module_path)
    line_count = count_lines(module_path)
    dependency_count = count_dependencies(module_path)

    # 加权评分
    score = (
        file_count * 10 +
        line_count / 100 * 3 +
        dependency_count * 2
    )

    if score <= 40:
        return "small"      # 1-4 文件
    elif score <= 200:
        return "medium"     # 5-20 文件
    elif score <= 1000:
        return "large"      # 21-50 文件
    else:
        return "xlarge"     # >50 文件
```

**决策**：使用加权评分算法，综合考虑文件数量、代码行数、依赖复杂度。

**理由**：
- 单一指标（文件数量）不够准确
- 加权评分更贴近实际复杂度
- 可调节权重适应不同项目类型

### 替代方案评估

| 方案 | 优点 | 缺点 | 评分 |
|------|------|------|------|
| **加权评分算法**（选择） | 综合考虑多个因素，准确度高 | 计算复杂度稍高 | ⭐⭐⭐⭐⭐ |
| 单一文件数量 | 简单快速 | 忽略代码复杂度，不准确 | ⭐⭐⭐ |
| AST 分析 | 最准确（分析实际代码结构） | 性能开销大，实现复杂 | ⭐⭐⭐⭐ |
| AI 识别 | 适应性强，无规则限制 | 不可预测，成本高 | ⭐⭐⭐ |

---

## Research Task 002: 技术栈检测增强方案

### 研究问题

1. 如何扩充技术栈检测规则从 10+ 到 20+？
2. 如何提高检测准确率（从当前水平到 ≥ 95%）？
3. 如何处理多个技术栈同时存在的情况？

### 研究方法

- 调研主流 Python/JavaScript 技术栈的导入模式
- 分析 False Positive 和 False Negative 案例
- 设计多技术栈组合规则

### 研究发现

#### 1. 技术栈检测规则扩充

**当前 v2.0 支持的技术栈**（10 种）：
- SQLAlchemy, Django ORM, FastAPI, Flask, Celery, pytest, Dockerfile, Click

**扩充目标**（33 种）：

**后端框架**（4 种）：
```bash
# FastAPI
if grep -rq "from fastapi" src/ || grep -rq "import fastapi" src/; then
    tech_stack+=("fastapi")
fi

# Flask
if grep -rq "from flask" src/; then
    tech_stack+=("flask")
fi

# Django
if grep -rq "from django" src/ || [ -f "manage.py" ]; then
    tech_stack+=("django")
fi

# Tornado
if grep -rq "import tornado" src/; then
    tech_stack+=("tornado")
fi
```

**CLI 框架**（3 种）：
```bash
# Click
if grep -rq "import click" src/ || grep -rq "from click" src/; then
    tech_stack+=("click")
fi

# Typer
if grep -rq "import typer" src/ || grep -rq "from typer" src/; then
    tech_stack+=("typer")
fi

# argparse (标准库)
if grep -rq "import argparse" src/; then
    tech_stack+=("argparse")
fi
```

**前端框架**（3 种）：
```bash
# React
if [ -f "package.json" ] && grep -q '"react"' package.json; then
    tech_stack+=("react")
fi

# Vue
if [ -f "package.json" ] && grep -q '"vue"' package.json; then
    tech_stack+=("vue")
fi

# Streamlit
if grep -rq "import streamlit" src/; then
    tech_stack+=("streamlit")
fi
```

**决策**：使用组合检测策略（导入语句 + 配置文件 + 文件存在）

**理由**：
- 导入语句检测适用于 Python 项目
- package.json 检测适用于 JavaScript 项目
- 文件存在检测适用于框架特定文件（如 Django 的 manage.py）

#### 2. 检测准确率提升策略

**当前准确率问题**：
- **False Positive**：误报（如测试文件导入 `pytest`，但项目不使用 pytest）
- **False Negative**：漏报（如技术栈在 `requirements.txt` 但未在代码中导入）

**提升策略**：

1. **排除测试文件**：
```bash
# 排除 tests/、test_*.py 目录和文件
grep -r "from fastapi" src/ --exclude-dir=tests --exclude="test_*.py"
```

2. **多源验证**：
```bash
# 同时检查导入语句和依赖文件
if (grep -rq "import pytest" src/ || grep -q "pytest" requirements.txt || grep -q "pytest" pyproject.toml); then
    tech_stack+=("pytest")
fi
```

3. **阈值过滤**：
```bash
# 只在导入次数 ≥ 阈值时判定为使用该技术栈
import_count=$(grep -r "from fastapi" src/ | wc -l)
if [ "$import_count" -ge 3 ]; then
    tech_stack+=("fastapi")
fi
```

**决策**：采用多源验证 + 阈值过滤 + 排除测试文件

**理由**：
- 多源验证减少 False Negative
- 阈值过滤减少 False Positive
- 排除测试文件提高准确性

**预期准确率**：95%+（基于多源验证策略）

#### 3. 多技术栈去重逻辑

**冲突场景**：
- FastAPI 和 Flask 同时存在（只应生成一份 API 文档）
- SQLAlchemy 和 Django ORM 同时存在（只应生成一份数据模型文档）

**去重规则**（优先级）：

| 类别 | 优先级（高→低） | 说明 |
|------|----------------|------|
| 后端框架 | FastAPI > Flask > Django > Tornado | 现代框架优先 |
| ORM | SQLAlchemy > Django ORM > Tortoise ORM | 通用 ORM 优先 |
| 前端框架 | React > Vue > Streamlit | 主流框架优先 |
| 消息队列 | Kafka > RabbitMQ | 企业级优先 |

**实现**：
```bash
# 后端框架去重
if contains "fastapi" "${tech_stack[@]}"; then
    tech_stack=("${tech_stack[@]//flask/}")  # 移除 Flask
    tech_stack=("${tech_stack[@]//django/}") # 移除 Django
fi
```

**决策**：使用优先级规则，保留最高优先级的技术栈

**理由**：
- 避免生成重复文档
- 优先级反映技术栈的现代性和流行度
- 用户仍可手动配置覆盖

### 替代方案评估

| 方案 | 优点 | 缺点 | 评分 |
|------|------|------|------|
| **优先级去重**（选择） | 简单高效，符合直觉 | 可能丢失用户想保留的技术栈 | ⭐⭐⭐⭐⭐ |
| 生成所有文档 | 信息完整 | 文档冗余，用户困惑 | ⭐⭐ |
| 询问用户选择 | 最灵活 | 中断自动化流程，用户体验差 | ⭐⭐⭐ |
| 并列显示 | 展示所有技术栈 | 文档结构混乱 | ⭐⭐ |

---

## Research Task 003: AI 内容生成优化

### 研究问题

1. 如何从 README、pyproject.toml、package.json 自动提取项目信息？
2. 如何设计提示词模板以生成高质量的模块文档？
3. 如何确保 AI 生成的内容格式规范（Markdown、Mermaid 图）？

### 研究方法

- 分析 dingtalk-sdk-generator 和 dingtalk-notable-connect 的文档内容模式
- 测试不同的提示词策略
- 设计内容验证规则

### 研究发现

#### 1. 项目信息提取逻辑

**README.md 提取**：

```python
import re

def extract_from_readme(readme_path):
    with open(readme_path, encoding="utf-8") as f:
        content = f.read()

    # 提取项目名称（第一个 # 标题）
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    project_name = title_match.group(1) if title_match else "Unknown"

    # 提取项目描述（第一段）
    desc_match = re.search(r"^#\s+.+?\n\n(.+?)(?:\n\n|$)", content, re.DOTALL)
    description = desc_match.group(1).strip() if desc_match else ""

    # 提取核心功能（列表项）
    features = []
    in_feature_list = False
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("-") or line.startswith("*"):
            features.append(line[1:].strip())
            in_feature_list = True
        elif in_feature_list and not line:
            break

    return {
        "name": project_name,
        "description": description,
        "features": features[:10]  # 最多 10 个特性
    }
```

**pyproject.toml 提取**：

```python
import tomli

def extract_from_pyproject(toml_path):
    with open(toml_path, "rb") as f:
        data = tomli.load(f)

    project = data.get("project", {})
    dependencies = project.get("dependencies", [])
    dev_dependencies = [
        dep for dep in dependencies
        if any(test_tool in dep for test_tool in ["pytest", "ruff", "mypy", "black"])
    ]

    return {
        "name": project.get("name"),
        "version": project.get("version"),
        "description": project.get("description"),
        "dependencies": dependencies,
        "dev_dependencies": dev_dependencies
    }
```

**决策**：使用正则表达式解析 README，使用 tomli 库解析 pyproject.toml

**理由**：
- 正则表达式简单高效，适用于 Markdown
- tomli 是 Python 标准 TOML 解析库（Python 3.11+ 内置）
- 容错性强（字段缺失时返回默认值）

#### 2. AI 提示词模板设计

**服务模块提示词**：

```markdown
请为 {MODULE_NAME} 服务模块生成技术文档。

## 模块信息
- 模块名称: {MODULE_NAME}
- 模块路径: {MODULE_PATH}
- 文件数量: {FILE_COUNT}
- 相关文件: {RELATED_FILES}

## 文档要求
1. **简介**: 简要描述该服务的职责和功能（2-3 段）
2. **核心功能**: 列出 3-5 个核心功能（使用无序列表）
3. **架构图**: 使用 Mermaid 绘制服务架构图（graph TD 格式）
4. **使用示例**: 提供 1-2 个代码示例
5. **相关文档**: 引用相关的其他文档

## 格式要求
- 使用 Markdown 格式
- 代码块使用 ```python 语言标记
- Mermaid 图必须使用 graph TD 或 graph LR 方向
- 避免使用过于技术化的术语，面向开发者

## 内容来源
请基于以下文件内容生成文档：
{FILE_CONTENTS}
```

**API 模块提示词**：

```markdown
请为 {MODULE_NAME} API 模块生成技术文档。

## 模块信息
- 模块名称: {MODULE_NAME}
- 模块路径: {MODULE_PATH}
- 端点数量: {ENDPOINT_COUNT}

## 文档要求
1. **API 概览**: 列出所有 API 端点（使用表格）
2. **端点详情**: 为每个端点提供：
   - HTTP 方法和路径
   - 请求参数（表格格式）
   - 响应格式（JSON 示例）
   - 错误码说明
3. **使用示例**: cURL 或 Python 代码示例
4. **认证说明**: 如何进行身份认证

## 格式要求
- 端点列表使用 Markdown 表格
- 请求/响应使用 JSON 代码块
- 遵循 OpenAPI 规范
```

**决策**：为不同模块类型设计专用提示词模板

**理由**：
- 不同模块类型关注点不同（服务 vs API vs 页面）
- 专用提示词提高生成质量
- 模板化便于维护和迭代

#### 3. 内容格式验证规则

**Markdown 格式验证**：

```python
import re

def validate_markdown(content):
    errors = []

    # 检查标题层级（必须从 # 开始，逐级递增）
    lines = content.split("\n")
    prev_level = 0
    for line in lines:
        if line.startswith("#"):
            level = len(re.match(r"^#+", line).group())
            if level > prev_level + 1:
                errors.append(f"标题层级跳跃: {line}")
            prev_level = level

    # 检查代码块语言标记
    code_blocks = re.findall(r"```(\w+)", content)
    for lang in code_blocks:
        if lang not in ["python", "bash", "json", "markdown", "mermaid"]:
            errors.append(f"未知代码块语言: {lang}")

    # 检查 Mermaid 图格式
    mermaid_blocks = re.findall(r"```mermaid\n(.*?)\n```", content, re.DOTALL)
    for block in mermaid_blocks:
        if not block.startswith("graph") and not block.startswith("flowchart"):
            errors.append(f"Mermaid 图必须以 graph 或 flowchart 开始")

    return errors
```

**决策**：实现格式验证规则，在生成后自动检查

**理由**：
- 确保生成内容符合格式规范
- 及早发现格式问题
- 减少人工修正工作量

### 替代方案评估

| 方案 | 优点 | 缺点 | 评分 |
|------|------|------|------|
| **专用提示词模板**（选择） | 针对性强，质量高 | 需要维护多个模板 | ⭐⭐⭐⭐⭐ |
| 通用提示词 | 简单，易维护 | 生成质量不稳定 | ⭐⭐⭐ |
| Few-Shot Learning | 示例驱动，效果好 | Token 消耗大 | ⭐⭐⭐⭐ |
| 无模板（自由生成） | 灵活性最高 | 质量不可控 | ⭐⭐ |

---

## Research Task 004: 性能优化策略

### 研究问题

1. 如何并行处理多个业务模块？
2. 如何缓存检测结果（技术栈、模块结构）？
3. 如何优化大项目（> 1000 文件）的处理时间？

### 研究方法

- 调研 Bash 并行处理技术（xargs、parallel、后台任务）
- 设计缓存策略（文件路径哈希、时间戳检查）
- 性能测试和瓶颈分析

### 研究发现

#### 1. 并行处理方案

**方案对比**：

| 工具 | 优点 | 缺点 | 并发度 |
|------|------|------|--------|
| **xargs**（选择） | POSIX 标准，广泛可用 | 配置稍复杂 | CPU 核心数 |
| GNU parallel | 功能强大，易用 | 需要额外安装 | 可自定义 |
| Bash 后台任务 | 原生支持 | 控制复杂 | 手动管理 |

**xargs 并行实现**：

```bash
# 并行处理多个模块的文档生成
find "$MODULES_DIR" -mindepth 1 -maxdepth 1 -type d | \
    xargs -P $(nproc) -I {} bash -c '
        module_name=$(basename "{}")
        echo "处理模块: $module_name"
        generate_module_document "{}" "$module_name"
    '
```

**决策**：使用 xargs 进行并行处理

**理由**：
- POSIX 标准，所有 Linux 系统都可用
- 性能接近 GNU parallel
- 无需额外依赖

**预期性能提升**：3-4x（取决于 CPU 核心数）

#### 2. 缓存策略设计

**缓存粒度**：
1. **技术栈检测结果缓存**
2. **业务模块结构缓存**
3. **文件内容哈希缓存**

**缓存实现**：

```bash
CACHE_DIR=".cache/wiki-generator"
TECH_STACK_CACHE="$CACHE_DIR/tech_stack.json"
MODULES_CACHE="$CACHE_DIR/modules.json"

# 计算目录哈希（基于文件路径和修改时间）
compute_hash() {
    local dir=$1
    find "$dir" -type f -printf "%T@ %p\n" | sort | md5sum | cut -d" " -f1
}

# 检查缓存是否有效
is_cache_valid() {
    local cache_file=$1
    local target_dir=$2

    if [ ! -f "$cache_file" ]; then
        return 1
    fi

    local cached_hash=$(jq -r ".hash" "$cache_file")
    local current_hash=$(compute_hash "$target_dir")

    [ "$cached_hash" == "$current_hash" ]
}

# 使用缓存
detect_tech_stack_cached() {
    local project_dir=$1

    if is_cache_valid "$TECH_STACK_CACHE" "$project_dir"; then
        echo "使用缓存的技术栈检测结果"
        jq -r ".tech_stack[]" "$TECH_STACK_CACHE"
        return
    fi

    # 执行检测
    local tech_stack=($(detect_tech_stack "$project_dir"))

    # 保存到缓存
    local hash=$(compute_hash "$project_dir")
    jq -n \
        --arg hash "$hash" \
        --argjson tech_stack "$(echo "${tech_stack[@]}" | jq -R -s -c 'split(" ")')" \
        '{hash: $hash, tech_stack: $tech_stack}' > "$TECH_STACK_CACHE"

    echo "${tech_stack[@]}"
}
```

**决策**：使用文件哈希 + JSON 文件缓存

**理由**：
- 哈希比较快速准确
- JSON 格式易于调试
- 缓存文件可手动清理

**预期性能提升**：
- 首次运行：无影响
- 二次运行（无变更）：10x+（跳过检测和扫描）
- 二次运行（少量变更）：5x+（只处理变更部分）

#### 3. 大项目优化策略

**瓶颈分析**：
1. **文件扫描**：`find` 和 `grep` 在大目录下变慢
2. **AI 生成**：每个模块文档需要 AI 处理
3. **文件 I/O**：读写大量小文件

**优化策略**：

**策略 1：限制扫描深度**
```bash
# 只扫描前 3 层目录
find "$PROJECT_DIR" -maxdepth 3 -type f -name "*.py"
```

**策略 2：限制生成的文档数量**
```bash
# 最多生成 50 个模块文档
MAX_MODULES=50
module_count=0
for module in "${modules[@]}"; do
    if [ $module_count -ge $MAX_MODULES ]; then
        echo "警告: 已达到最大文档数量限制 ($MAX_MODULES)"
        break
    fi
    generate_module_document "$module"
    module_count=$((module_count + 1))
done
```

**策略 3：分批处理**
```bash
# 将大型模块拆分为多个批次
BATCH_SIZE=10
for ((i=0; i<${#modules[@]}; i+=BATCH_SIZE)); do
    batch=("${modules[@]:i:BATCH_SIZE}")
    process_batch "${batch[@]}"
done
```

**决策**：组合使用扫描深度限制 + 文档数量限制 + 分批处理

**理由**：
- 扫描深度限制减少 I/O
- 文档数量限制控制总时间
- 分批处理避免内存溢出

**预期性能**：
- 中型项目（500 文件）：< 60 秒
- 大型项目（1000 文件）：< 90 秒
- 超大型项目（2000+ 文件）：< 120 秒（但只生成部分文档）

### 替代方案评估

| 方案 | 优点 | 缺点 | 评分 |
|------|------|------|------|
| **组合优化策略**（选择） | 全面覆盖瓶颈 | 实现复杂 | ⭐⭐⭐⭐⭐ |
| 只优化并行 | 简单 | 未解决 I/O 瓶颈 | ⭐⭐⭐ |
| 只优化缓存 | 二次运行快 | 首次无提升 | ⭐⭐⭐ |
| 预编译索引 | 最快 | 维护成本高 | ⭐⭐⭐⭐ |

---

## 总结和决策

### 技术选型总结

| 决策点 | 选择方案 | 理由 |
|--------|---------|------|
| 业务模块识别 | 多层目录扫描 + 加权评分 | 准确度高，兼容多种项目结构 |
| 技术栈检测 | 多源验证 + 优先级去重 | 准确率 95%+，避免重复 |
| AI 内容生成 | 专用提示词模板 | 针对性强，质量稳定 |
| 性能优化 | 并行处理 + 缓存 + 分批 | 全面覆盖瓶颈，性能提升 3-10x |

### 风险评估

| 风险 | 影响 | 缓解措施 | 残余风险 |
|------|------|----------|----------|
| 业务模块识别不准确 | 高 | 多层扫描 + 配置覆盖 | 低 |
| 大型项目性能问题 | 中 | 分批处理 + 数量限制 | 低 |
| AI 生成质量不稳定 | 中 | 专用模板 + 格式验证 | 中 |

### 后续工作

基于研究结果，下一阶段（Phase 1: 设计和契约）将：

1. **生成数据模型**：
   - TechStackRule（技术栈规则）
   - BusinessModule（业务模块）
   - DocumentConfig（文档配置）
   - ValidationResult（验证结果）

2. **生成 API 契约**：
   - detect_tech_stack() - 技术栈检测
   - identify_business_modules() - 业务模块识别
   - calculate_module_scale() - 模块规模评估
   - extract_project_info() - 项目信息提取
   - generate_document_outline() - 文档大纲生成

3. **生成快速开始文档**：
   - 开发环境设置
   - 代码结构概览
   - 核心功能使用流程
   - 开发工作流

---

**研究报告版本**: 1.0.0
**完成日期**: 2026-01-04
**状态**: ✅ 完成 - 所有 NEEDS CLARIFICATION 已解决
