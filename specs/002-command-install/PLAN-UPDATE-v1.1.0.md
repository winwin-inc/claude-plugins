# Plan.md 更新报告 v1.1.0

**更新日期**: 2025-01-03
**更新类型**: 重大架构澄清
**版本**: 1.0.0 → 1.1.0

---

## 更新背景

在实现过程中，用户提供了关键的架构澄清：

**用户原话**:
> "本项目名称为 wiki-generator，只需要用命令 uvx wiki-generator 就能把 .claude/commands/wiki-generate.md 和 .claude/templates 安装到当前命令运行目录下"

这是一个**重大的架构定位变更**，将项目从通用的"命令安装器"重新定位为专用的"wiki-generator 安装工具"。

---

## 主要变更

### 1. 项目命名变更

| 旧名称 | 新名称 | 影响 |
|--------|--------|------|
| `command-install` | `wiki-generator` | 所有文档、目录、包名 |
| 通用命令安装器 | Wiki Generator 专用安装器 | 项目定位和用途 |

### 2. 调用方式变更

| 旧方式 | 新方式 | 理由 |
|--------|--------|------|
| `python command-install/cli.py <action>` | `uvx wiki-generator <action>` | 现代 Python 工具链 |
| `python -m command-install.cli <action>` | `python -m wiki_generator.cli <action>` | 模块命名 |
| `command-install <action>` | `wiki-generator <action>` | 命令名称 |

**推荐方式**: `uvx wiki-generator <action>`
- uv 会自动处理依赖管理
- 无需手动安装，直接运行
- 符合现代 Python 工具最佳实践

### 3. 项目定位变更

**旧定位**: 通用命令安装管理器
- 可以安装任何 Claude Code 命令
- 通用的命令市场工具

**新定位**: Wiki Generator 专用安装工具
- 主要用途：安装 wiki-generate.md 和 templates
- 专用工具，明确目标
- 简化安装流程

### 4. 目录结构变更

```bash
# 旧结构
command-install/
├── cli.py
├── pyproject.toml
└── ...

# 新结构
wiki-generator/           # 目录名变更
├── cli.py
├── pyproject.toml        # 包名变更
└── ...
```

---

## 详细变更列表

### 文档控制部分

- [x] 功能名称: `command-install` → `wiki-generator`
- [x] 计划版本: 1.0.0 → 1.1.0
- [x] 添加版本历史记录

### 执行摘要部分

- [x] 项目目标：从"通用命令安装管理器" → "Wiki Generator 安装工具"
- [x] 核心价值：添加"一键安装"，强调 `uvx wiki-generator`
- [x] 关键成果：添加"专用用途"，明确安装目标
- [x] 实现策略：
  - 技术栈：Python 3.8+ + uv（强调依赖管理和执行）
  - 调用方式：优先推荐 `uvx wiki-generator`
  - 添加"默认目标"：安装到当前运行目录

### 技术上下文部分

- [x] 项目类型：独立 Python CLI 工具 → **专用安装器**
- [x] 添加"项目名称": wiki-generator
- [x] 添加"执行方式": uvx wiki-generator

### 技术决策部分

添加两个新决策：

| 决策点 | 决策结果 | 理由 |
|--------|----------|------|
| **项目命名** | wiki-generator（而非 command-install） | 明确用途，专用安装器 |
| **执行方式** | uvx wiki-generator（而非 python cli.py） | 现代 Python 工具链，自动依赖管理 |

### 宪章合规性检查部分

#### 原则 3：工具定位原则
- [x] 更新为：`wiki-generator` 是一个独立的 Python CLI 工具
- [x] 添加：通过 `uvx wiki-generator` 调用，自动处理依赖
- [x] 明确：用于将 wiki-generate.md 和 templates 安装到目标项目
- [x] 强调：专用工具，不是通用命令安装器

#### 原则 4：命令一致性原则
- [x] 命令工具名称：`command-install` → `wiki-generator`
- [x] 命令格式：添加 `uvx wiki-generator <action>` 选项
- [x] 调用示例：全面更新为三种方式，优先 uvx

