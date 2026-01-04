# 文件冲突处理策略 - 执行摘要

**版本**: 1.0.0
**日期**: 2025-01-03

---

## 快速参考

### 推荐策略速查表

| 场景 | 默认策略 | 命令行参数 | 风险等级 |
|------|----------|-----------|---------|
| **全新安装** | 直接安装 | 无 | 🟢 低 |
| **更新命令** | 备份后覆盖 | `--backup` | 🟡 中 |
| **配置文件（JSON）** | 智能合并 | `--merge` | 🟡 中 |
| **配置文件（其他）** | 保留 | `--keep-config` | 🟢 低 |
| **模板文件** | 备份后覆盖 | `--backup` | 🟡 中 |
| **批量操作** | 跳过冲突 | `--batch` | 🟢 低 |
| **强制操作** | 强制覆盖 | `--force` | 🔴 高 |

---

## 核心发现

### 1. 成熟工具的做法

| 工具 | 默认策略 | 特色功能 | 教训 |
|------|----------|----------|------|
| **npm** | 覆盖 | `--force`, `--legacy-peer-deps` | ⚠️ 无条件覆盖可能丢失数据 |
| **pip** | 覆盖 | `--ignore-conflicts` | ⚠️ 长期存在的问题 |
| **apt** | 询问用户 | 交互式配置文件处理 | ✅ 配置文件需要特殊对待 |
| **Homebrew** | 预览+覆盖 | `--dry-run`, Brewfile 备份 | ✅ 预览功能很重要 |
| **Magentrix** | 可配置 | `overwrite`, `skip`, `manual` | ✅ 提供多种策略 |

### 2. 关键洞察

✅ **没有万能策略**
- 不同场景需要不同的处理方式
- 用户应该有最终控制权

✅ **安全第一**
- 默认策略应该保守（跳过或备份）
- 避免不可逆的数据丢失

✅ **透明度是关键**
- 清晰告知用户将要发生什么
- 提供详细的操作摘要和差异

✅ **分类处理**
- 命令文件、配置文件、模板文件需要不同策略
- 配置文件应该智能合并或保留

---

## 冲突检测机制

### 检测流程

```
1. 快速检查：文件是否存在？
   ├─ 不存在 → 无冲突，直接安装
   └─ 存在 → 继续

2. 哈希比较：内容是否相同？
   ├─ 相同 → 跳过（内容一致）
   └─ 不同 → 继续

3. 来源识别：文件来自哪里？
   ├─ 本命令安装 → 版本冲突
   ├─ 其他命令安装 → 依赖冲突
   └─ 用户文件 → 用户修改冲突

4. 修改分析：修改程度如何？
   ├─ 轻微（< 10%）→ 可能自动合并
   ├─ 中度（10-50%）→ 需要用户决策
   └─ 重大（> 50%）→ 建议保留用户版本
```

### 推荐的检测方法

| 方法 | 用途 | 优先级 |
|------|------|--------|
| **文件存在检查** | 快速排除无冲突场景 | P0 |
| **SHA-256 哈希** | 准确判断内容差异 | P0 |
| **时间戳比较** | 识别用户修改 | P1 |
| **内容差异分析** | 量化修改程度 | P2 |

⚠️ **安全警告**：不要使用 MD5（存在碰撞攻击），使用 SHA-256

---

## 推荐的冲突解决策略

### 策略对比

| 策略 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **覆盖** | • 简单<br>• 确保一致性 | • 丢失修改<br>• 无法回滚 | • `--force`<br>• 内容相同 |
| **跳过** | • 完全安全<br>• 用户控制 | • 安装不完整<br>• 需手动处理 | • 默认策略<br>• 批量安装 |
| **备份后覆盖** | • 可回滚<br>• 保留数据 | • 需管理备份<br>• 占用空间 | • 命令更新<br>• 模板更新 |
| **交互式询问** | • 用户控制<br>• 灵活决策 | • 无法自动化<br>• 较慢 | • 单文件操作<br>• 重要文件 |
| **智能合并** | • 保留修改<br>• 自动化 | • 实现复杂<br>• 可能出错 | • JSON 配置<br>• 有标记的模板 |

