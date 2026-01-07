# Winwin Claude Code 插件

> 自动生成和维护项目 Wiki 文档的 Claude Code 插件，提供文档生成、Git 提交助手和会话管理功能。

## ✨ 主要功能

### 📚 Wiki 文档生成器

#### 核心功能
- **智能增量更新** - 只更新受代码变更影响的文档，性能提升 60-80%
- **手动编辑保护** - 自动识别并保留用户手动编辑的内容
- **智能变更检测** - Git diff + 哈希值双重检测机制
- **元数据追踪** - 动态追踪文档与源文件的映射关系
- **配置驱动**：通过 `{output_dir}/wiki-config.json` 自定义生成行为
- **智能检测**：自动识别项目技术栈并生成相应文档
- **多语言支持**：支持中文和英文文档生成
- **分层结构**：按照项目标准组织文档（概述、架构、API、快速开始等）
- **模板系统**：提供丰富的文档模板，支持自定义

```bash
# 生成 Wiki 文档（默认增量模式）
/wiki-generate

# 完整重新生成（覆盖所有现有文档）
/wiki-generate --full

# 显式增量更新
/wiki-generate --incremental
```

### 📝 Git 提交助手
- **约定式提交**：自动生成符合规范的提交消息
- **表情符号**：为每种提交类型添加合适的表情符号
- **提交前检查**：可选的 lint、build 和文档更新检查
- **智能分析**：自动检测更改并建议是否需要拆分提交

### 💾 会话管理
- **保存会话**：保存 Claude Code 会话状态供后续使用
- **会话恢复**：快速恢复之前的工作上下文
- **数据迁移**：提供会话数据迁移脚本

## 📦 安装

### 方式一：从 GitHub 仓库安装（推荐）

```bash
# 在 Claude Code 中运行
/plugin marketplace add winwin-inc/claude-plugins
```

然后安装插件：

```bash
/plugin install winwin-code-assit@winwin-inc/claude-plugins
```

### 方式二：从本地目录安装（用于开发）

1. **克隆仓库**
   ```bash
   git clone https://github.com/winwin-inc/claude-plugins.git
   cd claude-plugins/repo-wiki
   ```

2. **在 Claude Code 中添加本地市场**
   ```bash
   # 在 Claude Code 中运行
   /plugin marketplace add /path/to/claude-plugins
   ```

3. **安装插件**
   ```bash
   /plugin install winwin-code-assit@claude-plugins
   ```

### 方式三：使用 --plugin-dir 测试（开发模式）

```bash
# 在命令行中启动 Claude Code 并加载插件
claude --plugin-dir /path/to/claude-plugins
```

这种方式适合开发测试，无需安装即可使用插件。

## 🚀 使用方法

### Wiki 文档生成

#### 基础用法

```bash
# 生成 Wiki 文档（使用默认配置）
/wiki-generate

# 完整重新生成（覆盖所有现有文档）
/wiki-generate --full
```

#### 配置文件

配置文件位于 `{output_dir}/wiki-config.json`。首次运行 `/wiki-generate` 时，系统会自动创建配置文件。

默认位置：`docs/wiki-config.json`

```json
{
  "output_dir": "docs",
  "exclude_patterns": [
    "node_modules",
    "dist",
    ".git",
    "build"
  ],
  "include_patterns": [
    "src/**/*.ts",
    "lib/**/*.ts"
  ],
  "template_dir": ".claude-plugin/templates/wiki-generate",
  "quality_threshold": 80,
  "diagrams": {
    "enabled": true,
    "detail_level": "medium"
  },
  "language": "zh",
  "tech_stack": {
    "backend": ["python", "fastapi"],
    "frontend": ["react", "typescript"],
    "database": ["postgresql"]
  }
}
```

#### 配置选项

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `output_dir` | string | `"docs"` | 文档输出目录 |
| `exclude_patterns` | array | `["node_modules"]` | 排除的文件模式 |
| `include_patterns` | array | `["**/*"]` | 包含的文件模式 |
| `template_dir` | string | `".claude-plugin/templates/wiki-generate"` | 模板目录 |
| `quality_threshold` | number | `80` | 文档质量阈值（0-100） |
| `diagrams.enabled` | boolean | `true` | 是否生成图表 |
| `diagrams.detail_level` | string | `"medium"` | 图表详细程度（low/medium/high） |
| `language` | string | `"zh"` | 文档语言（zh/en） |
| `tech_stack` | object | `{}` | 技术栈配置 |

