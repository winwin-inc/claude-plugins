# 命令安装器文档索引

**版本**: 1.0.0
**最后更新**: 2025-01-03

---

## 文档导航

### 📋 核心文档

| 文档 | 描述 | 行数 | 适用对象 |
|------|------|------|----------|
| **[spec.md](spec.md)** | 功能规范 - 完整的需求和验收标准 | 703 | 产品经理、开发者 |
| **[EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)** | 执行摘要 - 快速参考指南 | 416 | 所有角色 |
| **[file-conflict-strategy-research.md](file-conflict-strategy-research.md)** | 文件冲突策略研究报告 - 完整分析和最佳实践 | 1873 | 开发者、架构师 |
| **[decision-tree.md](decision-tree.md)** | 决策流程图 - 可视化决策逻辑 | 565 | 开发者 |
| **[source-parsing-research.md](source-parsing-research.md)** | 源码解析研究报告 | 1604 | 开发者 |

### 📁 辅助文档

| 目录 | 描述 |
|------|------|
| **[checklists/](checklists/)** | 需求检查清单和验收标准 |

---

## 快速开始

### 对于产品经理

1. **第一步**: 阅读 [spec.md](spec.md) 了解完整功能需求
2. **第二步**: 查看 [checklists/requirements.md](checklists/requirements.md) 了解验收标准
3. **第三步**: 参考 [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md) 了解关键决策

### 对于开发者

1. **第一步**: 阅读 [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md) 快速了解整体设计
2. **第二步**: 深入阅读 [file-conflict-strategy-research.md](file-conflict-strategy-research.md) 理解冲突处理机制
3. **第三步**: 查看 [decision-tree.md](decision-tree.md) 理解决策流程
4. **第四步**: 阅读 [spec.md](spec.md) 了解详细需求
5. **第五步**: 查看 [source-parsing-research.md](source-parsing-research.md) 了解实现细节

### 对于测试工程师

1. **第一步**: 阅读 [spec.md](spec.md) 第 2 节（用户场景）和第 3 节（功能需求）
2. **第二步**: 查看 [checklists/requirements.md](checklists/requirements.md) 了解验收标准
3. **第三步**: 参考 [file-conflict-strategy-research.md](file-conflict-strategy-research.md) 第 9 节（测试场景）

---

## 文档阅读顺序

### 🎯 快速通道（30 分钟）

```
1. EXECUTIVE_SUMMARY.md (10 分钟)
   ↓
2. spec.md - 第 1-3 节 (15 分钟)
   ↓
3. decision-tree.md - 前 3 个流程图 (5 分钟)
```

### 📚 完整理解（2 小时）

```
1. spec.md (完整) - 30 分钟
   ↓
2. file-conflict-strategy-research.md (完整) - 60 分钟
   ↓
3. decision-tree.md (完整) - 20 分钟
   ↓
4. source-parsing-research.md - 10 分钟
```

### 🔍 深度研究（4 小时）

```
完整阅读所有文档 + 参考资料链接
```

---

## 关键概念速查

### 文件冲突处理策略

| 策略 | 描述 | 命令行参数 | 默认场景 |
|------|------|-----------|---------|
| **跳过 (Skip)** | 保留现有文件 | `--skip` | 批量安装 |
| **备份后覆盖 (Backup)** | 创建备份后更新 | `--backup` | 命令更新 |
| **强制覆盖 (Force)** | 直接覆盖 | `--force` | 用户明确要求 |
| **交互式询问 (Ask)** | 询问用户选择 | `--ask` | 单个重要文件 |
| **智能合并 (Merge)** | 合并文件内容 | `--merge` | JSON 配置 |

### 文件类型分类

```
系统文件
├── 命令文件 (.claude/commands/*.md)
│   └── 默认策略: backup
├── 配置文件 (.claude/*.json)
│   └── 默认策略: merge
└── 模板文件 (.claude/templates/*)
    └── 默认策略: backup

用户文件
├── 用户自定义命令
│   └── 默认策略: ask
├── 用户修改的模板
│   └── 默认策略: ask
└── 用户配置文件
    └── 默认策略: keep
```

### 检测流程

```
1. 文件是否存在?
   ├─ 否 → 直接安装
   └─ 是 → 继续

2. 内容是否相同? (SHA-256)
   ├─ 是 → 跳过
   └─ 否 → 继续

3. 文件类型?
   ├─ 命令文件 → 检查用户修改
   ├─ 配置文件 → 尝试合并
   ├─ 模板文件 → 检查自定义区域
   └─ 其他文件 → 应用通用策略

4. 用户修改?
   ├─ 否 → 备份后覆盖
   └─ 是 → 应用用户策略

5. 执行操作并记录
```

---

## 常见问题快速链接

### 冲突检测

- **Q: 如何检测文件冲突？**
  A: [file-conflict-strategy-research.md](file-conflict-strategy-research.md) 第 2 节

- **Q: 使用什么哈希算法？**
  A: [file-conflict-strategy-research.md](file-conflict-strategy-research.md) 第 2.2 节（推荐 SHA-256）

### 冲突解决

- **Q: 默认策略是什么？**
  A: [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md) "推荐策略速查表"

- **Q: 如何处理配置文件冲突？**
  A: [file-conflict-strategy-research.md](file-conflict-strategy-research.md) 第 5.3 节

