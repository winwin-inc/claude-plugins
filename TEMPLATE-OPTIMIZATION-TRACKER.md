# Wiki Generator 模板优化跟踪文档

**创建日期**: 2026-01-05
**优化计划**: 基于 dingtalk-notable-connect 和 dingtalk-sdk-generator 参考项目
**目标**: 全面优化 wiki-generator 模板和 skills

---

## 📊 总体进度

- **总阶段数**: 8
- **已完成**: 4
- **进行中**: 0
- **待开始**: 4

---

## 🎯 优化目标总结

基于参考项目的优秀实践：

1. **模块化文档组织** - 按功能模块组织，子模块在各自的子目录中
2. **统一的文档头部格式** - cite块 + 目录 + 章节引用
3. **精确的源文件引用** - file:// 协议 + 行号范围
4. **丰富的 Mermaid 图表** - erDiagram, flowchart, classDiagram, sequenceDiagram
5. **规范的代码示例** - 语言标识 + 文件路径 + 运行结果
6. **专业的 API 文档格式** - HTTP方法 + 参数表 + 响应结构

---

## 📋 Phase 1: 统一模板变量格式

**状态**: ✅ 已完成 (2026-01-05)
**优先级**: 🔴 高
**实际用时**: ~15 分钟

### 目标
统一所有模板使用 `{variable_name}` 格式

### 执行情况
✅ 已修改 6 个文件：
- [x] `templates/overview.md.template`
- [x] `templates/module.md.template`
- [x] `templates/api.md.template`
- [x] `templates/architecture.md.template`
- [x] `templates/development.md.template`
- [x] `templates/index.md.template`

### 修改内容
将所有 `{{variable_name}}` 替换为 `{variable_name}`

### 验证结果
```bash
grep -r '{{' wiki_generator/.claude/templates/
# 结果: 0 个残留
```

### 完成标准
- ✅ 所有模板使用统一变量格式
- ✅ 无 `{{ }}` 格式残留
- ✅ 变量命名一致性

---

## 📋 Phase 2: 添加 Claude 指导注释

**状态**: ✅ 已完成 (2026-01-05)
**优先级**: 🔴 高
**实际用时**: ~20 分钟
**依赖**: Phase 1 完成

### 目标
在模板中添加注释，指导Claude从哪些文件提取信息

### 执行情况
✅ 已修改 22 个文件：
**中文模板（11个）**：
- [x] `templates/zh/overview.md.template`
- [x] `templates/zh/quickstart.md.template`
- [x] `templates/zh/corefeatures.md.template`
- [x] `templates/zh/datamodel.md.template`
- [x] `templates/zh/testing.md.template`
- [x] `templates/zh/development.md.template`
- [x] `templates/zh/security.md.template`
- [x] `templates/zh/troubleshooting.md.template`
- [x] `templates/zh/techstack.md.template`
- [x] `templates/zh/architecture.md.template`
- [x] `templates/zh/deployment.md.template`

**英文模板（11个）**：
- [x] `templates/en/overview.md.template`
- [x] `templates/en/quickstart.md.template`
- [x] `templates/en/corefeatures.md.template`
- [x] `templates/en/datamodel.md.template`
- [x] `templates/en/testing.md.template`
- [x] `templates/en/development.md.template`
- [x] `templates/en/security.md.template`
- [x] `templates/en/troubleshooting.md.template`
- [x] `templates/en/techstack.md.template`
- [x] `templates/en/architecture.md.template`
- [x] `templates/en/deployment.md.template`

### 添加的注释类型
定义了 40+ 个变量的数据源映射，包括：
- 项目基本信息（project_name, version, description）
- 概览相关（overview_summary, core_features）
- 技术栈（programming_languages, frameworks, tools）
- 安装配置（installation_steps, configuration_steps）
- 代码结构（directory_structure, architecture_overview）
- API 相关（api_overview, api_endpoints）
- 开发相关（development_setup, testing_guide）
- 部署相关（deployment_steps, environment_variables）
- 图表相关（architecture_diagram, data_relationships）
- 元数据（generation_time, doc_version, code_version）

### 示例
```markdown
<!-- Claude: 从 README.md 的前几段提取项目概述 -->
{overview_summary}

<!-- Claude: 从 requirements.txt、package.json、pyproject.toml dependencies 提取 -->
{dependencies}
```

### 完成标准
- ✅ 所有关键变量都有指导注释
- ✅ 注释清晰指明数据源
- ✅ 注释使用中文

---

## 📋 Phase 3: 优化代码示例格式

**状态**: ⏳ 待开始
**优先级**: 🟡 中
**预计时间**: 2-3 小时
**依赖**: Phase 1-2 完成

### 目标
统一代码示例的展示格式

