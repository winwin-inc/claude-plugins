# API Contracts: 自动文档大纲提取与主题映射

**功能版本**: 1.0.0
**创建日期**: 2026-01-04
**状态**: 草稿

---

## API 概览

本文档定义了自动文档大纲提取功能的内部 API 契约。这些函数主要由 `wiki-generate.md` 命令调用，不对外暴露。

---

## 1. detect_tech_stack()

检测项目使用的技术栈。

### 函数签名

```bash
detect_tech_stack(project_path: string): string[]
```

### 参数

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| `project_path` | string | ✅ | 项目根目录路径 |

### 返回值

技术栈名称列表（已去重）。

```json
["fastapi", "sqlalchemy", "pytest"]
```

### 检测规则

参考 [research.md](../research.md) Research Task 002。

### 实现要点

1. 使用多源验证（导入语句 + 配置文件 + 文件存在）
2. 应用阈值过滤（避免误报）
3. 排除测试文件和目录
4. 应用优先级去重规则

### 错误处理

| 错误代码 | 说明 | 处理方式 |
|---------|------|----------|
| `PROJECT_NOT_FOUND` | 项目目录不存在 | 返回空列表 |
| `ACCESS_DENIED` | 无权限访问目录 | 返回空列表 + 警告日志 |

---

## 2. identify_business_modules()

识别项目的业务模块。

### 函数签名

```bash
identify_business_modules(project_path: string, module_type: enum): BusinessModule[]
```

### 参数

| 参数名 | 类型 | 必需 | 说明 | 枚举值 |
|--------|------|------|------|--------|
| `project_path` | string | ✅ | 项目根目录路径 | - |
| `module_type` | enum | ✅ | 模块类型 | `service` / `page` / `api` / `model` |

### 返回值

业务模块对象列表。

```json
[
  {
    "id": "user_service",
    "name": "用户管理服务",
    "type": "service",
    "path": "src/services/user_service.py",
    "file_count": 5,
    "line_count": 1500,
    "dependency_count": 8,
    "scale": "medium",
    "depth": 2,
    "related_files": [...],
    "dependencies": [...]
  }
]
```

### 扫描路径

参考 [data-model.md](../data-model.md) BusinessModule.Type 枚举。

### 实现要点

1. 按优先级顺序扫描多个路径
2. 使用文件模式匹配（启发式扫描）
3. 计算模块规模（加权评分算法）
4. 确定文档层级深度

### 错误处理

| 错误代码 | 说明 | 处理方式 |
|---------|------|----------|
| `NO_MODULES_FOUND` | 未找到任何模块 | 返回空列表 |
| `INVALID_MODULE_TYPE` | 无效的模块类型 | 抛出异常 |

---

## 3. calculate_module_scale()

计算模块的规模等级。

### 函数签名

```bash
calculate_module_scale(module_path: string): {scale: enum, depth: integer}
```

### 参数

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| `module_path` | string | ✅ | 模块路径 |

### 返回值

包含规模等级和层级深度的对象。

```json
{
  "scale": "medium",
  "depth": 2
}
```

### 规模等级规则

| 文件数量 | 规模等级 | 层级深度 |
|---------|---------|---------|
| 1-4 | `small` | 1 |
| 5-20 | `medium` | 2 |
| 21-50 | `large` | 3 |
| >50 | `xlarge` | 4 |

### 实现要点

1. 统计模块目录下的 `.py` 或 `.tsx` 文件数量
2. 根据文件数量返回规模等级
3. 根据规模等级返回层级深度

---

## 4. extract_project_info()

从项目文件中提取信息。

### 函数签名

```bash
extract_project_info(project_path: string): object
```

### 参数

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| `project_path` | string | ✅ | 项目根目录路径 |

### 返回值

项目信息对象。

```json
{
  "project": {
    "name": "my-project",
    "description": "项目描述",
    "version": "1.0.0",
    "python_version": "3.11",
    "features": [...]
  },
  "tech_stack": {
    "backend_framework": "FastAPI",
    "orm": "SQLAlchemy",
    "database": "PostgreSQL"
  },
  "dependencies": {
    "production": [...],
    "development": [...]
  }
}
```

### 提取来源

1. `README.md`：项目名称、描述、核心功能
2. `pyproject.toml`：依赖、版本号、开发依赖
3. `package.json`：JavaScript 项目的依赖
4. `.python-version` 或 `runtime.txt`：Python 版本

### 实现要点

1. 使用正则表达式解析 README
2. 使用 `tomli` 库解析 pyproject.toml
3. 容错处理（字段缺失时返回默认值）

---

## 5. generate_document_outline()

生成文档大纲。

### 函数签名

```bash
generate_document_outline(config: DocumentConfig, modules: BusinessModule[]): object
```

### 参数

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| `config` | DocumentConfig | ✅ | 文档配置 |
| `modules` | BusinessModule[] | ✅ | 业务模块列表 |

### 返回值

文档大纲对象（树状结构）。

```json
{
  "required_documents": [...],
  "conditional_documents": [...],
  "business_module_documents": [...]
}
```

### 实现要点

1. 根据检测到的技术栈确定条件文档
2. 根据业务模块列表和规模等级确定文档结构
3. 应用层级深度规则
4. 生成文档索引

---

## 错误代码规范

所有 API 函数应遵循统一的错误代码规范。

### 格式

`<CATEGORY>_<SPECIFIC_ERROR>`

### 类别

| 类别 | 说明 |
|------|------|
| `PROJECT` | 项目相关错误（目录不存在、无权限等） |
| `MODULE` | 模块相关错误（未找到模块、无效类型等） |
| `CONFIG` | 配置相关错误（无效配置、缺失字段等） |
| `GENERATION` | 文档生成相关错误（模板缺失、AI 生成失败等） |

### 示例

- `PROJECT_NOT_FOUND`
- `MODULE_INVALID_TYPE`
- `CONFIG_MISSING_FIELD`
- `GENERATION_TEMPLATE_NOT_FOUND`

---

## 性能要求

| 函数 | 最大执行时间 | 说明 |
|------|------------|------|
| `detect_tech_stack()` | < 5 秒 | 中型项目（< 500 文件） |
| `identify_business_modules()` | < 30 秒 | 大型项目（< 1000 文件） |
| `calculate_module_scale()` | < 1 秒 | 单个模块 |
| `extract_project_info()` | < 2 秒 | 读取并解析文件 |
| `generate_document_outline()` | < 5 秒 | 大型项目（< 100 模块） |

---

**API 契约版本**: 1.0.0
**最后更新**: 2026-01-04
**状态**: ✅ 完成 - 已定义所有内部 API