- **Q: 智能合并如何工作？**
  A: [file-conflict-strategy-research.md](file-conflict-strategy-research.md) 第 3.5 节

### 最佳实践

- **Q: 其他工具如何处理冲突？**
  A: [file-conflict-strategy-research.md](file-conflict-strategy-research.md) 第 4 节（npm、pip、apt、Homebrew）

- **Q: 如何设计错误消息？**
  A: [file-conflict-strategy-research.md](file-conflict-strategy-research.md) 第 7 节

### 实现

- **Q: 如何实现决策树？**
  A: [decision-tree.md](decision-tree.md) "主决策流程图"

- **Q: 配置文件结构是什么？**
  A: [file-conflict-strategy-research.md](file-conflict-strategy-research.md) 第 6 节

### 测试

- **Q: 需要哪些测试场景？**
  A: [file-conflict-strategy-research.md](file-conflict-strategy-research.md) 第 9 节

---

## 实现路线图

### Phase 1: 基础功能 (P0) - 1-2 周

**文档参考**:
- [spec.md](spec.md) 第 3.1 节（核心命令）
- [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md) "Phase 1"

**任务**:
- [x] 文件存在检查
- [ ] SHA-256 哈希比较
- [ ] 跳过和覆盖策略
- [ ] 基本错误消息
- [ ] 备份功能

**测试**:
- [file-conflict-strategy-research.md](file-conflict-strategy-research.md) 第 9.1 节（单元测试）

### Phase 2: 用户体验 (P1) - 2-3 周

**文档参考**:
- [spec.md](spec.md) 第 3.2 节（配置管理）
- [decision-tree.md](decision-tree.md) "交互式冲突解决流程"

**任务**:
- [ ] 命令行参数支持
- [ ] 交互式询问
- [ ] JSON 配置合并
- [ ] 详细摘要报告
- [ ] 差异查看

**测试**:
- [file-conflict-strategy-research.md](file-conflict-strategy-research.md) 第 9.2 节（集成测试）

### Phase 3: 增强功能 (P2) - 2-3 周

**文档参考**:
- [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md) "Phase 3"
- [decision-tree.md](decision-tree.md) "批量安装冲突处理流程"

**任务**:
- [ ] 批量操作优化
- [ ] 回滚机制
- [ ] 备份管理（自动清理）
- [ ] 性能优化
- [ ] 日志和审计

**测试**:
- [file-conflict-strategy-research.md](file-conflict-strategy-research.md) 第 9.3 节（边界测试）

---

## 参考资料链接

### 外部资源

**npm**:
- [StackOverflow: Fix dependency conflict](https://stackoverflow.com/questions/64936044/fix-the-upstream-dependency-conflict-installing-npm-packages)

**pip**:
- [pip overwrites files unconditionally (GitHub)](https://github.com/pypa/pip/issues/4625)
- [Override conflicting dependencies](https://pip.pypa.io/en/latest/ux-research-design/research-results/override-conflicting-dependencies/)

**apt**:
- [AskUbuntu: Resolve package conflict](https://askubuntu.com/questions/973988/how-to-resolve-package-conflict-with-apt-get)
- [apt.conf Configuration Reference](https://manpages.ubuntu.com/manpages/xenial/man5/apt.conf.5.html)

**Homebrew**:
- [Common Issues Documentation](https://docs.brew.sh/Common-Issues)

**安全**:
- [Gradle Dependency Verification](https://docs.gradle.org/current/userguide/dependency_verification.html)

### 内部文档

- [CLAUDE.md](../../CLAUDE.md) - 项目指南
- [PROJECT-SUMMARY.md](../../PROJECT-SUMMARY.md) - 项目总览
- [specs/README.md](../README.md) - 规范文档索引

---

## 贡献指南

### 如何更新文档

1. **保持同步**: 如果修改了实现，请同步更新相关文档
2. **版本控制**: 在文档末尾注明版本和更新日期
3. **交叉引用**: 使用相对路径引用其他文档
4. **示例代码**: 提供可运行的代码示例

### 文档规范

- 使用 Markdown 格式
- 中文为主，技术术语保留英文
- 使用表格和列表提高可读性
- 添加适当的 emoji 增强视觉效果
- 代码示例使用语法高亮

---

## 反馈和问题

### 报告问题

如果您发现文档中的问题：
1. 检查是否已有相关 Issue
2. 创建新 Issue，标明文档路径
3. 描述问题并建议改进

### 提出改进

如果您有改进建议：
1. 在 Issue 中描述您的想法
2. 说明改进的原因和预期效果
3. 如果可能，提供具体的修改方案

---

## 文档统计

| 文档 | 行数 | 字数 | 主题 |
|------|------|------|------|
| spec.md | 703 | ~15K | 功能规范 |
| EXECUTIVE_SUMMARY.md | 416 | ~10K | 执行摘要 |
| file-conflict-strategy-research.md | 1873 | ~45K | 冲突策略研究 |
| decision-tree.md | 565 | ~12K | 决策流程 |
| source-parsing-research.md | 1604 | ~38K | 源码解析 |
| **总计** | **5161** | **~120K** | **完整文档集** |

---

**文档版本**: 1.0.0
**最后更新**: 2025-01-03
**维护者**: Repo Wiki Generator 项目团队