### 新格式规范
```markdown
### 配置示例

```env title=".env"
# 数据库连接
DATABASE_URL=postgresql://user:pass@localhost:5432/db
```

### 运行命令

```bash title="终端"
# 安装依赖
uv sync

# 启动服务
uv run python main.py
```

**输出**:
{command_output}

**Section sources**
- [setup.sh](file://scripts/setup.sh#L10-L25)
```

### 需要修改的文件
- [ ] `templates/zh/quickstart.md.template`
- [ ] `templates/zh/development.md.template`
- [ ] `templates/zh/deployment.md.template`
- [ ] `templates/zh/testing.md.template`
- [ ] 对应的英文模板

### 完成标准
- ✅ 所有代码块有语言标识
- ✅ 关键代码块有 title 属性
- ✅ 命令示例包含输出展示
- ✅ 代码示例有引用来源

---

## 📋 Phase 4: 增强 API 文档支持

**状态**: ⏳ 待开始
**优先级**: 🟡 中
**预计时间**: 3-4 小时
**依赖**: Phase 1-3 完成

### 目标
添加 API 文档专用模板和生成逻辑

### 新增模板
- [ ] `templates/zh/api-reference.md.template` - API 参考文档模板
- [ ] `templates/zh/api-endpoint.md.template` - 单个 API 端点模板
- [ ] `templates/en/api-reference.md.template`
- [ ] `templates/en/api-endpoint.md.template`

### 模板内容要点
- HTTP 方法与 URL 路径
- 请求参数（路径、查询、请求体）
- 响应结构（成功、错误）
- 请求示例（Python、cURL）
- 参数表格（参数名、类型、必填、描述、约束）

### 需要修改的 skills
- [ ] `skills/doc-generator/content_extraction.md`
  - 添加 API 签名提取逻辑
  - 添加 FastAPI/Flask 路由提取
- [ ] `skills/doc-generator/content_generation.md`
  - 添加 API 文档生成逻辑
  - 支持参数表格生成

### 完成标准
- ✅ 新模板创建完成
- ✅ Skills 更新完成
- ✅ API 文档格式符合参考项目
- ✅ 支持多种 API 框架

---

## 📋 Phase 5: 优化 Mermaid 图表生成

**状态**: ⏳ 待开始
**优先级**: 🟢 低
**预计时间**: 2-3 小时
**依赖**: Phase 1-4 完成

### 目标
增强图表生成的智能性和多样性

### 图表类型映射表
| 文档类型 | 图表类型 | 生成条件 |
|---------|---------|---------|
| 数据模型 | `erDiagram` | 检测到 SQLAlchemy/Django ORM |
| 架构文档 | `flowchart TD` | 检测到多模块结构 |
| API 文档 | `sequenceDiagram` | 检测到 FastAPI/Flask |
| 类关系 | `classDiagram` | 检测到类继承 |
| 部署指南 | `graph TB` | 包含 Docker/k8s 配置 |

### 需要修改的 skills
- [ ] `skills/doc-generator/outline_generation.md`
  - 添加图表类型选择逻辑
  - 根据技术栈决定图表类型
- [ ] `skills/doc-generator/content_generation.md`
  - 添加图表生成代码
  - 支持 erDiagram, classDiagram, sequenceDiagram

### 完成标准
- ✅ 支持至少 5 种图表类型
- ✅ 智能选择图表类型
- ✅ 图表语法正确
- ✅ 图表有图例说明

---

## 📋 Phase 6: 添加文档元数据

**状态**: ⏳ 待开始
**优先级**: 🟢 低
**预计时间**: 1-2 小时
**依赖**: Phase 1-5 完成

### 目标
为生成的文档添加元数据信息

### 新增元数据模板
```markdown
---
**生成时间**: {generation_time}
**文档版本**: {doc_version}
**基于代码版本**: {code_version}
**生成工具**: wiki-generator v3.0
---

# {title}
```

### 需要添加的变量
- `{generation_time}` - ISO 8601 格式时间戳
- `{doc_version}` - 文档版本号
- `{code_version}` - Git commit hash 或 tag
- `{maintainer}` - 维护者信息（可选）

### 需要修改的文件
- [ ] 所有 `templates/zh/*.md.template`
- [ ] 所有 `templates/en/*.md.template`

### 完成标准
- ✅ 所有文档包含元数据
- ✅ 元数据格式统一
- ✅ 时间戳格式正确
- ✅ Git 版本信息准确

---

## 📋 Phase 7: 优化章节结构

**状态**: ⏳ 待开始
**优先级**: 🟢 低
**预计时间**: 2-3 小时
**依赖**: Phase 1-6 完成

### 目标
建立标准化的章节层次结构

