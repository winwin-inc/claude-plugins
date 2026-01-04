# Claude Code 自定义命令使用指南

## 概述

本项目提供了两个核心 Claude Code 自定义命令：

1. **Wiki Generator** (`/wiki-generate`) - 自动分析和生成项目 Wiki 文档
2. **Command Install** (`/command.install`) - 安装和管理自定义命令

---

## Wiki Generator 命令

### 概述

Wiki Generator 命令用于自动分析和生成项目 Wiki 文档。

**关键特性**：
- ✅ 单一命令，多参数控制
- ✅ AI 驱动的代码分析
- ✅ 智能增量更新（保护手动编辑）
- ✅ 质量验证和评分
- ✅ 多语言翻译支持

## 快速开始

### 1. 新项目完整文档生成

```bash
/wiki-generate --full
```

**功能**：
- 初始化文档目录结构
- 生成项目概览、架构文档
- 生成所有模块文档
- 生成 API 文档和开发指南
- 自动运行质量验证

### 2. 增量更新文档

```bash
/wiki-generate --update
```

**核心特性**：
- 基于 Git 提交分析变更
- **智能检测并保护手动编辑内容**
- 100% 保留用户的改进
- 生成清晰的变更报告

### 3. 单模块文档生成

```bash
/wiki-generate --module=src/auth
```

**功能**：
- 为指定模块生成详细文档
- API 接口提取和文档化
- 依赖关系图
- 可运行的代码示例

### 4. 文档质量验证

```bash
/wiki-generate --validate
```

**功能**：
- 全面检查文档质量
- 0-100 分的质量评分
- 列出优点和问题
- 提供改进建议

### 5. 多语言翻译

```bash
/wiki-generate --translate=en
```

**功能**：
- 翻译所有文档
- 保持代码示例不翻译
- 保持技术术语不翻译
- 创建目标语言目录结构

## 参数组合使用

支持参数组合以实现复杂工作流：

```bash
# 生成并验证
/wiki-generate --full --validate

# 更新并翻译
/wiki-generate --update --translate=en

# 生成模块并验证
/wiki-generate --module=src/auth --validate
```

## 配置文件

配置文件位于 `.claude/wiki-config.json`，首次运行时自动生成：

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
  "language": "zh-CN"
}
```

## 生成的文档结构

```
docs/
├── README.md                    # 导航索引
├── 00-Overview.md               # 项目概览
├── 01-Architecture.md           # 架构文档
├── 02-Development.md            # 开发指南
├── modules/                     # 模块文档
│   ├── auth.md
│   ├── payment.md
│   └── ...
├── api/                         # API 文档
│   └── ENDPOINTS.md
├── diagrams/                    # 生成的图表
└── CHANGELOG.md                 # 变更历史
```

## 性能目标

| 参数 | 性能目标 |
|------|----------|
| `--full` | < 5 分钟（100 个模块） |
| `--module=<path>` | < 10 秒（单模块） |
| `--update` | < 2 分钟（增量） |
| `--validate` | < 30 秒（全部文档） |
| `--translate=<lang>` | < 3 分钟（全部文档） |

## 质量标准

- 文档质量分数 ≥ 80
- 代码示例可运行率 ≥ 95%
- Mermaid 图表语法正确率 100%
- 增量更新手动编辑保留率 100%

## 项目宪章

本项目遵循 8 条核心原则：

1. **中文优先** - 所有用户交互使用简体中文
2. **代码优先** - 专注于命令实现，不自动生成文档
3. **工具定位** - 为其他项目生成文档的元项目
4. **命令一致性** - 使用 `/wiki.<category>` 格式
5. **文档质量** - 质量分数必须 ≥ 80
6. **增量更新** - 优先使用增量更新，保护手动编辑
7. **AI 辅助** - AI 生成草稿，人工审查
8. **性能预期** - 明确的性能标准

## 故障排除

### 错误：模块路径不存在

```bash
/wiki-generate --module=src/auth
# ❌ 错误：模块路径 src/auth 不存在
```

**解决**：检查路径是否正确，或使用 `--full` 初始化

### 错误：不是 Git 仓库

```bash
/wiki-generate --update
# ❌ 错误：当前目录不是 Git 仓库
```

**解决**：`--update` 需要 Git 仓库，使用 `--full` 生成完整文档

### 错误：配置文件损坏

```bash
# ❌ 错误：.claude/wiki-config.json 格式错误
```

**解决**：删除配置文件，重新运行命令以生成默认配置

## 贡献指南

本项目遵循 SpecKit 方法论：
1. Constitution（宪章）
2. Specification（规范）
3. Planning（计划）
4. Tasks（任务）
5. Implementation（实现）

## 版本历史

- **v1.0.0** (2025-01-03): 初始版本
  - 单一命令架构
  - 5 个核心参数
  - 智能增量更新
  - 质量验证
  - 多语言翻译

## 许可证

MIT

---

## Command Install 命令

### 概述

Command Install 命令用于安装和管理 Claude Code 自定义命令。

**关键特性**：
- ✅ 从 Git 仓库安装命令
- ✅ 从本地文件安装命令
- ✅ 命令更新和卸载
- ✅ 智能冲突处理
- ✅ 备份和回滚机制

### 基本用法

#### 安装命令

```bash
# 从 Git 仓库安装
/command.install install https://github.com/user/command-repo

# 从本地文件安装
/command.install install ./my-command.md

# 使用预设名称安装
/command.install install wiki-generator
```

#### 列出已安装命令

```bash
/command.install list
```

#### 更新命令

```bash
/command.install update wiki-generator
```

#### 卸载命令

```bash
/command.install uninstall wiki-generator
```

#### 查看命令信息

```bash
/command.install info wiki-generator
```

### 配置文件

配置文件位于 `.claude/command-install.json`：

```json
{
  "version": "1.0.0",
  "installed_commands": {},
  "install_sources": {
    "presets": {}
  },
  "settings": {
    "auto_update": false,
    "backup_before_update": true,
    "keep_backup_count": 3,
    "conflict_strategy": "skip"
  },
  "backups": {}
}
```

### 高级选项

```bash
# 备份后覆盖冲突文件
/command.install install <source> --backup

# 强制覆盖
/command.install install <source> --force

# 跳过冲突文件
/command.install install <source> --skip

# 交互式询问
/command.install install <source> --ask

# 预览模式
/command.install install <source> --dry-run
```

---

**最后更新**: 2025-01-03
**维护者**: Repo Wiki Generator 项目团队
