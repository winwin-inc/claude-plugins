# 研究文档：技术决策与最佳实践

**功能编号**: 001
**文档版本**: 1.0.0
**创建日期**: 2025-01-03
**状态**: 完成

---

## 研究概述

本文档记录了 Wiki 生成命令实现过程中的关键技术研究和技术决策。

### 研究目标

1. 确定命令文件组织方式
2. 设计配置管理架构
3. 选择文档生成策略
4. 设计质量验证机制
5. 制定项目类型识别规则

---

## 研究 1：命令文件组织方式

### 研究问题

应该如何组织 19 个命令文件以平衡简单性和可维护性？

### 研究发现

**Claude Code 对子目录的支持**：
- 子目录会出现在命令描述中，如 `(project:basic)`
- 子目录不影响命令名称
- 不同子目录可以有同名命令

**最佳实践**：
- 命令数量 < 10：扁平结构
- 命令数量 10-20：分类子目录
- 命令数量 > 20：混合模式

### 技术决策

**决策**: **使用分类子目录**

**目录结构**:
```
.claude/commands/
├── basic/
│   ├── wiki-init.md
│   ├── wiki-overview.md
│   ├── wiki-module.md
│   └── wiki-validate.md
├── advanced/
│   ├── wiki-architecture.md
│   ├── wiki-modules-all.md
│   ├── wiki-api.md
│   ├── wiki-development.md
│   ├── wiki-diagrams.md
│   └── wiki-index.md
├── maintenance/
│   ├── wiki-update.md
│   ├── wiki-changelog.md
│   └── wiki-cleanup.md
└── tools/
    ├── wiki-search.md
    ├── wiki-stats.md
    ├── wiki-export.md
    ├── wiki-translate.md
    ├── wiki-compare.md
    └── wiki-todo.md
```

**理由**:
1. **清晰的分类**：按功能类型分组
2. **易于导航**：用户可以快速找到相关命令
3. **可扩展**：未来添加命令时有明确的归属
4. **描述性**：子目录出现在命令描述中，提供额外上下文

**优点**:
- 结构清晰，易于维护
- 命令描述自动包含分类信息
- 支持未来扩展

**缺点**:
- 路径稍长（但可接受）

---

## 研究 2：配置管理架构

### 研究问题

如何设计配置系统以支持不同项目的个性化需求？

### 研究发现

**配置需求分析**:
- 大多数项目需要自定义输出目录
- 不同项目有不同的排除模式
- 用户可能需要自定义质量阈值
- 高级用户需要自定义模板

**常见模式**:
- ESLint：全局 + 项目级配置
- Prettier：支持配置文件和 package.json
- TypeScript：tsconfig.json 层级继承

### 技术决策

**决策**: **全局 + 项目级配置，项目级优先**

**配置架构**:
```
1. 全局配置（可选）
   ~/.claude/wiki-config.json

2. 项目配置（主要）
   .claude/wiki-config.json

3. 优先级：项目配置 > 全局配置 > 默认配置
```

**配置项设计**:
```json
{
  "output_dir": "docs",
  "exclude_patterns": ["node_modules", "dist", "build", ".git"],
  "template_dir": ".claude/templates",
  "quality_threshold": 80,
  "diagrams": {
    "enabled": true,
    "detail_level": "medium"
  },
  "modules": {
    "auto_detect": true,
    "patterns": ["src/*", "lib/*", "app/*"]
  },
  "language": "zh-CN",
  "custom_templates": {}
}
```

**理由**:
1. **灵活性**：支持全局默认值和项目自定义
2. **简单性**：项目配置为主，全局可选
3. **可维护性**：配置项清晰，文档完善
4. **扩展性**：预留自定义模板字段

**优点**:
- 满足不同项目需求
- 全局配置减少重复
- 项目配置可覆盖全局设置

**缺点**:
- 需要实现配置合并逻辑（复杂度可接受）

---

## 研究 3：文档生成策略

### 研究问题

如何平衡 AI 生成的灵活性和模板的一致性？

### 研究发现

**AI 生成的特点**:
- 优点：灵活、智能、适应性强
- 缺点：不稳定、可能偏离预期

