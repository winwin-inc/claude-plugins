# Wiki 文档模板

本目录包含用于自动生成项目 Wiki 文档的 Markdown 模板文件。

## 目录结构

```
wiki-generate/
├── README.md                    # 本文件
├── TEMPLATE_FORMAT.md           # 模板格式规范文档
├── wiki-config.json.template    # Wiki 配置文件模板
├── zh/                          # 中文模板（13个文件）
│   ├── quickstart.md.template
│   ├── overview.md.template
│   ├── techstack.md.template
│   ├── architecture.md.template
│   ├── corefeatures.md.template
│   ├── development.md.template
│   ├── deployment.md.template
│   ├── testing.md.template
│   ├── troubleshooting.md.template
│   ├── security.md.template
│   ├── api-reference.md.template
│   ├── api-endpoint.md.template
│   └── datamodel.md.template
└── en/                          # 英文模板（13个文件）
    └── ...（对应英文版本）
```

## 模板文件说明

### 必需文档模板（9个）

这些文档在每次生成时都会创建：

| 模板文件 | 生成文档名 | 说明 |
|---------|-----------|------|
| quickstart.md.template | 00-快速开始.md | 5分钟入门指南 |
| overview.md.template | 01-项目概述.md | 项目介绍和核心概念 |
| techstack.md.template | 02-技术栈与依赖.md | 技术选型说明 |
| architecture.md.template | 03-系统架构设计.md | 架构图和设计模式 |
| corefeatures.md.template | 04-核心功能.md | 核心业务流程说明 |
| development.md.template | 05-开发指南.md | 开发环境设置和指南 |
| deployment.md.template | 06-部署指南.md | 部署流程和配置 |
| testing.md.template | 07-测试策略.md | 测试方法和工具说明 |
| troubleshooting.md.template | 08-故障排除.md | 常见问题和解决方案 |
| security.md.template | 09-安全考虑.md | 安全最佳实践 |

### 条件文档模板（4个）

这些文档根据技术栈检测动态生成：

| 模板文件 | 生成文档名 | 触发条件 |
|---------|-----------|---------|
| datamodel.md.template | 数据模型/数据模型.md | 检测到 SQLAlchemy/Django ORM |
| api-reference.md.template | API 文档/API 参考.md | 检测到 FastAPI/Flask/Django REST |
| api-endpoint.md.template | API 文档/API 接口.md | 检测到 FastAPI/Flask/Django REST |
| taskqueue.md.template | 任务队列/任务队列.md | 检测到 Celery/RQ |

## 模板变量格式

模板使用 `{variable_name}` 格式的占位符，在生成时会被替换为实际内容。

### 常用变量

| 变量名 | 说明 | 示例值 |
|-------|------|--------|
| `{project_name}` | 项目名称 | "MyProject" |
| `{version}` | 项目版本 | "1.0.0" |
| `{generation_time}` | 生成时间 | "2025-01-07 15:00:00" |
| `{description}` | 项目描述 | "项目简介文本" |

### 文档特定变量

不同模板文件有特定的变量，例如：

**architecture.md.template**:
- `{architecture_diagram}` - Mermaid 架构图
- `{design_patterns}` - 设计模式说明
- `{component_description}` - 组件描述

**api-reference.md.template**:
- `{api_overview}` - API 概述
- `{endpoints_table}` - 端点列表表格
- `{authentication}` - 认证说明

**datamodel.md.template**:
- `{models_list}` - 模型列表
- `{relationship_diagram}` - 关系图（Mermaid ER图）
- `{field_descriptions}` - 字段描述

## 添加新模板

如需添加新的文档模板：

1. **创建模板文件**：
   ```bash
   # 在 zh/ 目录创建中文模板
   touch zh/new-document.md.template

   # 在 en/ 目录创建英文模板
   touch en/new-document.md.template
   ```

2. **编写模板内容**：
   ```markdown
   ---
   **生成时间**: {generation_time}
   **文档版本**: {doc_version}
   ---

   # {document_title}

   {content}
   ```

3. **更新文档映射表**：
   在 [plugins/commands/wiki-generate.md](../../commands/wiki-generate.md) 的文档列表中添加新模板的映射。

4. **测试模板**：
   运行 `/wiki-generate --full` 生成文档并检查结果。

## 模板格式规范

详细的模板格式规范请参考 [TEMPLATE_FORMAT.md](TEMPLATE_FORMAT.md)。

主要要求：

- ✅ 使用 `{variable_name}` 格式的占位符
- ✅ 包含必需的元数据头部（生成时间、版本等）
- ✅ 支持 Mermaid 图表（使用 ` ```mermaid ` 代码块）
- ✅ 遵循 Markdown 规范
- ✅ 中英文双语版本保持结构一致

## 技术栈检测规则

模板生成根据以下技术栈检测规则：

| 技术栈 | 检测条件 | 生成模板 |
|-------|---------|---------|
| SQLAlchemy | `from sqlalchemy` 或 `import sqlalchemy` | datamodel.md.template |
| Django ORM | `from django.db` | datamodel.md.template |
| FastAPI | `from fastapi` 或 `import fastapi` | api-*.md.template |
| Flask | `from flask` | api-*.md.template |
| Django REST | `from rest_framework` | api-*.md.template |
| Celery | `from celery` 或 `import celery` | taskqueue.md.template |
| pytest | `import pytest` | testing.md.template |
| unittest | `import unittest` | testing.md.template |

## 相关文件

- [Wiki 生成命令](../../commands/wiki-generate.md) - 主要的文档生成逻辑
- [Doc-generator Skills](../../skills/doc-generator/) - 文档生成技能集
- [Wiki 配置示例](wiki-config.json.template) - 配置文件模板

---

**最后更新**: 2025-01-07
**维护者**: repo-wiki 项目团队