```bash
# 方式 1：使用 uvx（推荐）
uvx wiki-generator install <source>

# 方式 2：安装后直接调用
wiki-generator install <source>

# 方式 3：模块方式（开发模式）
python -m wiki_generator.cli install <source>
```

### 合规模要部分

- [x] 关键亮点：
  - "单一命令架构" → "专用工具架构"
  - 添加"现代执行方式：使用 uvx wiki-generator 调用"
  - 添加"清晰的专用安装器定位"

### 附录 A：命令实现检查清单

- [x] 项目结构：`command-install/` → `wiki-generator/`
- [x] 检查清单：不创建 `.claude/commands/wiki-generator.md`（而非 command-install.md）

### 计划状态部分

- [x] 最后更新：添加"（更新项目命名和调用方式）"
- [x] 下一步：添加"（反映 wiki-generator 命名）"

---

## 影响分析

### 对现有代码的影响

**当前状态**: 已经实现 Phase 1-4 (MVP)，共 49 个任务完成
**目录名称**: `command-install/`
**包名**: `command-install`

**需要重命名**:
1. 目录：`command-install/` → `wiki-generator/`
2. pyproject.toml 中的包名和项目元数据
3. 所有引用包名的代码
4. CLI 入口点配置

### 对后续实现的影响

**Phase 5-6** (update, uninstall):
- 使用新的包名 `wiki_generator`
- 使用新的命令名称 `wiki-generator`
- 确保所有文档引用新名称

**Phase 7** (高级功能):
- 专注于 wiki-generate.md 和 templates 的安装
- 不考虑通用化扩展

---

## 下一步行动

### 立即行动

1. ✅ **更新 plan.md** (已完成)
   - 反映新的项目命名
   - 更新所有命令示例
   - 更新技术决策

2. ⏳ **更新 tasks.md** (待执行)
   - 运行 `/speckit.tasks` 重新生成任务列表
   - 确保任务反映新的命名和架构
   - 更新所有任务描述

3. ⏳ **重命名代码目录** (待执行)
   - `command-install/` → `wiki-generator/`
   - 更新 pyproject.toml
   - 更新所有 import 语句
   - 更新 CLI 入口点

4. ⏳ **验证实现** (待执行)
   - 确保现有功能正常工作
   - 测试 `uvx wiki-generator` 调用方式
   - 更新测试用例

### 后续改进

1. **更新文档**:
   - README.md
   - 使用说明
   - 示例代码

2. **发布准备**:
   - PyPI 包名：`wiki-generator`
   - 确保 uvx 可以正确调用
   - 添加安装说明

3. **代码审查**:
   - 检查所有旧的引用
   - 确保没有硬编码的 "command-install"
   - 验证包名一致性

---

## 验收标准

- [x] plan.md 全面更新完成
- [ ] tasks.md 反映新命名
- [ ] 代码目录重命名为 wiki-generator
- [ ] pyproject.toml 更新包名
- [ ] 所有 import 语句更新
- [ ] CLI 可以通过 `uvx wiki-generator` 调用
- [ ] 所有文档更新
- [ ] 测试通过

---

## 重要提醒

### 关键决策回顾

1. **项目不是通用的命令安装器**，而是专门为 wiki-generator 设计的安装工具
2. **主要用途是安装**：
   - `.claude/commands/wiki-generate.md`
   - `.claude/templates/`
3. **推荐调用方式是 `uvx wiki-generator`**，而非直接运行 Python 脚本
4. **不创建 `.claude/commands/wiki-generator.md`** 文件

### 避免混淆

- ❌ 不要将此工具视为通用的"命令市场"
- ❌ 不要添加其他命令的安装逻辑
- ✅ 专注于 wiki-generator 的安装需求
- ✅ 保持简单、专用

---

**更新完成时间**: 2025-01-03
**更新者**: Claude Code (via /speckit.plan)
**下一步**: 执行 `/speckit.tasks` 重新生成任务列表