### 具体场景建议

#### 场景 1：全新安装
```
策略：直接安装
理由：无冲突
命令：/command.install install <source>
```

#### 场景 2：更新已修改的命令
```
策略：备份后覆盖（默认）
理由：保留用户修改，确保更新
命令：/command.install update wiki-generate
选项：--force / --skip / --ask
```

#### 场景 3：配置文件冲突
```
策略：智能合并（JSON）/ 保留（其他）
理由：保护用户配置
命令：/command.install update my-command
选项：--force-config / --keep-config
```

#### 场景 4：批量安装
```
策略：统一策略 + 摘要报告
理由：提高效率
命令：/command.install install --batch
结果：完整摘要 + 冲突列表
```

---

## 命令行参数设计

### 基本用法

```bash
# 默认安装（跳过冲突）
/command.install install <source>

# 强制覆盖所有冲突
/command.install install <source> --force

# 备份后覆盖
/command.install install <source> --backup

# 交互式询问
/command.install install <source> --ask

# 批量模式（跳过所有冲突）
/command.install install <source> --batch
```

### 文件类型特定参数

```bash
# 命令文件策略
/command.install install <source> --command-strategy=backup

# 配置文件策略
/command.install install <source> --config-strategy=merge

# 模板文件策略
/command.install install <source> --template-strategy=keep
```

### 备份控制

```bash
# 启用备份（默认）
/command.install install <source> --backup

# 禁用备份
/command.install install <source> --no-backup

# 指定备份目录
/command.install install <source> --backup-dir=/path/to/backups

# 限制备份数量
/command.install install <source> --keep-backups=3
```

---

## 配置文件示例

### `.claude/command-install.json`

```json
{
  "version": "1.0.0",
  "settings": {
    "conflict_strategy": {
      "command": "backup",
      "config": "merge",
      "template": "backup",
      "other": "skip"
    },
    "backup": {
      "enabled": true,
      "directory": ".claude/backups",
      "max_age_days": 30,
      "max_count": 3
    },
    "interactive": {
      "enabled": true,
      "batch_mode": "skip"
    },
    "verification": {
      "checksum_algorithm": "sha256",
      "verify_after_install": true
    }
  }
}
```

---

## 用户体验设计

### 错误消息模板

#### 简单冲突
```
⚠️  文件冲突

文件：.claude/commands/wiki-generate.md
原因：文件已存在

解决方案：
• 使用 --force 强制覆盖
• 使用 --skip 跳过此文件
• 使用 --backup 备份后覆盖
```

#### 用户修改检测
```
⚠️  检测到用户修改

文件：.claude/commands/wiki-generate.md
最后安装：2024-12-15 10:30:00
最后修改：2024-12-28 14:22:00
变更统计：+15 行，-8 行

建议：
• 使用 --backup 备份后更新（推荐）
• 使用 --skip 保留当前版本
• 使用 --diff 查看详细差异
```

### 交互式提示

```
⚠️  文件冲突：.claude/commands/wiki-generate.md

现有版本：1.0.0（2024-12-15 安装）
新版本：1.1.0
文件状态：已修改（15 行变更）

[1] 跳过（保留现有版本）
[2] 备份后更新（推荐）
[3] 强制覆盖（不备份）
[4] 查看详细差异
[5] 对所有冲突应用此操作
[6] 取消安装

选择 [1-6，默认 2]:
```

---

## 测试场景

### 必须测试的场景（P0）

| 测试 | 场景 | 预期结果 |
|------|------|----------|
| **无冲突安装** | 文件不存在 | 安装成功 |
| **内容相同** | 内容完全一致 | 跳过安装 |
| **哈希检测** | 内容不同 | 正确检测冲突 |
| **备份创建** | 使用备份策略 | 备份文件存在 |
| **JSON 合并** | 配置文件冲突 | 保留用户配置 |

### 重要测试场景（P1）