#### 生成的文档结构

```
docs/
├── index.md                    # 文档索引
├── overview.md                 # 项目概述
├── quickstart.md              # 快速开始
├── architecture.md            # 系统架构
├── api.md                     # API 文档
├── development.md             # 开发指南
└── modules/                   # 模块文档
    ├── module-name.md
    └── ...
```

### Git 提交助手

#### 基础用法

```bash
# 创建标准提交（运行提交前检查）
/commit

# 跳过提交前检查
/commit --no-verify
```

#### 提交前检查

默认运行以下检查：
- `pnpm lint` - 代码质量检查
- `pnpm build` - 构建验证
- `pnpm generate:docs` - 文档更新

#### 支持的提交类型

| 类型 | 表情符号 | 说明 |
|------|----------|------|
| `feat` | ✨ | 新功能 |
| `fix` | 🐛 | 错误修复 |
| `docs` | 📝 | 文档更改 |
| `style` | 💄 | 代码风格更改 |
| `refactor` | ♻️ | 代码重构 |
| `perf` | ⚡ | 性能改进 |
| `test` | ✅ | 测试相关 |
| `chore` | 🔧 | 工具、配置 |

#### 示例提交消息

```
✨ feat: 添加用户认证系统

- 实现登录/注册功能
- 添加 JWT 认证
- 集成 OAuth2.0
```

### 会话管理

#### 保存会话

```bash
# 保存当前会话
/save-session

# 指定会话名称
/save-session feature-implementation
```

#### 会话文件位置

会话默认保存在：
```
docs/plans/sessions/
└── 2026-01-06-feature-implementation.md
```

#### 会话数据迁移

如果你有旧版本的会话数据，可以使用迁移脚本：

```bash
# 运行迁移脚本
./scripts/migrate-sessions.sh
```

这将：
1. 备份现有数据到 `docs/claude-sessions/backup/`
2. 迁移会话到 `docs/plans/sessions/`
3. 验证迁移结果

## 📁 项目结构

```
claude-plugins/
├── .claude-plugin/            # 插件配置
│   ├── plugin.json            # 插件元数据
│   ├── templates/             # Wiki 生成模板
│   │   └── wiki-generate/     # 文档模板
│   │       ├── en/           # 英文模板
│   │       ├── zh/           # 中文模板
│   │       └── *.template    # 通用模板
│   └── scripts/              # 实用脚本
│       └── migrate-sessions.sh
├── commands/                  # Claude Code 命令
│   ├── commit.md             # Git 提交助手
│   ├── save-session.md       # 会话管理
│   └── wiki-generate.md      # Wiki 生成器
├── templates/                 # 插件资源（已移动）
└── scripts/                   # 插件脚本（已移动）
```

## 🔧 高级配置

### 插件管理

#### 列出已安装的市场

```bash
# 查看所有已添加的市场
/plugin marketplace list
```

#### 浏览可用插件

```bash
# 查看来自所有市场的可用插件
/plugin
```

#### 更新市场

```bash
# 从市场来源刷新插件列表
/plugin marketplace update winwin-inc/claude-plugins
```

#### 移除市场

```bash
# 从配置中移除市场
/plugin marketplace remove winwin-inc/claude-plugins
```

#### 配置团队市场

在项目根目录的 `.claude/settings.json` 中配置自动市场安装：

```json
{
  "extraKnownMarketplaces": {
    "winwin-plugins": {
      "source": {
        "source": "github",
        "repo": "winwin-inc/claude-plugins"
      }
    }
  },
  "enabledPlugins": [
    "winwin-code-assit@winwin-plugins"
  ]
}
```

当团队成员信任项目文件夹时，Claude Code 会自动安装这些市场和插件。

### 自定义文档模板

1. 复制默认模板：
   ```bash
   cp -r templates/wiki-generate my-templates
   ```

