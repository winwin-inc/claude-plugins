# 快速开始指南：Claude Code 命令安装器

**功能编号**: 001
**功能名称**: command-install
**指南版本**: 1.0.0
**创建日期**: 2025-01-03
**状态**: ✅ 完成

---

## 目录

1. [5 分钟快速开始](#5-分钟快速开始)
2. [常见使用场景](#常见使用场景)
3. [命令参考](#命令参考)
4. [配置说明](#配置说明)
5. [故障排除](#故障排除)

---

## 5 分钟快速开始

### 步骤 1：安装第一个命令

```bash
# 从 GitHub 仓库安装命令
/command.install install https://github.com/user/wiki-generator-repo
```

**输出**：
```
✅ 命令安装成功：wiki-generate

📦 安装摘要：
  命令名称：wiki-generate
  版本：1.0.0
  来源：https://github.com/user/wiki-generator-repo

📄 已安装文件：
  ✓ .claude/commands/wiki-generate.md
  ✓ .claude/templates/wiki-config.json.template
  ✓ .claude/templates/overview.md.template

💡 使用方法：
  /wiki-generate --full
```

### 步骤 2：列出已安装命令

```bash
# 查看所有已安装的命令
/command.install list
```

**输出**：
```
已安装的命令：

┌─────────────────┬─────────────────────┬────────┬──────────────────────┐
│ 命令名称        │ 描述                │ 版本   │ 安装日期             │
├─────────────────┼─────────────────────┼────────┼──────────────────────┤
│ wiki-generate   │ Wiki 文档生成器     │ 1.0.0  │ 2025-01-03           │
└─────────────────┴─────────────────────┴────────┴──────────────────────┘

总计：1 个命令
```

### 步骤 3：使用已安装的命令

```bash
# 使用新安装的命令生成文档
/wiki-generate --full
```

### 步骤 4：更新命令

```bash
# 更新到最新版本
/command.install update wiki-generate --backup
```

**输出**：
```
✅ 命令更新成功：wiki-generate

📦 更新摘要：
  当前版本：1.0.0
  新版本：1.2.0

🔄 变更内容：
  ✓ 新增：--translate 参数支持多语言翻译
  ✓ 改进：增量更新性能提升 50%

💾 备份位置：
  .claude/backups/wiki-generate.md.20250103_103000.bak
```

### 步骤 5：查看命令信息

```bash
# 查看命令详细信息
/command.install info wiki-generate
```

---

## 常见使用场景

### 场景 1：从 GitHub 安装命令

```bash
# 方式 1：HTTPS URL
/command.install install https://github.com/user/command-repo

# 方式 2：SSH URL
/command.install install git@github.com:user/command-repo.git

# 方式 3：带子目录
/command.install install https://github.com/user/repo/tree/main/commands/my-command
```

### 场景 2：从本地文件安装

```bash
# 安装本地文件
/command.install install ./my-command.md

# 安装本地目录
/command.install install /path/to/commands

# 使用绝对路径
/command.install install ~/Documents/commands/wiki-generate.md
```

### 场景 3：使用预设名称安装

```bash
# 安装预设命令
/command.install install wiki-generator

# 查看所有可用预设
/command.install presets list
```

### 场景 4：批量安装命令

```bash
# 从配置文件批量安装
/command.install install --batch

# 批量安装时跳过冲突
/command.install install https://github.com/user/repo --skip
```

### 场景 5：处理文件冲突

```bash
# 强制覆盖已存在的文件
/command.install install https://github.com/user/repo --force

# 跳过冲突文件（默认）
/command.install install https://github.com/user/repo --skip

# 备份后覆盖
/command.install install https://github.com/user/repo --backup

# 交互式询问
/command.install install https://github.com/user/repo --ask

# 预览模式（不实际安装）
/command.install install https://github.com/user/repo --dry-run
```

### 场景 6：回滚更新

```bash
# 回滚到最新备份
/command.install rollback wiki-generate

# 回滚到指定备份
/command.install rollback wiki-generate --to 20250103_103000

# 查看所有备份
/command.install backups list wiki-generate
```

### 场景 7：卸载命令

```bash
# 卸载命令（带确认）
/command.install uninstall wiki-generate

# 强制卸载（跳过确认）
/command.install uninstall wiki-generate --force

# 卸载并删除所有备份
/command.install uninstall wiki-generate --purge
```

---

## 命令参考

### 命令列表

| 命令 | 描述 | 示例 |
|------|------|------|
| `install` | 安装命令 | `/command.install install <source>` |
| `list` | 列出已安装命令 | `/command.install list` |
| `update` | 更新命令 | `/command.install update <name>` |
| `uninstall` | 卸载命令 | `/command.install uninstall <name>` |
| `info` | 显示命令信息 | `/command.install info <name>` |
| `help` | 显示帮助信息 | `/command.install help` |

### 全局选项

| 选项 | 描述 | 适用于 |
|------|------|--------|
| `--force` | 强制执行，跳过确认 | install, uninstall |
| `--dry-run` | 预览模式，不实际执行 | install, update |
| `--verbose` | 详细输出模式 | 所有命令 |
| `--quiet` | 静默模式，只输出错误 | 所有命令 |

### Install 选项

| 选项 | 描述 | 默认值 |
|------|------|--------|
| `--backup` | 备份后覆盖 | false |
| `--skip` | 跳过冲突文件 | true（批量） |
| `--merge` | 智能合并配置 | false |
| `--ask` | 交互式询问 | false |

### Update 选项

| 选项 | 描述 | 默认值 |
|------|------|--------|
| `--backup` | 更新前自动备份 | true |
| `--merge` | 智能合并配置 | false |
| `--force` | 强制更新 | false |

### Uninstall 选项

| 选项 | 描述 | 默认值 |
|------|------|--------|
| `--backup` | 卸载前自动备份 | true |
| `--force` | 强制卸载（跳过确认） | false |
| `--purge` | 同时删除备份 | false |

---

## 配置说明

### 配置文件位置

```
.claude/command-install.json
```

### 默认配置

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
    "conflict_strategy": "skip",
    "default_source_type": "git",
    "timeout_seconds": 60,
    "max_retries": 3
  }
}
```

### 配置项说明

#### auto_update

**类型**：布尔值
**默认值**：`false`
**描述**：是否自动更新所有命令

**示例**：
```json
{
  "settings": {
    "auto_update": true
  }
}
```

#### backup_before_update

**类型**：布尔值
**默认值**：`true`
**描述**：更新命令前是否自动创建备份

#### keep_backup_count

**类型**：整数
**默认值**：`3`
**描述**：每个命令保留的备份数量

**示例**：
```json
{
  "settings": {
    "keep_backup_count": 5
  }
}
```

#### conflict_strategy

**类型**：字符串
**默认值**：`"skip"`
**可选值**：`skip`、`overwrite`、`backup`、`ask`
**描述**：默认的文件冲突处理策略

**示例**：
```json
{
  "settings": {
    "conflict_strategy": "backup"
  }
}
```

#### install_sources.presets

**类型**：对象
**描述**：预设命令名称到仓库 URL 的映射

**示例**：
```json
{
  "install_sources": {
    "presets": {
      "wiki-generator": {
        "url": "https://github.com/official/wiki-generator",
        "description": "官方 Wiki 生成器",
        "version": "1.0.0"
      },
      "code-review": {
        "url": "https://github.com/official/code-review",
        "description": "代码审查助手",
        "version": "2.1.0"
      }
    }
  }
}
```

### 自定义预设

编辑配置文件，添加自定义预设：

```json
{
  "install_sources": {
    "presets": {
      "my-custom-command": {
        "url": "https://github.com/my-org/my-command",
        "description": "我的自定义命令",
        "version": "1.0.0"
      }
    }
  }
}
```

然后使用预设名称安装：

```bash
/command.install install my-custom-command
```

---

## 故障排除

### 问题 1：安装失败 - 命令已存在

**错误**：
```
❌ 安装失败

错误码：INSTALL_COMMAND_EXISTS
原因：命令 wiki-generate 已存在
```

**解决方案**：

```bash
# 方案 1：更新现有命令
/command.install update wiki-generate

# 方案 2：强制覆盖
/command.install install https://github.com/user/repo --force

# 方案 3：先卸载再安装
/command.install uninstall wiki-generate
/command.install install https://github.com/user/repo
```

---

### 问题 2：无法连接到 Git 仓库

**错误**：
```
❌ 安装失败

错误码：DOWNLOAD_NETWORK_ERROR
原因：无法连接到仓库
```

**解决方案**：

1. **检查网络连接**：
   ```bash
   ping github.com
   ```

2. **检查 URL 是否正确**：
   ```bash
   # 正确格式
   https://github.com/user/repo
   git@github.com:user/repo.git
   ```

3. **使用 SSH 而不是 HTTPS**：
   ```bash
   /command.install install git@github.com:user/repo.git
   ```

4. **稍后重试**：
   ```bash
   /command.install install https://github.com/user/repo --max-retries 5
   ```

---

### 问题 3：文件冲突

**错误**：
```
❌ 安装失败

错误码：INSTALL_FILE_CONFLICT
原因：文件 .claude/commands/wiki-generate.md 已存在
```

**解决方案**：

```bash
# 方案 1：跳过冲突（默认）
/command.install install https://github.com/user/repo --skip

# 方案 2：备份后覆盖
/command.install install https://github.com/user/repo --backup

# 方案 3：强制覆盖（不推荐）
/command.install install https://github.com/user/repo --force

# 方案 4：交互式选择
/command.install install https://github.com/user/repo --ask
```

---

### 问题 4：权限不足

**错误**：
```
❌ 安装失败

错误码：INSTALL_PERMISSION_DENIED
原因：没有写入 .claude/ 目录的权限
```

**解决方案**：

1. **检查目录权限**：
   ```bash
   ls -la .claude/
   ```

2. **修改权限**（Linux/macOS）：
   ```bash
   chmod 755 .claude/
   chmod 644 .claude/*
   ```

3. **使用 sudo（不推荐）**：
   ```bash
   sudo /command.install install https://github.com/user/repo
   ```

---

### 问题 5：磁盘空间不足

**错误**：
```
❌ 安装失败

错误码：SYSTEM_DISK_FULL
原因：磁盘空间不足
```

**解决方案**：

1. **检查磁盘空间**：
   ```bash
   df -h
   ```

2. **清理旧备份**：
   ```bash
   /command.install backups cleanup --keep 1
   ```

3. **清理系统临时文件**：
   ```bash
   # Linux/macOS
   rm -rf /tmp/command-install-*

   # Windows
   del %TEMP%\command-install-*
   ```

---

### 问题 6：更新后配置丢失

**问题**：更新命令后，配置文件被重置

**解决方案**：

1. **使用智能合并**：
   ```bash
   /command.install update wiki-generate --merge
   ```

2. **手动恢复配置**：
   ```bash
   # 查看备份
   /command.install backups list wiki-generate

   # 恢复备份
   /command.install restore wiki-generate --from 20250103_103000
   ```

3. **修改配置文件保护策略**：
   ```json
   {
     "settings": {
       "conflict_strategy": "backup",
       "protected_files": [
         ".claude/wiki-config.json"
       ]
     }
   }
   ```

---

## 最佳实践

### 1. 定期更新命令

```bash
# 查看需要更新的命令
/command.install list --updates-available

# 更新所有命令
/command.install update --all
```

### 2. 管理备份

```bash
# 定期清理旧备份
/command.install backups cleanup --keep 3

# 查看备份占用空间
/command.install backups stats
```

### 3. 使用配置文件

为团队项目创建共享配置：

```json
{
  "install_sources": {
    "presets": {
      "team-standard": "https://github.com/team/commands"
    }
  },
  "settings": {
    "auto_update": true,
    "backup_before_update": true
  }
}
```

### 4. 验证安装

```bash
# 安装后验证命令
/command.install info wiki-generate

# 检查文件完整性
/command.install verify wiki-generate
```

---

## 进阶使用

### 创建自定义命令包

1. **创建仓库结构**：
   ```
   my-command-repo/
   ├── commands/
   │   └── my-command.md
   ├── templates/
   │   └── template.md
   └── command-install.json
   ```

2. **配置元数据**：
   ```json
   {
     "name": "my-command",
     "version": "1.0.0",
     "description": "我的自定义命令"
   }
   ```

3. **发布到 GitHub**：
   ```bash
   git init
   git add .
   git commit -m "初始版本"
   git push origin main
   ```

4. **安装命令**：
   ```bash
   /command.install install https://github.com/user/my-command-repo
   ```

---

**指南完成时间**: 2025-01-03
**最后更新**: 2025-01-03