| 测试 | 场景 | 预期结果 |
|------|------|----------|
| **完整安装流程** | 多文件部分冲突 | 正确处理所有文件 |
| **更新流程** | 用户修改后更新 | 合并或备份 |
| **批量安装** | 多个冲突 | 生成完整摘要 |
| **权限错误** | 只读目录 | 清晰错误消息 |
| **中断恢复** | 安装中取消 | 清理临时文件 |

---

## 实施路线图

### Phase 1：基础功能（P0）
- [x] 文件存在检查
- [ ] SHA-256 哈希比较
- [ ] 跳过和覆盖策略
- [ ] 基本错误消息
- [ ] 备份功能

**预计时间**：1-2 周

### Phase 2：用户体验（P1）
- [ ] 命令行参数支持
- [ ] 交互式询问
- [ ] JSON 配置合并
- [ ] 详细摘要报告
- [ ] 差异查看

**预计时间**：2-3 周

### Phase 3：增强功能（P2）
- [ ] 批量操作优化
- [ ] 回滚机制
- [ ] 备份管理（自动清理）
- [ ] 性能优化
- [ ] 日志和审计

**预计时间**：2-3 周

### Phase 4：高级功能（P3）
- [ ] 图形化冲突解决界面
- [ ] 自动合并建议（AI）
- [ ] 云端备份集成
- [ ] 冲突预测

**预计时间**：未来迭代

---

## 关键指标

### 成功标准

| 指标 | 目标 | 测量方式 |
|------|------|----------|
| **冲突检测准确性** | ≥ 99.5% | 测试用例通过率 |
| **用户数据安全性** | 0 数据丢失 | 事故报告 |
| **安装成功率** | ≥ 95% | 使用统计 |
| **用户满意度** | ≥ 4.0/5.0 | 用户反馈 |

### 性能目标

| 操作 | 目标时间 |
|------|----------|
| **冲突检测** | < 1 秒（单文件） |
| **哈希计算** | < 0.5 秒（1MB 文件） |
| **备份操作** | < 2 秒（10 个文件） |
| **智能合并** | < 1 秒（JSON 配置） |

---

## 常见问题

### Q1：为什么默认不是"覆盖"？
**A**：根据 npm 和 pip 的教训，无条件覆盖会导致用户数据丢失。保守的默认策略（跳过或备份）更安全。

### Q2：备份文件会占用太多空间吗？
**A**：不会。通过限制备份数量（默认 3 个）和自动清理（30 天），空间占用可控。

### Q3：智能合并可靠吗？
**A**：对于 JSON 配置文件，深度合并是可靠的。对于其他文件，合并结果需要用户验证。

### Q4：如何处理批量安装中的冲突？
**A**：使用 `--batch` 参数统一策略，安装后查看摘要报告，手动处理冲突文件。

### Q5：回滚功能什么时候实现？
**A**：Phase 3（P2）。目前可以通过备份文件手动回滚。

---

## 参考资料

### 研究来源

1. **npm**
   - [StackOverflow: Fix dependency conflict](https://stackoverflow.com/questions/64936044/fix-the-upstream-dependency-conflict-installing-npm-packages)

2. **pip**
   - [pip overwrites files unconditionally (GitHub)](https://github.com/pypa/pip/issues/4625)
   - [Override conflicting dependencies](https://pip.pypa.io/en/latest/ux-research-design/research-results/override-conflicting-dependencies/)

3. **apt**
   - [AskUbuntu: Resolve package conflict](https://askubuntu.com/questions/973988/how-to-resolve-package-conflict-with-apt-get)

4. **Homebrew**
   - [Common Issues Documentation](https://docs.brew.sh/Common-Issues)

5. **安全**
   - [Gradle Dependency Verification](https://docs.gradle.org/current/userguide/dependency_verification.html)

---

## 联系和反馈

如有问题或建议，请：
1. 查看完整研究报告：`file-conflict-strategy-research.md`
2. 提交 Issue 到项目仓库
3. 参与社区讨论

---

**版本**: 1.0.0
**最后更新**: 2025-01-03
**完整报告**: `file-conflict-strategy-research.md`