**模板的特点**:
- 优点：稳定、一致、可控
- 缺点：僵化、限制创造力

**业界实践**:
- GitHub Copilot：AI 建议 + 人工确认
- Docsify：模板 + 内容填充
- Docusaurus：组件 + MDX

### 技术决策

**决策**: **结构模板 + AI 内容生成**

**生成策略**:
```
1. 结构模板（30%）
   - 定义文档结构
   - 定义章节标题
   - 定义占位符

2. AI 内容生成（70%）
   - 分析代码
   - 生成章节内容
   - 生成代码示例
   - 生成图表描述

3. 质量保证
   - 验证结构完整性
   - 验证内容准确性
   - 验证格式规范性
```

**示例模板**:
```markdown
# [模块名称] 模块

## 概述
[AI 生成：模块功能描述]

## API 接口
[AI 生成：API 列表和说明]

## 依赖关系
[AI 生成：依赖的模块]

## 使用示例
[AI 生成：可运行的代码示例]

## 注意事项
[AI 生成：使用注意点]
```

**理由**:
1. **平衡灵活性和一致性**：模板保证结构，AI 保证内容
2. **质量可控**：模板确保不遗漏关键部分
3. **易于维护**：修改模板即可调整所有文档
4. **用户友好**：结构清晰，易于阅读

**优点**:
- 文档结构一致
- 内容智能生成
- 易于定制和扩展

**缺点**:
- 需要维护模板（但成本低）

---

## 研究 4：质量验证机制

### 研究问题

如何自动化文档质量检查并确保可靠性？

### 研究发现

**质量维度**:
1. **结构完整性**：必需章节是否存在
2. **内容准确性**：代码示例是否正确
3. **链接有效性**：内部链接是否可访问
4. **格式规范性**：Markdown 格式是否正确
5. **语言质量**：中文是否自然流畅

**验证工具**:
- Markdown lint：检查格式
- Link checker：检查链接
- AI 评估：检查内容质量

### 技术决策

**决策**: **规则引擎 + AI 评估的混合模式**

**验证架构**:
```
1. 规则引擎（快速检查，60%）
   - 结构完整性：必需章节检查
   - 链接有效性：内部链接验证
   - 格式规范性：Markdown 语法检查
   - 代码示例：是否有代码块

2. AI 评估（深度检查，40%）
   - 内容准确性：代码示例是否可运行
   - 语言质量：中文是否自然
   - 技术准确性：描述是否正确
   - 完整性：是否遗漏重要信息

3. 分数计算
   - 规则引擎得分：60 分（满分）
   - AI 评估得分：40 分（满分）
   - 总分 = 规则得分 + AI 得分
```

**质量检查项**:

**规则引擎检查**（60 分）:
- [ ] 文档标题存在（5 分）
- [ ] 必需章节完整（15 分）
- [ ] 包含代码示例（10 分）
- [ ] 内部链接有效（10 分）
- [ ] Markdown 格式正确（10 分）
- [ ] 无空文件（5 分）
- [ ] 文档长度达标（5 分）

**AI 评估检查**（40 分）:
- [ ] 内容准确（10 分）
- [ ] 代码示例可运行（10 分）
- [ ] 中文表达自然（5 分）
- [ ] 技术术语准确（5 分）
- [ ] 结构逻辑清晰（5 分）
- [ ] 无明显遗漏（5 分）

**理由**:
1. **速度和质量的平衡**：规则引擎快速，AI 深度
2. **可扩展性**：可添加新的规则和评估项
3. **成本可控**：AI 评估只用于关键项
4. **透明性**：用户可以看到具体的问题

**优点**:
- 检查全面
- 速度可接受
- 结果可解释
- 成本可控

**缺点**:
- 需要维护规则（但规则相对稳定）

---

## 研究 5：项目类型识别

### 研究问题

如何准确识别不同类型的项目以应用适当的生成策略？

### 研究发现

**项目类型特征**:

**Node.js 项目**:
- package.json
- node_modules/ 目录
- npm 或 yarn 配置文件

**Python 项目**:
- requirements.txt
- setup.py 或 pyproject.toml
- __init__.py 文件
- .py 文件

