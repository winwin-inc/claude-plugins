# API 契约：Claude Code 命令安装器

**功能编号**: 001
**功能名称**: command-install
**契约版本**: 1.0.0
**创建日期**: 2025-01-03
**状态**: ✅ 完成

---

## 目录

1. [命令接口契约](#命令接口契约)
2. [配置文件契约](#配置文件契约)
3. [数据交换格式](#数据交换格式)
4. [错误码定义](#错误码定义)
5. [事件定义](#事件定义)

---

## 命令接口契约

### 命令：/command.install

**描述**：统一的命令安装和管理工具

**格式**：
```markdown
---
description: Claude Code 命令安装器
argument-hint: <action> [options]
allowed-tools: Read, Write, Glob, Grep, Bash
---
```

---

### 动作 1：install - 安装命令

**语法**：
```bash
/command.install install <source> [command-name]
```

**参数**：
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `source` | string | ✅ | 命令来源（Git URL、本地路径、预设名称） |
| `command-name` | string | ❌ | 指定命令名称（覆盖自动检测） |

**选项**：
| 选项 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `--force` | flag | false | 强制覆盖已存在的文件 |
| `--skip` | flag | true（批量） | 跳过冲突文件 |
| `--backup` | flag | false | 备份后覆盖 |
| `--ask` | flag | false | 交互式询问如何处理冲突 |
| `--dry-run` | flag | false | 预览模式，不实际安装 |
| `--merge` | flag | false | 智能合并 JSON 配置 |

**输入**：
```bash
/command.install install https://github.com/user/repo --backup
```

**输出**：
```
✅ 命令安装成功：wiki-generate

📦 安装摘要：
  命令名称：wiki-generate
  版本：1.0.0
  来源：https://github.com/user/repo
  安装时间：2025-01-03 08:00:00

📄 已安装文件：
  ✓ .claude/commands/wiki-generate.md (10 KB)
  ✓ .claude/templates/wiki-config.json.template (512 B)
  ✓ .claude/templates/overview.md.template (2 KB)

💡 使用方法：
  /wiki-generate --full
  /wiki-generate --update
  /wiki-generate --module=src/auth

📚 更多帮助：
  /wiki-generate --help
```

**错误输出**：
```
❌ 安装失败：wiki-generate

原因：命令已存在
💡 建议：
  - 使用 --force 强制覆盖
  - 使用 --update 更新到最新版本
  - 使用 --uninstall 先卸载现有版本

🔗 帮助：/command.install help
```

**验收标准**：
- [ ] 命令文件正确安装到 `.claude/commands/`
- [ ] 模板文件正确安装到 `.claude/templates/`
- [ ] 配置文件更新（记录安装信息）
- [ ] 安装时间 < 30 秒
- [ ] 显示清晰的安装摘要

---

### 动作 2：list - 列出已安装命令

**语法**：
```bash
/command.install list [--format=<format>]
```

**参数**：无

**选项**：
| 选项 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `--format` | string | table | 输出格式（table、json、简体） |

**输入**：
```bash
/command.install list
```

**输出**：
```
已安装的命令：

┌─────────────────┬─────────────────────┬────────┬──────────────────────┐
│ 命令名称        │ 描述                │ 版本   │ 安装日期             │
├─────────────────┼─────────────────────┼────────┼──────────────────────┤
│ wiki-generate   │ Wiki 文档生成器     │ 1.0.0  │ 2025-01-03           │
│ code-review     │ 代码审查助手        │ 2.1.0  │ 2025-01-02           │
│ test-runner     │ 测试运行器          │ 1.5.2  │ 2025-01-01           │
└─────────────────┴─────────────────────┴────────┴──────────────────────┘

总计：3 个命令
占用空间：45 KB
最新可用更新：1 个（code-review 2.1.0 → 2.2.0）
```

**JSON 格式输出**：
```bash
/command.install list --format=json
```

```json
{
  "commands": [
    {
      "name": "wiki-generate",
      "version": "1.0.0",
      "description": "Wiki 文档生成器",
      "installed_at": "2025-01-03T08:00:00Z",
      "source_type": "git",
      "source_url": "https://github.com/user/repo",
      "files_count": 3,
      "size": 10240
    }
  ],
  "total_count": 3,
  "total_size": 46080,
  "updates_available": 1
}
```

**验收标准**：
- [ ] 显示所有已安装命令
- [ ] 信息准确完整
- [ ] 支持多种输出格式
- [ ] 响应时间 < 5 秒

---

### 动作 3：update - 更新命令

**语法**：
```bash
/command.install update <command-name>
```

**参数**：
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `command-name` | string | ✅ | 要更新的命令名称 |

**选项**：
| 选项 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `--backup` | flag | true | 更新前自动备份 |
| `--merge` | flag | false | 智能合并配置文件 |
| `--force` | flag | false | 强制更新（忽略版本检查） |
| `--dry-run` | flag | false | 预览更新内容 |

**输入**：
```bash
/command.install update wiki-generate --backup
```

**输出**：
```
✅ 命令更新成功：wiki-generate

📦 更新摘要：
  当前版本：1.0.0
  新版本：1.2.0
  来源：https://github.com/user/repo

🔄 变更内容：
  ✓ 新增：--translate 参数支持多语言翻译
  ✓ 改进：增量更新性能提升 50%
  ✓ 修复：配置文件合并问题

📄 已更新文件：
  ✓ .claude/commands/wiki-generate.md (备份：.claude/backups/wiki-generate.md.20250103_103000.bak)
  ✓ .claude/templates/overview.md.template

💾 备份位置：
  .claude/backups/wiki-generate.md.20250103_103000.bak

💡 回滚方法：
  /command.install rollback wiki-generate --to 20250103_103000
```

**错误输出**：
```
❌ 更新失败：wiki-generate

原因：无法连接到更新源
💡 建议：
  - 检查网络连接
  - 确认仓库 URL 是否正确
  - 稍后重试

🔗 帮助：/command.install help update
```

**验收标准**：
- [ ] 命令成功更新到最新版本
- [ ] 备份自动创建（如启用）
- [ ] 用户配置得到保留
- [ ] 显示清晰的变更摘要
- [ ] 更新时间 < 30 秒

---

### 动作 4：uninstall - 卸载命令

**语法**：
```bash
/command.install uninstall <command-name>
```

**参数**：
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `command-name` | string | ✅ | 要卸载的命令名称 |

**选项**：
| 选项 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `--backup` | flag | true | 卸载前自动备份 |
| `--force` | flag | false | 强制卸载（跳过确认） |
| `--purge` | flag | false | 同时删除备份文件 |

**输入**：
```bash
/command.install uninstall wiki-generate --backup
```

**输出**：
```
⚠️  即将卸载命令：wiki-generate

📋 将要删除的文件：
  - .claude/commands/wiki-generate.md
  - .claude/templates/wiki-config.json.template
  - .claude/templates/overview.md.template
  - .claude/templates/module.md.template

💾 备份位置：
  .claude/backups/wiki-generate.md.20250103_110000.bak

确认卸载？[y/N] y

✅ 命令卸载成功：wiki-generate

📊 卸载摘要：
  删除文件数：4
  释放空间：15 KB
  备份已创建：是

💾 备份位置：
  .claude/backups/wiki-generate.md.20250103_110000.bak

💡 恢复方法：
  /command.install restore wiki-generate --from 20250103_110000
```

**验收标准**：
- [ ] 所有相关文件被删除
- [ ] 无孤立文件残留
- [ ] 配置文件更新（移除记录）
- [ ] 备份自动创建（如启用）
- [ ] 卸载时间 < 10 秒

---

### 动作 5：info - 显示命令详细信息

**语法**：
```bash
/command.install info <command-name>
```

**参数**：
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `command-name` | string | ✅ | 要查询的命令名称 |

**选项**：无

**输入**：
```bash
/command.install info wiki-generate
```

**输出**：
```
命令：wiki-generate
版本：1.0.0
作者：Repo Wiki Generator Team
描述：Wiki 文档生成器

📦 安装信息：
  安装来源：https://github.com/user/wiki-generator-repo
  来源类型：Git 仓库
  安装日期：2025-01-03 08:00:00
  最后更新：2025-01-03 10:30:00

📄 资源文件（3 个，共 15 KB）：
  - .claude/commands/wiki-generate.md (10 KB)
  - .claude/templates/wiki-config.json.template (512 B)
  - .claude/templates/overview.md.template (2 KB)

🔗 依赖关系：
  无依赖

📚 更多信息：
  主页：https://github.com/user/wiki-generator-repo
  许可证：MIT
  标签：documentation, wiki, generator

💾 备份文件：
  - 2025-01-03 10:30:00 (.claude/backups/wiki-generate.md.20250103_103000.bak)

🔄 更新状态：
  当前版本：1.0.0
  最新版本：1.2.0
  有可用更新：是
```

**验收标准**：
- [ ] 信息准确完整
- [ ] 资源清单详细
- [ ] 显示更新状态
- [ ] 响应时间 < 5 秒

---

## 配置文件契约

### 文件：.claude/command-install.json

**描述**：存储命令安装管理器的配置和命令来源信息

**版本**：1.0.0

**结构**：
```json
{
  "$schema": "./command-install-schema.json",
  "version": "1.0.0",

  "installed_commands": {
    "命令名": {
      "name": "命令名",
      "version": "版本号",
      "source_type": "来源类型",
      "source_url": "来源 URL",
      "installed_at": "安装时间",
      "updated_at": "更新时间",
      "files": [
        {
          "path": "文件路径",
          "type": "文件类型",
          "size": 文件大小,
          "checksum": "SHA-256 校验和"
        }
      ],
      "dependencies": ["依赖命令列表"],
      "metadata": {
        "author": "作者",
        "description": "描述",
        "tags": ["标签列表"],
        "license": "许可证",
        "homepage": "主页 URL"
      },
      "auto_update_enabled": false
    }
  },

  "install_sources": {
    "presets": {
      "预设名": {
        "url": "仓库 URL",
        "description": "描述",
        "version": "版本"
      }
    }
  },

  "settings": {
    "auto_update": false,
    "backup_before_update": true,
    "keep_backup_count": 3,
    "conflict_strategy": "skip",
    "default_source_type": "git",
    "timeout_seconds": 60,
    "max_retries": 3
  },

  "backups": {
    "命令名": [
      {
        "backup_path": "备份路径",
        "timestamp": "备份时间",
        "reason": "备份原因",
        "size": 文件大小,
        "checksum": "校验和"
      }
    ]
  }
}
```

### 字段说明

#### installed_commands

已安装命令的字典，键为命令名称。

**必需字段**：
- `name`：命令名称
- `version`：版本号（SemVer 格式）
- `source_type`：来源类型（git、local、preset）
- `installed_at`：安装时间（ISO 8601）
- `files`：文件列表

**可选字段**：
- `source_url`：来源 URL（git 和 preset）
- `source_path`：来源路径（local）
- `updated_at`：最后更新时间
- `dependencies`：依赖命令列表
- `metadata`：元数据对象
- `auto_update_enabled`：是否启用自动更新

#### files

命令包含的文件列表。

**字段**：
- `path`：文件相对路径
- `type`：文件类型（command、template、config、other）
- `size`：文件大小（字节）
- `checksum`：SHA-256 校验和

#### install_sources

安装来源配置。

**presets**：预设命令字典
- `url`：仓库 URL
- `description`：描述
- `version`：版本

#### settings

全局设置。

**字段**：
- `auto_update`：是否自动更新所有命令
- `backup_before_update`：更新前是否自动备份
- `keep_backup_count`：保留备份数量
- `conflict_strategy`：默认冲突策略（skip、overwrite、backup、ask）
- `default_source_type`：默认来源类型
- `timeout_seconds`：操作超时时间
- `max_retries`：最大重试次数

#### backups

备份文件记录。

**结构**：
```json
{
  "命令名": [
    {
      "backup_path": "备份文件路径",
      "timestamp": "备份时间（ISO 8601）",
      "reason": "备份原因（update、uninstall、manual）",
      "size": "文件大小（字节）",
      "checksum": "SHA-256 校验和"
    }
  ]
}
```

---

## 数据交换格式

### 请求格式

所有命令使用统一的请求格式：

```bash
/command.install <action> [positional-args] [options]
```

**位置参数**（positional-args）：
- 必需参数，按顺序指定
- 示例：`<source> [command-name]`

**选项**（options）：
- 可选参数，使用 `--option-name` 格式
- 布尔标志：`--force`、`--dry-run`
- 带值选项：`--format=json`、`--to=20250103_103000`

### 响应格式

#### 成功响应

```
✅ 操作描述

详细信息和摘要...
```

**前缀约定**：
- `✅`：成功
- `⚠️`：警告
- `💡`：提示信息
- `📦`：安装信息
- `📄`：文件信息
- `🔄`：更新信息
- `💾`：备份信息

#### 错误响应

```
❌ 错误描述

原因：<具体原因>
💡 建议：
  - 建议 1
  - 建议 2

🔗 帮助：/command.install help <action>
```

**前缀约定**：
- `❌`：错误
- `💡`：建议
- `🔗`：帮助链接

### JSON 格式

某些命令支持 JSON 输出（`--format=json`）：

```json
{
  "success": true,
  "message": "操作成功",
  "data": {
    // 具体数据
  }
}
```

错误响应：

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "reason": "详细原因",
    "suggestions": ["建议 1", "建议 2"]
  }
}
```

---

## 错误码定义

### 格式

错误码格式：`[CATEGORY]_[SPECIFIC]`

**分类**：
- `RESOLVE`：来源解析错误
- `DOWNLOAD`：下载/克隆错误
- `VALIDATE`：验证错误
- `INSTALL`：安装错误
- `UPDATE`：更新错误
- `UNINSTALL`：卸载错误
- `CONFIG`：配置错误
- `SYSTEM`：系统错误

### 错误码列表

| 错误码 | 描述 | HTTP 状态码 |
|--------|------|-------------|
| **RESOLVE_UNKNOWN_TYPE** | 无法识别来源类型 | 400 |
| **RESOLVE_INVALID_URL** | Git URL 格式错误 | 400 |
| **RESOLVE_PRESET_NOT_FOUND** | 预设名称未找到 | 404 |
| **RESOLVE_LOCAL_NOT_FOUND** | 本地路径不存在 | 404 |
| **DOWNLOAD_NETWORK_ERROR** | 网络连接失败 | 503 |
| **DOWNLOAD_TIMEOUT** | 下载超时 | 504 |
| **DOWNLOAD_PERMISSION_DENIED** | 仓库访问权限不足 | 403 |
| **VALIDATE_MISSING_FRONTMATTER** | 命令文件缺少 frontmatter | 422 |
| **VALIDATE_INVALID_JSON** | JSON 格式错误 | 422 |
| **VALIDATE_CHECKSUM_MISMATCH** | 文件校验和不匹配 | 422 |
| **INSTALL_COMMAND_EXISTS** | 命令已存在 | 409 |
| **INSTALL_FILE_CONFLICT** | 文件冲突 | 409 |
| **INSTALL_PERMISSION_DENIED** | 写入权限不足 | 403 |
| **UPDATE_NOT_INSTALLED** | 命令未安装 | 404 |
| **UPDATE_NO_UPDATE_AVAILABLE** | 无可用更新 | 400 |
| **UPDATE_BACKUP_FAILED** | 备份创建失败 | 500 |
| **UNINSTALL_NOT_INSTALLED** | 命令未安装 | 404 |
| **UNINSTALL_DEPENDENCY_EXISTS** | 存在依赖此命令的其他命令 | 409 |
| **CONFIG_INVALID_FORMAT** | 配置文件格式错误 | 422 |
| **CONFIG_VERSION_MISMATCH** | 配置文件版本不兼容 | 422 |
| **SYSTEM_DISK_FULL** | 磁盘空间不足 | 507 |
| **SYSTEM_INTERNAL_ERROR** | 内部错误 | 500 |

### 错误响应示例

**RESOLVE_INVALID_URL**：
```
❌ 安装失败

错误码：RESOLVE_INVALID_URL
原因：Git URL 格式错误（htp://github.com/user/repo）
💡 建议：
  - 使用 HTTPS URL：https://github.com/user/repo
  - 使用 SSH URL：git@github.com:user/repo.git
  - 检查 URL 拼写是否正确

🔗 帮助：/command.install help install
```

**INSTALL_COMMAND_EXISTS**：
```
❌ 安装失败

错误码：INSTALL_COMMAND_EXISTS
原因：命令 wiki-generate 已存在
💡 建议：
  - 使用 --force 强制覆盖
  - 使用 --update 更新到最新版本
  - 使用 --uninstall wiki-generate 先卸载现有版本

🔗 帮助：/command.install help install
```

---

## 事件定义

### 安装事件

```yaml
event: command.installed
timestamp: 2025-01-03T08:00:00Z
data:
  command_name: wiki-generate
  version: 1.0.0
  source_type: git
  source_url: https://github.com/user/repo
  files_installed: 3
  total_size: 10240
```

### 更新事件

```yaml
event: command.updated
timestamp: 2025-01-03T10:30:00Z
data:
  command_name: wiki-generate
  old_version: 1.0.0
  new_version: 1.2.0
  files_updated: 2
  backup_created: true
  backup_path: .claude/backups/wiki-generate.md.20250103_103000.bak
```

### 卸载事件

```yaml
event: command.uninstalled
timestamp: 2025-01-03T11:00:00Z
data:
  command_name: wiki-generate
  version: 1.0.0
  files_removed: 4
  space_freed: 15360
  backup_created: true
```

### 错误事件

```yaml
event: command.install_failed
timestamp: 2025-01-03T12:00:00Z
data:
  command_name: wiki-generate
  error_code: DOWNLOAD_NETWORK_ERROR
  error_message: 网络连接失败
  source_url: https://github.com/user/repo
  retry_count: 3
```

---

**契约完成时间**: 2025-01-03
**下一步**: Phase 2 - 实现策略