### 标准结构
```markdown
# 一级标题（文档标题）

## 二级标题（主要章节）

### 三级标题（子章节）

#### 四级标题（细节说明）

**要点说明**:
- 要点1
- 要点2

**实现细节**:
{implementation_details}

**示例**:
```python
{code_example}
```

**注意事项**:
{notes}

**Section sources**
- [源文件](file://path#L1-L100)
```

### 需要修改的文件
- [ ] 所有模板文件

### 完成标准
- ✅ 章节层次清晰
- ✅ 使用标准格式元素
- ✅ 每个章节有引用来源
- ✅ 结构一致性

---

## 📋 Phase 8: 更新 Skills

**状态**: ⏳ 待开始
**优先级**: 🔴 高
**预计时间**: 4-6 小时
**依赖**: Phase 1-7 完成

### 目标
更新 doc-generator skills 以支持优化后的模板

### 需要更新的 skills

#### 1. content_extraction.md
- [ ] 添加 API 签名提取
  - FastAPI 路由提取
  - Flask 路由提取
  - 函数签名提取
- [ ] 添加类继承关系提取
  - 基类识别
  - 继承链构建
- [ ] 添加配置文件提取
  - .env 文件解析
  - YAML/JSON 配置提取

#### 2. outline_generation.md
- [ ] 添加图表类型选择逻辑
  - 根据技术栈选择图表
  - 根据内容类型选择图表
- [ ] 优化章节结构生成
  - 根据模块规模确定层级
  - 生成标准化章节

#### 3. content_generation.md
- [ ] 支持新变量格式
  - 统一使用 `{variable_name}`
- [ ] 生成元数据信息
  - 时间戳
  - Git 版本
  - 文档版本
- [ ] 生成规范化的代码示例
  - 添加语言标识
  - 添加 title 属性
  - 添加输出展示
- [ ] 智能选择图表类型
  - 实现图表类型映射
  - 生成图表代码

#### 4. index_generation.md
- [ ] 改进目录索引生成
  - 自动生成多级目录
  - 支持嵌套章节
- [ ] 添加锚点链接生成
  - 章节锚点
  - 图表锚点
- [ ] 生成交叉引用链接
  - 文档间引用
  - 相关章节引用

### 完成标准
- ✅ 所有 skills 更新完成
- ✅ 支持新模板格式
- ✅ 支持元数据生成
- ✅ 支持代码示例规范化
- ✅ 支持智能图表选择

---

## 📝 实施步骤总结

### 会话 1: Phase 1-2（高优先级）
- [ ] Phase 1: 统一变量格式
- [ ] Phase 2: 添加 Claude 指导注释

### 会话 2: Phase 3-4（中优先级）
- [ ] Phase 3: 优化代码示例格式
- [ ] Phase 4: 增强 API 文档支持

### 会话 3: Phase 5-6（低优先级）
- [ ] Phase 5: 优化 Mermaid 图表生成
- [ ] Phase 6: 添加文档元数据

### 会话 4: Phase 7-8（完成阶段）
- [ ] Phase 7: 优化章节结构
- [ ] Phase 8: 更新 Skills

### 会话 5: 测试和文档
- [ ] 生成测试文档
- [ ] 对比参考项目
- [ ] 调整和优化
- [ ] 更新 README 和使用文档

---

## 🎯 质量标准

### 模板质量
- [ ] 变量格式统一
- [ ] Claude 指导注释完整
- [ ] 代码示例格式规范
- [ ] 章节结构清晰
- [ ] 元数据信息完整

### 生成质量
- [ ] 与参考项目格式一致
- [ ] 代码示例可运行
- [ ] 图表语法正确
- [ ] 引用链接有效
- [ ] 目录索引准确

### 兼容性
- [ ] 向后兼容现有模板
- [ ] 支持中英文双语
- [ ] 支持多种技术栈
- [ ] 支持多种图表类型

---

## 📚 参考资源

### 参考项目路径
- `/home/yewenbin/work/tools/dingtalk-notable-connect/.qoder/repowiki`
- `/home/yewenbin/work/common/dingtalk-sdk-generator/.qoder/repowiki`

### 关键文件
- 模板目录: `wiki_generator/.claude/templates/`
- Skills 目录: `wiki_generator/.claude/skills/doc-generator/`
- 命令文档: `wiki_generator/.claude/commands/wiki-generate.md`

---

## 📌 注意事项

1. **备份优先**: 每个会话开始前备份当前模板
2. **逐步验证**: 每个 phase 完成后进行测试
3. **参考对照**: 时刻对比参考项目的格式
4. **中文优先**: 所有注释和说明使用中文
5. **向后兼容**: 保持现有模板的兼容性

---

**最后更新**: 2026-01-05
**下次会话重点**: Phase 1-2（统一变量格式 + Claude 指导注释）