**Java 项目**:
- pom.xml (Maven)
- build.gradle (Gradle)
- src/main/java/ 目录

**Go 项目**:
- go.mod 文件
- .go 文件

**Ruby 项目**:
- Gemfile
- .rb 文件

### 技术决策

**决策**: **基于文件特征的规则识别 + 手动配置**

**识别规则**:
```
优先级 1：明确配置（.claude/wiki-config.json 中的 project_type）
优先级 2：文件特征匹配
优先级 3：目录结构推测
优先级 4：默认为通用项目
```

**识别算法**:
```
function detectProjectType():
    config = loadConfig()
    if config.project_type:
        return config.project_type

    if exists("package.json"):
        return "nodejs"
    if exists("requirements.txt") or exists("setup.py"):
        return "python"
    if exists("pom.xml") or exists("build.gradle"):
        return "java"
    if exists("go.mod"):
        return "go"
    if exists("Gemfile"):
        return "ruby"

    # 目录结构推测
    if exists("src/main/java"):
        return "java"
    if exists("src/"):
        # 分析 src/ 下的文件类型
        return detectByExtension()

    return "generic"
```

**项目类型配置**:
```json
{
  "project_type": "nodejs",
  "type_specific": {
    "main_entry": "package.json#main",
    "dependencies": "package.json#dependencies",
    "scripts": "package.json#scripts"
  }
}
```

**理由**:
1. **准确性**：基于明确特征，错误率低
2. **灵活性**：支持手动覆盖
3. **可扩展**：易于添加新类型
4. **回退机制**：默认通用策略

**优点**:
- 识别准确
- 支持手动配置
- 易于扩展
- 有回退方案

**缺点**:
- 需要维护识别规则（但规则稳定）

---

## 技术决策总结

| 决策点 | 选择 | 关键理由 |
|--------|------|----------|
| 命令文件组织 | 分类子目录 | 清晰、可扩展、描述性 |
| 配置管理 | 全局 + 项目级 | 灵活、简单、可维护 |
| 文档生成 | 模板 + AI | 平衡灵活性和一致性 |
| 质量验证 | 规则 + AI 混合 | 速度、质量、成本平衡 |
| 项目识别 | 特征规则 + 配置 | 准确、灵活、可扩展 |

---

## 实现建议

### 1. 命令文件实现优先级

**阶段 1（MVP）**:
- basic/wiki-init.md
- basic/wiki-overview.md
- basic/wiki-module.md
- basic/wiki-validate.md

**阶段 2（扩展）**:
- advanced/ 目录下所有命令
- maintenance/wiki-update.md

**阶段 3（增强）**:
- maintenance/ 目录下其他命令
- tools/ 目录下所有命令

### 2. 配置系统实现

1. **首先实现默认配置**：硬编码在命令中
2. **然后实现项目配置**：读取 `.claude/wiki-config.json`
3. **最后实现全局配置**：读取 `~/.claude/wiki-config.json`

### 3. 质量验证实现

1. **首先实现规则引擎**：快速检查
2. **然后集成 AI 评估**：深度检查
3. **优化分数计算**：合理权重分配

### 4. 项目识别实现

1. **首先实现基本规则**：Node.js, Python
2. **然后扩展识别规则**：Java, Go, Ruby
3. **最后支持手动配置**：配置文件覆盖

---

## 风险与缓解

| 风险 | 缓解措施 |
|------|----------|
| Claude Code 子目录行为变化 | 监控官方文档，提供扁平结构备选方案 |
| AI 生成质量不稳定 | 质量验证 + 人工审查 + 迭代优化 |
| 项目类型识别失败 | 手动配置 + 默认通用策略 |
| 性能不达标 | 优化提示词 + 分批处理 + 缓存 |

---

## 参考资料

- [Claude Code 自定义命令文档](https://code.claude.com/docs/en/slash-commands#custom-slash-commands)
- [Markdown 规范](https://commonmark.org/)
- [Mermaid 图表语法](https://mermaid-js.github.io/mermaid/)
- [项目配置最佳实践](https://github.com/dwyl/generate-readme)

---

**研究状态**: ✅ 完成
**下一步**: Phase 1 设计
**最后更新**: 2025-01-03