2. 修改模板文件（支持变量插值）：
   ```markdown
   # {{PROJECT_NAME}}

   **作者**: {{AUTHOR}}
   **版本**: {{VERSION}}
   **技术栈**: {{TECH_STACK}}
   ```

3. 在 `wiki-config.json` 中指定模板目录：
   ```json
   {
     "template_dir": "my-templates"
   }
   ```

### 插件开发

#### 本地测试

```bash
# 使用 --plugin-dir 测试本地插件
claude --plugin-dir /path/to/repo-wiki
```

#### 插件调试

1. 检查插件是否加载：
   ```bash
   # 在 Claude Code 中
   /agents
   ```

2. 查看可用命令：
   ```bash
   /
   ```

3. 查看插件日志：
   ```bash
   # Claude Code 日志位置
   ~/.claude/logs/
   ```

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m '✨ feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

### 代码规范

- 使用 `/commit` 命令创建提交
- 遵循约定式提交规范
- 添加必要的测试
- 更新相关文档

## 📖 常见问题

### Q: 为什么命令无法识别？

**A**: 请确保：
1. 插件市场已正确添加：`/plugin marketplace list`
2. 插件已安装：输入 `/plugin` 查看可用插件
3. 命令文件在插件根目录的 `commands/` 目录
4. `plugin.json` 配置正确且包含必需字段
5. 如果使用 `--plugin-dir`，确保路径正确

### Q: Wiki 生成失败怎么办？

**A**: 检查：
1. `{output_dir}/wiki-config.json` 配置是否正确（默认为 `docs/wiki-config.json`）
2. 输出目录是否有写权限
3. 模板文件是否完整
4. 查看错误日志获取详细信息

### Q: 如何自定义提交前检查？

**A**: 编辑 `commands/commit.md`，修改以下部分：
```markdown
# 默认运行
pnpm lint
pnpm build
pnpm generate:docs
```

替换为你项目的实际命令。

### Q: 支持哪些文档语言？

**A**: 当前支持：
- 中文（zh）- 默认
- 英文（en）

可以扩展模板以支持更多语言。

### Q: 如何创建自己的插件市场？

**A**: 参考以下步骤：
1. 创建 GitHub 仓库
2. 在根目录添加 `.claude-plugin/marketplace.json` 文件
3. 在 `plugins` 数组中列出你的插件
4. 使用 `/plugin marketplace add owner/repo` 安装市场

详见：[插件市场文档](https://code.claude.com/docs/zh-CN/plugin-marketplaces)

## 📝 更新日志

### v1.0.0 (2026-01-06)

#### ✨ 新功能
- Wiki 文档生成器
- Git 提交助手（约定式提交 + 表情符号）
- 会话管理（保存/恢复/迁移）

#### 🔧 改进
- 优化插件目录结构以符合 Claude Code 规范`
- 简化 plugin.json 配置
- 添加多语言模板支持

#### 🐛 修复
- 修复命令无法识别的问题
- 修复插件安装后无可用命令的问题

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🔗 相关链接

### 官方文档
- [Claude Code 官方文档](https://code.claude.com/docs)
- [插件开发指南](https://code.claude.com/docs/en/plugins)
- [插件市场文档](https://code.claude.com/docs/zh-CN/plugin-marketplaces)
- [约定式提交规范](https://www.conventionalcommits.org/)

### 社区资源
- [Building My First Claude Code Plugin](https://alexop.dev/posts/building-my-first-claude-code-plugin/) - 实用插件开发教程
- [Claude Code Plugin 2025 指南](https://skywork.ai/blog/ai-agent/claude-code-plugin-2025-plugins-sonnet-4-5-developer-tools/) - 2025年插件系统更新
- [如何用插件定制你的 Claude Code](https://sorrycc.com/claude-code-plugins) - 中文插件定制指南

## 👥 作者

**Winwin.Inc Team**

- 网站: https://winwin.inc
- 邮箱: support@winwin.inc
- GitHub: [@winwin-inc](https://github.com/winwin-inc)

## 🙏 致谢

感谢 Anthropic 团队开发 Claude Code 和强大的插件系统！

---

**Made with ❤️ by Winwin.Inc Team**
