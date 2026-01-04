# 配置文件契约

**版本**: 1.0.0
**最后更新**: 2025-01-03

---

## 配置文件结构

### 文件位置

- **项目配置**: `.claude/wiki-config.json`
- **全局配置**: `~/.claude/wiki-config.json`（可选）

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "output_dir": {
      "type": "string",
      "default": "docs",
      "description": "文档输出目录"
    },
    "exclude_patterns": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "default": ["node_modules", "dist", "build", ".git"],
      "description": "排除的目录模式"
    },
    "template_dir": {
      "type": "string",
      "default": ".claude/templates",
      "description": "自定义模板目录"
    },
    "quality_threshold": {
      "type": "integer",
      "minimum": 0,
      "maximum": 100,
      "default": 80,
      "description": "质量分数阈值"
    },
    "diagrams": {
      "type": "object",
      "properties": {
        "enabled": {
          "type": "boolean",
          "default": true
        },
        "detail_level": {
          "type": "string",
          "enum": ["low", "medium", "high"],
          "default": "medium"
        }
      }
    },
    "modules": {
      "type": "object",
      "properties": {
        "auto_detect": {
          "type": "boolean",
          "default": true
        },
        "patterns": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "default": ["src/*", "lib/*", "app/*"]
        }
      }
    },
    "language": {
      "type": "string",
      "default": "zh-CN",
      "description": "默认语言"
    },
    "project_type": {
      "type": "string",
      "description": "项目类型（手动指定）"
    }
  }
}
```

---

## 配置项说明

### output_dir

- **类型**: string
- **默认值**: "docs"
- **描述**: 生成的文档保存目录
- **示例**: "docs", "documentation", "wiki"

### exclude_patterns

- **类型**: array[string]
- **默认值**: ["node_modules", "dist", "build", ".git"]
- **描述**: 分析代码时排除的目录模式
- **示例**: ["node_modules", "coverage", "*.test.js"]

### template_dir

- **类型**: string
- **默认值**: ".claude/templates"
- **描述**: 自定义文档模板目录
- **示例**: ".claude/custom-templates"

### quality_threshold

- **类型**: integer
- **范围**: 0-100
- **默认值**: 80
- **描述**: 文档质量最低要求分数
- **示例**: 80, 85, 90

### diagrams.enabled

- **类型**: boolean
- **默认值**: true
- **描述**: 是否生成 Mermaid 图表

### diagrams.detail_level

- **类型**: enum
- **值**: "low", "medium", "high"
- **默认值**: "medium"
- **描述**: 图表详细程度

### modules.auto_detect

- **类型**: boolean
- **默认值**: true
- **描述**: 是否自动检测项目模块

### modules.patterns

- **类型**: array[string]
- **默认值**: ["src/*", "lib/*", "app/*"]
- **描述**: 模块目录匹配模式
- **示例**: ["src/*", "lib/*", "packages/*"]

### language

- **类型**: string
- **默认值**: "zh-CN"
- **描述**: 文档默认语言
- **示例**: "zh-CN", "en", "ja"

### project_type

- **类型**: string
- **描述**: 手动指定项目类型
- **值**: "nodejs", "python", "java", "go", "ruby", "generic"
- **示例**: "nodejs"

---

## 配置优先级

1. **项目配置** (`.claude/wiki-config.json`)
2. **全局配置** (`~/.claude/wiki-config.json`)
3. **默认值** (硬编码)

---

## 配置验证

### 必需检查

- [ ] JSON 格式正确
- [ ] output_dir 为有效路径
- [ ] exclude_patterns 为数组
- [ ] quality_threshold 在 0-100 范围内

### 可选检查

- [ ] template_dir 存在（如果指定）
- [ ] diagrams.detail_level 为有效值
- [ ] language 为有效语言代码
- [ ] project_type 为支持的类型

---

## 示例配置

### 最小配置

```json
{
}
```

使用所有默认值。

### 典型配置

```json
{
  "output_dir": "docs",
  "exclude_patterns": ["node_modules", "dist", ".git"],
  "quality_threshold": 80,
  "diagrams": {
    "enabled": true,
    "detail_level": "medium"
  }
}
```

### 高级配置

```json
{
  "output_dir": "documentation",
  "exclude_patterns": ["node_modules", "dist", "coverage", "*.test.js"],
  "template_dir": ".claude/custom-templates",
  "quality_threshold": 85,
  "diagrams": {
    "enabled": true,
    "detail_level": "high"
  },
  "modules": {
    "auto_detect": true,
    "patterns": ["src/*", "lib/*", "packages/*"]
  },
  "language": "zh-CN",
  "project_type": "nodejs"
}
```

---

**契约状态**: ✅ 完成
**最后更新**: 2025-01-03
