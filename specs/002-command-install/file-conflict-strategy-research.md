# 文件冲突处理策略研究报告

**版本**: 1.0.0
**创建日期**: 2025-01-03
**研究范围**: Claude Code 命令安装器文件冲突处理
**研究者**: Repo Wiki Generator 项目团队

---

## 目录

1. [执行摘要](#执行摘要)
2. [冲突检测机制](#冲突检测机制)
3. [冲突解决策略对比](#冲突解决策略对比)
4. [成熟工具最佳实践](#成熟工具最佳实践)
5. [推荐策略](#推荐策略)
6. [决策树设计](#决策树设计)
7. [配置设计](#配置设计)
8. [用户体验设计](#用户体验设计)
9. [测试场景](#测试场景)
10. [实现建议](#实现建议)
11. [参考资料](#参考资料)

---

## 执行摘要

### 研究结论

通过对 npm、pip、apt、Homebrew 等成熟包管理器的研究，我们发现：

1. **没有万能策略**：不同场景需要不同的冲突处理方式
2. **用户控制权优先**：提供灵活的配置选项比单一策略更重要
3. **安全第一**：默认策略应该保守，避免数据丢失
4. **透明度是关键**：清晰告知用户将要发生什么操作

### 核心推荐

为 Claude Code 命令安装器推荐的策略组合：

| 场景 | 默认策略 | 可选策略 |
|------|----------|----------|
| **全新安装** | 跳过（Skip） | 强制覆盖（Force） |
| **更新命令** | 备份后覆盖（Backup） | 保留（Keep）、交互式（Ask） |
| **配置文件** | 智能合并（Merge） | 覆盖（Overwrite）、保留（Keep） |
| **模板文件** | 备份后覆盖（Backup） | 保留（Keep） |

---

## 冲突检测机制

### 1. 冲突类型分类

#### 1.1 按文件类型分类

```
系统文件
├── 命令文件（.claude/commands/*.md）
├── 模板文件（.claude/templates/*）
├── 配置文件（.claude/*.json）
└── 元数据文件（.claude/command-install.json）

用户文件
├── 用户自定义命令
├── 用户修改的模板
├── 用户配置文件
└── 项目特定文件
```

#### 1.2 按冲突性质分类

| 类型 | 描述 | 严重程度 |
|------|------|----------|
| **同名冲突** | 新文件与现有文件同名 | 高 |
| **版本冲突** | 同一命令的不同版本 | 中 |
| **依赖冲突** | 不同命令依赖同一资源 | 中 |
| **格式冲突** | 文件格式不兼容 | 低 |
| **权限冲突** | 无法写入目标文件 | 高 |

### 2. 冲突检测方法

#### 2.1 文件存在检查

**实现方式**：
```javascript
// 伪代码示例
function detectConflict(targetPath, newContent) {
  if (!fs.existsSync(targetPath)) {
    return { conflict: false };
  }

  // 文件存在，需要进一步分析
  return analyzeExistingFile(targetPath, newContent);
}
```

**优点**：
- 简单快速
- 无需读取文件内容

**缺点**：
- 无法判断内容是否真的冲突
- 可能误报（相同内容也视为冲突）

#### 2.2 内容哈希比较

**推荐的哈希算法**：

| 算法 | 安全性 | 性能 | 推荐度 |
|------|--------|------|--------|
| **SHA-256** | 高 | 中 | ✅ 推荐 |
| MD5 | 低 | 高 | ⚠️ 不推荐（存在碰撞攻击） |
| BLAKE3 | 高 | 高 | ✅ 未来可选 |

**实现方式**：
```javascript
const crypto = require('crypto');
const fs = require('fs');

function computeFileHash(filePath) {
  const content = fs.readFileSync(filePath);
  return crypto.createHash('sha256').update(content).digest('hex');
}

function detectConflictByHash(targetPath, newContent) {
  if (!fs.existsSync(targetPath)) {
    return { conflict: false };
  }

  const existingHash = computeFileHash(targetPath);
  const newHash = crypto.createHash('sha256').update(newContent).digest('hex');

  if (existingHash === newHash) {
    return { conflict: false, reason: 'content-identical' };
  }

  return { conflict: true, reason: 'content-differs' };
}
```

**优点**：
- 准确判断内容是否相同
- 快速比较大量文件

**缺点**：
- 需要读取和哈希整个文件
- 无法显示具体差异

**参考**：Gradle 依赖验证使用校验和来断言完整性

#### 2.3 时间戳比较

**实现方式**：
```javascript
function detectConflictByTimestamp(targetPath, newContent) {
  if (!fs.existsSync(targetPath)) {
    return { conflict: false };
  }

  const stats = fs.statSync(targetPath);
  const existingMtime = stats.mtime;
  const installRecord = getInstallRecord(targetPath);

  if (!installRecord) {
    // 没有安装记录，可能是用户手动创建的文件
    return { conflict: true, reason: 'untracked-file' };
  }

  const installTime = new Date(installRecord.installedAt);

  if (existingMtime > installTime) {
    // 文件在安装后被修改过
    return { conflict: true, reason: 'user-modified' };
  }

  return { conflict: true, reason: 'stale-version' };
}
```

**优点**：
- 可以识别用户修改
- 相对快速

**缺点**：
- 时间戳可能不准确（时钟漂移）
- 无法量化修改程度

#### 2.4 内容差异分析

**实现方式**：
```javascript
const diff = require('diff');

function detectConflictByDiff(targetPath, newContent) {
  if (!fs.existsSync(targetPath)) {
    return { conflict: false };
  }

  const existingContent = fs.readFileSync(targetPath, 'utf8');
  const differences = diff.diffLines(existingContent, newContent);

  const addedLines = differences
    .filter(d => d.added)
    .reduce((sum, d) => sum + d.count, 0);

  const removedLines = differences
    .filter(d => d.removed)
    .reduce((sum, d) => sum + d.count, 0);

  const changePercent = (addedLines + removedLines) /
    existingContent.split('\n').length * 100;

  return {
    conflict: true,
    reason: 'content-differs',
    changes: { addedLines, removedLines, changePercent }
  };
}
```

**优点**：
- 提供详细的差异信息
- 可以量化修改程度

**缺点**：
- 计算开销较大
- 对于大文件可能较慢

### 3. 综合检测策略

**推荐的检测流程**：

```
1. 快速检查：文件是否存在？
   ├─ 不存在 → 无冲突
   └─ 存在 → 继续

2. 哈希比较：内容是否相同？
   ├─ 相同 → 无冲突（可跳过）
   └─ 不同 → 继续

3. 来源识别：文件来源是什么？
   ├─ 本命令安装 → 版本冲突
   ├─ 其他命令安装 → 依赖冲突
   └─ 用户文件 → 用户修改冲突

4. 修改分析：修改程度如何？
   ├─ 轻微修改（< 10%）→ 可能自动合并
   ├─ 中度修改（10-50%）→ 需要用户决策
   └─ 重大修改（> 50%）→ 建议保留用户版本
```

---

## 冲突解决策略对比

### 策略 A：覆盖（Overwrite）

**定义**：直接用新文件覆盖现有文件，不保留备份。

**优点**：
- ✅ 实现简单
- ✅ 确保版本一致性
- ✅ 无需额外存储空间

**缺点**：
- ❌ 永久丢失用户修改
- ❌ 无法回滚
- ❌ 可能破坏用户配置

**适用场景**：
- 用户明确要求强制更新（`--force`）
- 文件内容完全相同（实际无冲突）
- 系统临时文件

**成熟工具示例**：
- **pip**：无条件覆盖文件（已知问题）
- **npm**：使用 `--force` 标志时覆盖

**风险等级**：🔴 高风险

---

### 策略 B：跳过（Skip）

**定义**：跳过冲突文件，继续安装其他文件。

**优点**：
- ✅ 完全安全，不会丢失数据
- ✅ 用户可控制后续操作
- ✅ 适用于批量安装

**缺点**：
- ❌ 可能导致安装不完整
- ❌ 用户需要手动处理冲突
- ❌ 可能造成版本不一致

**适用场景**：
- 默认安装策略
- 用户手动修改过的文件
- 批量安装中的非关键文件

**成熟工具示例**：
- **Magentrix CLI**：提供 `skip` 选项
- **npm**：使用 `--ignore-scripts` 跳过某些操作

**风险等级**：🟢 低风险

---

### 策略 C：备份后覆盖（Backup & Overwrite）

**定义**：先备份现有文件，然后用新文件覆盖。

**实现方式**：
```javascript
function backupAndOverwrite(filePath, newContent) {
  // 生成备份文件名
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const backupPath = `${filePath}.backup.${timestamp}`;

  // 备份原文件
  fs.copyFileSync(filePath, backupPath);

  // 写入新文件
  fs.writeFileSync(filePath, newContent);

  // 记录备份位置
  recordBackup(filePath, backupPath);

  return { backupPath };
}
```

**优点**：
- ✅ 可回滚
- ✅ 保留用户数据
- ✅ 安装完整

**缺点**：
- ❌ 需要管理备份文件
- ❌ 占用额外存储空间
- ❌ 备份文件可能累积

**备份管理策略**：
- 限制备份数量（如保留最近 3 个）
- 自动清理过期备份（如 30 天后）
- 提供清理命令

**适用场景**：
- 命令更新
- 配置文件更新
- 模板文件更新

**成熟工具示例**：
- **Homebrew**：使用 `--dry-run` 预览，然后备份
- **apt**：保留旧配置文件为 `.dpkg-old` 或 `.dpkg-dist`

**风险等级**：🟡 中风险

---

### 策略 D：交互式询问（Interactive）

**定义**：在遇到冲突时询问用户如何处理。

**优点**：
- ✅ 用户完全控制
- ✅ 可以根据具体情况决策
- ✅ 避免意外数据丢失

**缺点**：
- ❌ 无法自动化
- ❌ 用户体验可能较慢
- ❌ 不适合批量操作

**交互设计示例**：
```
⚠️  检测到文件冲突：

文件：.claude/commands/wiki-generate.md
- 现有版本：1.0.0（2024-12-15 安装）
- 新版本：1.1.0
- 文件已修改：是（15 行变更）

请选择操作：
[1] 跳过（保留现有文件）
[2] 备份后更新（创建备份，然后安装新版本）
[3] 强制覆盖（不备份，直接覆盖）
[4] 查看差异
[5] 全部应用相同操作

您的选择 [1-5]:
```

**适用场景**：
- 单个命令安装/更新
- 重要配置文件
- 用户主动操作（非脚本）

**成熟工具示例**：
- **apt**：配置文件冲突时弹出交互式提示
- **Magentrix CLI**：提供 `manual` 冲突解决选项

**风险等级**：🟢 低风险（用户控制）

---

### 策略 E：智能合并（Smart Merge）

**定义**：尝试合并两个文件的内容，保留双方修改。

**实现方式**：
```javascript
function smartMerge(existingPath, newContent) {
  const existingContent = fs.readFileSync(existingPath, 'utf8');

  // 识别文件类型和结构
  const fileType = detectFileType(existingPath);

  if (fileType === 'json') {
    // JSON 配置文件：深度合并
    return mergeJson(existingContent, newContent);
  } else if (fileType === 'markdown') {
    // Markdown 命令文件：区域合并
    return mergeMarkdownRegions(existingContent, newContent);
  } else {
    // 其他文件：三向合并
    return threeWayMerge(existingContent, newContent);
  }
}
```

**优点**：
- ✅ 最大化保留用户修改
- ✅ 自动化处理
- ✅ 适用于配置文件

**缺点**：
- ❌ 实现复杂
- ❌ 可能产生冲突标记
- ❌ 需要验证合并结果

**合并策略示例**：

#### JSON 配置合并
```javascript
function mergeJson(existing, new) {
  const existingObj = JSON.parse(existing);
  const newObj = JSON.parse(new);

  // 深度合并，保留用户自定义字段
  const merged = deepMerge(existingObj, newObj);

  return JSON.stringify(merged, null, 2);
}
```

#### Markdown 区域合并
```javascript
function mergeMarkdownRegions(existing, new) {
  // 识别特殊区域
  const userRegion = extractRegion(existing, '用户自定义区域');
  const newContent = replaceRegion(new, '用户自定义区域', userRegion);

  return newContent;
}
```

**适用场景**：
- JSON 配置文件
- 包含用户区域的模板文件
- 简单的文本文件

**风险等级**：🟡 中风险（需要验证）

---

## 成熟工具最佳实践

### 1. npm（Node Package Manager）

**冲突处理特点**：
- **默认行为**：覆盖文件
- **控制标志**：`--force`, `--ignore-scripts`
- **依赖冲突**：使用 `--legacy-peer-deps` 绕过对等依赖冲突

**最佳实践**：
```bash
# 强制覆盖
npm install --force

# 忽略依赖冲突
npm install --legacy-peer-deps

# 干运行（预览）
npm install --dry-run
```

**教训**：
- ⚠️ 无条件覆盖可能导致数据丢失
- ✅ 提供多种标志让用户控制行为
- ✅ 使用 `--dry-run` 预览操作

**参考资料**：
- [StackOverflow: Fix upstream dependency conflict](https://stackoverflow.com/questions/64936044/fix-the-upstream-dependency-conflict-installing-npm-packages)

---

### 2. pip（Python Package Manager）

**冲突处理特点**：
- **已知问题**：无条件覆盖文件
- **依赖冲突**：提供 `--ignore-conflicts` 选项
- **模块冲突**：不同包可能包含同名模块

**最佳实践**：
```bash
# 覆盖冲突的依赖
pip install --ignore-conflicts

# 使用虚拟环境隔离冲突
python -m venv venv
source venv/bin/activate
pip install package
```

**教训**：
- ⚠️ 无条件覆盖是长期存在的问题
- ✅ 虚拟环境是解决包冲突的更好方案
- ✅ 提供冲突覆盖选项，但默认行为应保守

**参考资料**：
- [pip overwrites existing files unconditionally (GitHub Issue)](https://github.com/pypa/pip/issues/4625)
- [Install packages with conflicting dependencies](https://pip.pypa.io/en/latest/ux-research-design/research-results/override-conflicting-dependencies/)

---

### 3. apt（Debian/Ubuntu Package Manager）

**冲突处理特点**：
- **配置文件（conffile）**：特殊处理
- **交互式提示**：更新时询问用户
- **非交互模式**：通过 `dpkg` 选项配置

**配置文件处理**：
```bash
# 保留现有配置（默认）
Y, "yes, install the package maintainer's version"

# 保留当前配置
N, "no, keep the currently-installed version"

# 查看差异
D, "show the differences between the versions"

# 启动 shell
Z, "start a shell to examine the situation"
```

**非交互式配置**：
```bash
# 自动处理配置冲突（保留旧配置）
sudo DEBIAN_FRONTEND=noninteractive \
  apt-get -o Dpkg::Options::="--force-confdef" \
  -o Dpkg::Options::="--force-confold" \
  upgrade

# 自动处理配置冲突（安装新配置）
sudo DEBIAN_FRONTEND=noninteractive \
  apt-get -o Dpkg::Options::="--force-confdef" \
  -o Dpkg::Options::="--force-confnew" \
  upgrade
```

**配置文件后缀**：
- `.dpkg-old`：旧配置文件
- `.dpkg-dist`：发行版默认配置
- `.dpkg-new`：新配置文件（未安装）

**教训**：
- ✅ 配置文件需要特殊处理
- ✅ 提供详细的选项和交互
- ✅ 支持非交互模式（自动化）
- ✅ 保留旧版本文件用于恢复

**参考资料**：
- [AskUbuntu: How to resolve package conflict](https://askubuntu.com/questions/973988/how-to-resolve-package-conflict-with-apt-get)
- [apt.conf Configuration Reference](https://manpages.ubuntu.com/manpages/xenial/man5/apt.conf.5.html)

---

### 4. Homebrew（macOS Package Manager）

**冲突处理特点**：
- **链接冲突**：`brew link --overwrite`
- **预览模式**：`--dry-run`
- **备份策略**：使用 Brewfile

**最佳实践**：
```bash
# 预览将被覆盖的文件
brew link --overwrite formula_name --dry-run

# 强制覆盖链接
brew link --overwrite formula_name

# 备份所有已安装的包
brew bundle dump --file=~/Brewfile

# 从 Brewfile 恢复
brew bundle --file=~/Brewfile
```

**备份策略**：
1. **Brewfile**：记录所有已安装的包
2. **Time Machine**：macOS 系统备份
3. **仓库克隆**：克隆 Homebrew 仓库并同步

**教训**：
- ✅ 提供预览功能让用户了解影响
- ✅ 提供备份和恢复机制
- ✅ 使用声明式配置（Brewfile）
- ✅ Git reset 用于解决仓库冲突

**参考资料**：
- [Homebrew Common Issues Documentation](https://docs.brew.sh/Common-Issues)
- [Force overwrite application (GitHub Issue)](https://github.com/Homebrew/homebrew-cask/issues/46411)

---

### 5. Magentrix CLI

**冲突处理特点**：
- 提供明确的冲突解决策略
- 支持批量操作

**可用策略**：
- `overwrite`：覆盖现有文件
- `skip`：跳过冲突文件
- `manual`：手动解决冲突

**参考资料**：
- [Magentrix CLI Package](https://www.npmjs.com/package/@magentrix-corp/magentrix-cli)

---

### 6. Git（版本控制系统）

虽然不是包管理器，但 Git 的冲突处理机制非常成熟：

**合并策略**：
- `git merge`：三向合并
- `git rebase`：变基合并
- `git stash`：暂存修改

**冲突解决**：
- 交互式解决（`git mergetool`）
- 选择一方（`git checkout --ours` / `--theirs`）
- 手动编辑

**教训**：
- ✅ 提供多种合并策略
- ✅ 可视化差异
- ✅ 支持部分提交（`git add -p`）

---

## 推荐策略

### 场景 1：全新安装

**场景描述**：
- 用户第一次安装命令
- `.claude/commands/` 目录中不存在同名文件

**推荐策略**：**直接安装**

**理由**：
- 无冲突，无需特殊处理
- 用户期望命令立即可用

**实现**：
```javascript
if (!fs.existsSync(targetPath)) {
  fs.writeFileSync(targetPath, newContent);
  return { success: true, action: 'installed' };
}
```

**特殊情况**：用户手动创建了同名文件

**处理**：
```javascript
if (fs.existsSync(targetPath)) {
  const hash = computeFileHash(targetPath);
  const newHash = computeHash(newContent);

  if (hash === newHash) {
    // 内容相同，跳过
    return { success: true, action: 'skipped', reason: 'identical' };
  }

  // 内容不同，按冲突处理
  return handleConflict(targetPath, newContent, options);
}
```

---

### 场景 2：更新已安装的命令

**场景描述**：
- 命令已存在
- 检测到新版本
- 用户可能手动修改过文件

**推荐策略**：**备份后覆盖（默认）**

**理由**：
- 保留用户修改（可恢复）
- 确保更新到最新版本
- 提供回滚能力

**实现**：
```javascript
function updateCommand(commandName, newContent, options) {
  const targetPath = getCommandPath(commandName);

  if (!fs.existsSync(targetPath)) {
    return installNewCommand(commandName, newContent);
  }

  // 检查是否被修改
  const record = getInstallRecord(commandName);
  const stats = fs.statSync(targetPath);
  const isModified = stats.mtime > new Date(record.installedAt);

  if (isModified && !options.force) {
    // 文件已被修改，使用默认策略
    if (options.strategy === 'backup') {
      return backupAndOverwrite(targetPath, newContent);
    } else if (options.strategy === 'skip') {
      return { action: 'skipped', reason: 'user-modified' };
    } else if (options.strategy === 'ask') {
      return askUser(targetPath, newContent, 'update');
    }
  }

  // 未修改或强制更新
  return backupAndOverwrite(targetPath, newContent);
}
```

**命令行参数**：
```bash
# 默认：备份后更新
/command.install update wiki-generate

# 强制覆盖（不备份）
/command.install update wiki-generate --force

# 跳过更新
/command.install update wiki-generate --skip

# 交互式询问
/command.install update wiki-generate --ask
```

---

### 场景 3：配置文件冲突

**场景描述**：
- 安装或更新包含配置文件的命令
- 用户已自定义配置

**推荐策略**：**智能合并（JSON）/ 保留（其他）**

**理由**：
- 配置文件通常包含用户自定义
- 智能合并可以保留用户设置
- 避免覆盖用户配置

**实现 - JSON 配置**：
```javascript
function handleConfigConflict(configPath, newConfig) {
  const existing = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  const newConfigObj = JSON.parse(newConfig);

  // 深度合并，新配置的默认值 + 用户自定义
  const merged = deepMerge(newConfigObj, existing);

  // 添加合并标记
  const mergedWithMetadata = {
    ...merged,
    _merged: true,
    _mergedAt: new Date().toISOString(),
    _mergedFrom: ['existing', 'new']
  };

  fs.writeFileSync(
    configPath,
    JSON.stringify(mergedWithMetadata, null, 2)
  );

  return { action: 'merged', changes: detectMergeChanges(existing, merged) };
}
```

**实现 - 其他配置文件**：
```javascript
function handleGenericConfigConflict(configPath, newContent) {
  // 对于非 JSON 配置，默认保留
  if (!options.force) {
    return {
      action: 'skipped',
      reason: 'config-file-protected',
      message: '配置文件已保留，请手动合并更改'
    };
  }

  // 用户明确要求覆盖
  return backupAndOverwrite(configPath, newContent);
}
```

**命令行示例**：
```bash
# 默认：智能合并 JSON，保留其他配置
/command.install update my-command

# 强制覆盖配置
/command.install update my-command --force-config

# 保留所有配置（不合并）
/command.install update my-command --keep-config
```

---

### 场景 4：模板文件冲突

**场景描述**：
- 命令包含模板文件
- 用户可能自定义了模板

**推荐策略**：**备份后覆盖**

**理由**：
- 模板通常是命令的一部分
- 更新通常包含改进
- 用户可以恢复备份

**实现**：
```javascript
function handleTemplateConflict(templatePath, newContent, options) {
  const strategy = options.templateStrategy || 'backup';

  switch (strategy) {
    case 'backup':
      return backupAndOverwrite(templatePath, newContent);
    case 'keep':
      return { action: 'skipped', reason: 'user-template-kept' };
    case 'overwrite':
      return overwriteFile(templatePath, newContent);
    default:
      return backupAndOverwrite(templatePath, newContent);
  }
}
```

**特殊考虑**：
- 如果模板文件包含用户自定义区域，使用智能合并
- 识别特殊标记（如 `<!-- USER CUSTOM SECTION -->`）

---

### 场景 5：批量安装

**场景描述**：
- 一次性安装多个命令
- 可能存在多个冲突

**推荐策略**：**统一策略 + 摘要报告**

**理由**：
- 不希望每个冲突都询问用户
- 提供完整的操作摘要
- 允许用户回滚

**实现**：
```javascript
async function batchInstall(commands, options) {
  const results = [];
  const strategy = options.strategy || 'skip';

  for (const cmd of commands) {
    try {
      const result = await installCommand(cmd, {
        ...options,
        strategy,
        interactive: false // 批量模式不交互
      });
      results.push(result);
    } catch (error) {
      results.push({
        command: cmd.name,
        status: 'failed',
        error: error.message
      });
    }
  }

  // 生成摘要报告
  return generateSummaryReport(results);
}
```

**报告示例**：
```
批量安装完成

总计：10 个命令
成功：7 个
跳过：2 个（文件冲突）
失败：1 个

跳过的命令：
- wiki-generate（文件已存在）
- code-review（文件已存在）

使用 --force 强制覆盖，或手动处理冲突文件。
```

---

### 场景 6：依赖冲突

**场景描述**：
- 两个命令依赖同一个模板文件
- 模板文件版本不同

**推荐策略**：**版本仲裁 + 通知**

**理由**：
- 确定唯一的版本
- 通知用户潜在问题
- 提供解决方案

**实现**：
```javascript
function resolveDependencyConflict(conflicts) {
  const resolution = [];

  for (const conflict of conflicts) {
    const { file, commands } = conflict;
    const versions = commands.map(c => c.version);

    // 选择最新版本
    const latestVersion = Math.max(...versions);
    const winner = commands.find(c => c.version === latestVersion);

    resolution.push({
      file,
      selected: winner.name,
      version: latestVersion,
      affected: commands.filter(c => c !== winner),
      action: 'installed-latest'
    });
  }

  return resolution;
}
```

**通知示例**：
```
⚠️  依赖冲突已解决：

模板：.claude/templates/common.md
- 使用版本：1.2.0（来自 wiki-generate）
- 影响命令：code-review（需要 1.0.0）

建议：检查 code-review 是否与 common.md v1.2.0 兼容。
```

---

## 决策树设计

### 主决策树

```
开始检测文件冲突
│
├─ 文件不存在？
│  └─ 是 → 直接安装
│
├─ 文件存在
│  │
│  ├─ 内容相同？
│  │  └─ 是 → 跳过（无操作）
│  │
│  └─ 内容不同
│     │
│     ├─ 文件类型？
│     │  │
│     │  ├─ 命令文件
│     │  │  │
│     │  │  ├─ 用户修改？
│     │  │  │  ├─ 是 → 应用命令策略（ask/backup/skip）
│     │  │  │  └─ 否 → 备份后覆盖
│     │  │  │
│     │  │  └─ 操作：备份 → 覆盖 → 记录
│     │  │
│     │  ├─ 配置文件（JSON）
│     │  │  │
│     │  │  ├─ 可合并？
│     │  │  │  ├─ 是 → 智能合并
│     │  │  │  └─ 否 → 应用配置策略
│     │  │  │
│     │  │  └─ 操作：合并 → 验证 → 记录
│     │  │
│     │  ├─ 模板文件
│     │  │  │
│     │  │  ├─ 有自定义区域？
│     │  │  │  ├─ 是 → 区域合并
│     │  │  │  └─ 否 → 备份后覆盖
│     │  │  │
│     │  │  └─ 操作：备份 → 合并/覆盖 → 记录
│     │  │
│     │  └─ 其他文件
│     │     │
│     │     └─ 应用通用策略（skip/ask）
│     │
│     └─ 用户策略？
│        ├─ --force → 无条件覆盖
│        ├─ --skip → 跳过所有冲突
│        ├─ --backup → 备份后覆盖
│        └─ --ask → 交互式询问
│
└─ 生成冲突报告
```

### 交互式决策树（`--ask` 模式）

```
遇到冲突
│
├─ 显示冲突信息
│  ├─ 文件路径
│  ├─ 冲突类型
│  ├─ 现有版本信息
│  └─ 新版本信息
│
├─ 询问用户
│  │
│  ├─ [1] 跳过此文件
│  ├─ [2] 备份后覆盖
│  ├─ [3] 强制覆盖
│  ├─ [4] 查看差异
│  ├─ [5] 对所有冲突应用相同操作
│  └─ [6] 取消安装
│
└─ 执行用户选择
   └─ 记录决策（用于批量操作）
```

---

## 配置设计

### 全局配置文件：`.claude/command-install.json`

```json
{
  "version": "1.0.0",
  "settings": {
    // 默认冲突策略
    "conflict_strategy": {
      "command": "backup",
      "config": "merge",
      "template": "backup",
      "other": "skip"
    },

    // 备份设置
    "backup": {
      "enabled": true,
      "directory": ".claude/backups",
      "max_age_days": 30,
      "max_count": 3,
      "compression": false
    },

    // 交互设置
    "interactive": {
      "enabled": true,
      "batch_mode": "skip",
      "timeout_seconds": 300
    },

    // 验证设置
    "verification": {
      "checksum_algorithm": "sha256",
      "verify_after_install": true,
      "run_tests": false
    }
  }
}
```

### 命令级配置

每个命令的元数据中可以指定冲突策略：

```markdown
---
name: wiki-generate
version: 1.0.0
conflict_resolution:
  strategy: backup
  merge_patterns:
    - pattern: "<!-- USER_CUSTOM -->"
      action: preserve
---
```

### 命令行参数

```bash
# 全局策略
/command.install install <source> --strategy=backup
/command.install install <source> --strategy=skip
/command.install install <source> --strategy=ask

# 强制覆盖
/command.install install <source> --force

# 文件类型特定策略
/command.install install <source> --command-strategy=backup
/command.install install <source> --config-strategy=merge
/command.install install <source> --template-strategy=keep

# 备份控制
/command.install install <source> --backup
/command.install install <source> --no-backup
/command.install install <source> --backup-dir=/path/to/backups

# 交互控制
/command.install install <source> --ask
/command.install install <source> --yes
/command.install install <source> --batch
```

### 环境变量

```bash
# 默认冲突策略
export COMMAND_INSTALL_STRATEGY=backup

# 备份目录
export COMMAND_INSTALL_BACKUP_DIR=.claude/backups

# 非交互模式
export COMMAND_INSTALL_NON_INTERACTIVE=1

# 日志级别
export COMMAND_INSTALL_LOG_LEVEL=debug
```

### 优先级顺序

```
1. 命令行参数（最高优先级）
2. 命令元数据配置
3. 全局配置文件
4. 环境变量
5. 默认值（最低优先级）
```

---

## 用户体验设计

### 1. 清晰的错误消息

#### 消息模板

**模板 1：简单冲突**
```
⚠️  文件冲突

文件：.claude/commands/wiki-generate.md
原因：文件已存在

解决方案：
• 使用 --force 强制覆盖
• 使用 --skip 跳过此文件
• 使用 --backup 备份后覆盖

详情：/command.install info wiki-generate
```

**模板 2：用户修改检测**
```
⚠️  检测到用户修改

文件：.claude/commands/wiki-generate.md
最后安装：2024-12-15 10:30:00
最后修改：2024-12-28 14:22:00
变更统计：+15 行，-8 行

建议：
• 使用 --backup 备份后更新（保留您的修改）
• 使用 --skip 保留当前版本
• 使用 --force 强制覆盖（丢失修改）
• 使用 --diff 查看详细差异
```

**模板 3：配置文件冲突**
```
⚠️  配置文件冲突

文件：.claude/wiki-config.json
您的配置包含 3 个自定义设置

操作：
• 智能合并：保留您的自定义设置 + 新默认值 [默认]
• 保留现有：跳过此配置文件
• 查看差异：显示具体变更
• 强制覆盖：使用新配置（丢失自定义）
```

**模板 4：批量操作摘要**
```
批量安装完成

✅ 成功：7 个命令
⏭️  跳过：2 个命令（文件冲突）
❌ 失败：1 个命令

跳过的文件：
• .claude/commands/wiki-generate.md（已修改）
• .claude/templates/common.md（用户自定义）

下一步：
1. 检查跳过的文件是否需要更新
2. 使用 --force 重新安装跳过的命令
3. 或手动合并更改

详细报告：.claude/install-report-20250103-103022.json
```

---

### 2. 交互式提示设计

#### 提示符设计

```
⚠️  文件冲突：.claude/commands/wiki-generate.md

现有版本：1.0.0（2024-12-15 安装）
新版本：1.1.0
文件状态：已修改（15 行变更）

版本差异：
  • 新增：2 个功能
  • 改进：3 个功能
  • 修复：1 个 bug

[1] 跳过（保留现有版本）
[2] 备份后更新（推荐）
[3] 强制覆盖（不备份）
[4] 查看详细差异
[5] 对所有冲突应用此操作
[6] 取消安装

选择 [1-6，默认 2]:
```

#### 差异查看器

```
差异：.claude/commands/wiki-generate.md

--- 现有版本 (1.0.0)
+++ 新版本 (1.1.0)

@@ -15,7 +15,9 @@
 功能：
-- 生成概览文档
+- 生成概览文档（新增图片支持）
+- 生成架构图（新增）
 - 生成模块文档

@@ -42,6 +44,8 @@
 配置：
 - output_dir: docs
+- image_format: svg
+- diagram_detail: medium

按 Q 返回，按 S 应用'跳过'，按 O 应用'覆盖':
```

---

### 3. 进度指示

#### 安装进度

```
正在安装：wiki-generator...

[████████████████████░░░░] 80% (4/5)

✓ 命令文件：wiki-generate.md
✓ 模板文件：overview.md.template
✓ 模板文件：architecture.md.template
✓ 配置文件：wiki-config.json
⏳ 模板文件：module.md.template... (冲突)
```

#### 冲突处理进度

```
处理冲突：模块模板文件

[1/3] 分析文件差异... ✓
[2/3] 检测用户修改区域... ✓
[3/3] 智能合并... ✓

结果：
  • 保留：2 个用户自定义区域
  • 更新：5 个模板区域
  • 新增：3 个功能区域
```

---

### 4. 颜色和格式建议

虽然 Claude Code 不一定支持颜色，但可以建议终端输出使用以下格式：

```
✅ 成功：绿色
⚠️  警告：黄色
❌ 错误：红色
ℹ️  信息：蓝色
⏭️  跳过：灰色
⏳ 进行中：青色
```

---

### 5. 操作反馈

#### 操作前确认

```
即将执行以下操作：

安装命令：wiki-generator (v1.1.0)

将创建/修改以下文件：
• .claude/commands/wiki-generate.md（新建）
• .claude/templates/overview.md.template（新建）
• .claude/templates/architecture.md.template（新建）
• .claude/wiki-config.json（合并）

冲突处理：
• .claude/wiki-config.json → 智能合并（保留现有配置）

备份位置：
• .claude/backups/wiki-config.json.backup-20250103-103022

确认？[Y/n]:
```

#### 操作后摘要

```
安装完成！

命令：wiki-generator v1.1.0
状态：✅ 成功

文件操作：
• 新建：3 个文件
• 更新：1 个文件（合并）
• 跳过：0 个文件
• 备份：1 个文件

位置：
• 命令：.claude/commands/wiki-generate.md
• 配置：.claude/wiki-config.json

下一步：
1. 检查配置文件：.claude/wiki-config.json
2. 运行命令：/wiki:overview
3. 查看文档：docs/00-README.md

回滚：
/command.install rollback wiki-generator --backup=20250103-103022
```

---

## 测试场景

### 单元测试场景

#### 测试 1：无冲突安装

**输入**：
- 目标文件不存在
- 新内容有效

**预期输出**：
- 文件创建成功
- 返回 `{ action: 'installed' }`

**测试代码**：
```javascript
test('安装不存在的命令文件', () => {
  const result = installCommand('test-command.md', content);
  expect(result.action).toBe('installed');
  expect(fs.existsSync('.claude/commands/test-command.md')).toBe(true);
});
```

---

#### 测试 2：内容相同

**输入**：
- 目标文件存在
- 内容与新内容完全相同

**预期输出**：
- 跳过安装
- 返回 `{ action: 'skipped', reason: 'identical' }`

**测试代码**：
```javascript
test('跳过内容相同的文件', () => {
  fs.writeFileSync('.claude/commands/test.md', content);
  const result = installCommand('test.md', content);
  expect(result.action).toBe('skipped');
  expect(result.reason).toBe('identical');
});
```

---

#### 测试 3：哈希冲突检测

**输入**：
- 目标文件存在
- 计算文件哈希

**预期输出**：
- 正确识别内容是否相同

**测试代码**：
```javascript
test('正确检测内容差异', () => {
  fs.writeFileSync('.claude/commands/test.md', 'old content');
  const result = detectConflictByHash('.claude/commands/test.md', 'new content');
  expect(result.conflict).toBe(true);
  expect(result.reason).toBe('content-differs');
});
```

---

#### 测试 4：备份创建

**输入**：
- 文件存在
- 策略为 `backup`

**预期输出**：
- 备份文件创建
- 主文件更新
- 返回备份路径

**测试代码**：
```javascript
test('备份后覆盖文件', () => {
  fs.writeFileSync('.claude/commands/test.md', 'old content');
  const result = backupAndOverwrite('.claude/commands/test.md', 'new content');

  expect(fs.existsSync('.claude/commands/test.md.backup.')).toBe(true);
  expect(fs.readFileSync('.claude/commands/test.md', 'utf8')).toBe('new content');
  expect(result.backupPath).toMatch(/backup.*\.md$/);
});
```

---

#### 测试 5：智能合并（JSON）

**输入**：
- 现有配置：`{ a: 1, b: 2 }`
- 新配置：`{ a: 10, c: 3 }`

**预期输出**：
- 合并结果：`{ a: 1, b: 2, c: 3 }`（保留用户 a:1）

**测试代码**：
```javascript
test('智能合并 JSON 配置', () => {
  const existing = JSON.stringify({ a: 1, b: 2 });
  const newConfig = JSON.stringify({ a: 10, c: 3 });
  const result = smartMergeJson(existing, newConfig);

  const merged = JSON.parse(result);
  expect(merged.a).toBe(1); // 保留用户值
  expect(merged.b).toBe(2);
  expect(merged.c).toBe(3);
});
```

---

### 集成测试场景

#### 测试 6：完整安装流程

**场景**：
- 从 Git 仓库安装命令
- 包含多个文件
- 部分文件冲突

**步骤**：
1. 准备测试仓库
2. 创建部分冲突文件
3. 执行安装
4. 验证结果

**预期**：
- 命令文件正确安装
- 冲突文件按策略处理
- 生成正确报告

---

#### 测试 7：更新流程

**场景**：
- 已安装命令 v1.0
- 用户修改了配置
- 更新到 v1.1

**步骤**：
1. 安装 v1.0
2. 修改配置文件
3. 更新到 v1.1

**预期**：
- 命令文件更新
- 配置文件合并
- 备份创建

---

#### 测试 8：批量安装冲突

**场景**：
- 批量安装 10 个命令
- 3 个命令有冲突

**步骤**：
1. 准备 10 个命令
2. 创建 3 个冲突文件
3. 执行批量安装

**预期**：
- 7 个成功安装
- 3 个冲突处理
- 完整摘要报告

---

### 边界测试场景

#### 测试 9：权限错误

**输入**：
- 目标目录只读

**预期**：
- 返回清晰的权限错误
- 不创建部分文件

---

#### 测试 10：磁盘空间不足

**输入**：
- 模拟磁盘满

**预期**：
- 检测空间不足
- 清理部分文件
- 返回错误信息

---

#### 测试 11：中断恢复

**输入**：
- 安装过程中中断（Ctrl+C）

**预期**：
- 清理临时文件
- 记录安装状态
- 支持恢复安装

---

### 性能测试场景

#### 测试 12：大量文件

**输入**：
- 安装包含 1000 个文件的命令

**预期**：
- 安装时间 < 30 秒
- 内存使用合理

---

#### 测试 13：大文件哈希

**输入**：
- 100MB 的文件

**预期**：
- 哈希计算时间 < 5 秒
- 内存峰值 < 200MB

---

### 安全测试场景

#### 测试 14：路径遍历攻击

**输入**：
- 恶意文件名：`../../etc/passwd`

**预期**：
- 拒绝安装
- 记录安全事件

---

#### 测试 15：恶意内容

**输入**：
- 命令文件包含恶意脚本

**预期**：
- 检测并警告
- 不执行脚本

---

## 实现建议

### 架构设计

```javascript
// 冲突处理器核心架构

class ConflictResolver {
  constructor(config) {
    this.config = config;
    this.detectors = [
      new ExistenceDetector(),
      new HashDetector(),
      new TimestampDetector(),
      new DiffDetector()
    ];
    this.resolvers = {
      command: new CommandConflictResolver(),
      config: new ConfigConflictResolver(),
      template: new TemplateConflictResolver(),
      other: new GenericConflictResolver()
    };
  }

  async detectConflict(targetPath, newContent) {
    for (const detector of this.detectors) {
      const result = await detector.detect(targetPath, newContent);
      if (result.conflict) {
        return result;
      }
    }
    return { conflict: false };
  }

  async resolveConflict(conflict, newContent, options) {
    const fileType = this.detectFileType(conflict.path);
    const resolver = this.resolvers[fileType] || this.resolvers.other;

    return resolver.resolve(conflict, newContent, options);
  }
}
```

---

### 错误处理

```javascript
class ConflictError extends Error {
  constructor(message, conflict, suggestions) {
    super(message);
    this.name = 'ConflictError';
    this.conflict = conflict;
    this.suggestions = suggestions;
  }
}

function handleError(error) {
  if (error instanceof ConflictError) {
    console.log(`⚠️  ${error.message}`);
    console.log('\n解决方案：');
    error.suggestions.forEach(s => console.log(`• ${s}`));
  } else {
    console.log(`❌ 错误：${error.message}`);
  }
}
```

---

### 日志记录

```javascript
class ConflictLogger {
  log(conflict, resolution) {
    const entry = {
      timestamp: new Date().toISOString(),
      conflict: {
        path: conflict.path,
        type: conflict.type,
        reason: conflict.reason
      },
      resolution: {
        action: resolution.action,
        backupPath: resolution.backupPath,
        user: resolution.user
      }
    };

    this.writeLog(entry);
  }

  generateReport() {
    // 生成冲突处理报告
  }
}
```

---

### 回滚机制

```javascript
class RollbackManager {
  constructor() {
    this.snapshots = [];
  }

  createSnapshot() {
    const snapshot = {
      id: generateId(),
      timestamp: new Date(),
      files: this.captureState()
    };
    this.snapshots.push(snapshot);
    return snapshot.id;
  }

  async rollback(snapshotId) {
    const snapshot = this.snapshots.find(s => s.id === snapshotId);
    if (!snapshot) {
      throw new Error('快照不存在');
    }

    for (const file of snapshot.files) {
      await fs.writeFile(file.path, file.content);
    }
  }
}
```

---

## 参考资料

### 研究来源

1. **npm 冲突处理**
   - [StackOverflow: Fix upstream dependency conflict](https://stackoverflow.com/questions/64936044/fix-the-upstream-dependency-conflict-installing-npm-packages)

2. **pip 文件覆盖问题**
   - [pip overwrites existing files unconditionally (GitHub Issue)](https://github.com/pypa/pip/issues/4625)
   - [Install packages with conflicting dependencies](https://pip.pypa.io/en/latest/ux-research-design/research-results/override-conflicting-dependencies/)

3. **apt 配置文件冲突**
   - [AskUbuntu: How to resolve package conflict](https://askubuntu.com/questions/973988/how-to-resolve-package-conflict-with-apt-get)
   - [apt.conf Configuration Reference](https://manpages.ubuntu.com/manpages/xenial/man5/apt.conf.5.html)

4. **Homebrew 冲突处理**
   - [Homebrew Common Issues Documentation](https://docs.brew.sh/Common-Issues)
   - [Force overwrite application (GitHub Issue)](https://github.com/Homebrew/homebrew-cask/issues/46411)

5. **Magentrix CLI 冲突策略**
   - [Magentrix CLI Package](https://www.npmjs.com/package/@magentrix-corp/magentrix-cli)

6. **文件哈希和验证**
   - [Hash-Based File Content Identification (ResearchGate)](https://www.researchgate.net/publication/236942036_Hash-Based_File_Content_Identification_Using_Distributed_Systems)
   - [Gradle Dependency Verification](https://docs.gradle.org/current/userguide/dependency_verification.html)

---

## 总结

本研究报告通过分析成熟包管理器的最佳实践，为 Claude Code 命令安装器提供了全面的文件冲突处理策略建议。

### 核心建议

1. **默认策略应保守**：使用"跳过"或"备份后覆盖"避免数据丢失
2. **提供用户控制**：通过命令行参数和配置文件让用户自定义策略
3. **智能分类处理**：不同文件类型使用不同策略（命令、配置、模板）
4. **透明操作**：清晰告知用户将要执行的操作和影响
5. **支持回滚**：备份机制确保可恢复
6. **完善验证**：使用 SHA-256 哈希验证文件完整性

### 实施优先级

**P0（必须）**：
- 基本冲突检测（存在性、哈希）
- 跳过和备份策略
- 清晰的错误消息

**P1（重要）**：
- 命令行参数支持
- 交互式询问
- JSON 配置智能合并

**P2（增强）**：
- 批量操作摘要
- 详细差异查看
- 回滚机制

**P3（未来）**：
- 图形化冲突解决界面
- 自动合并建议
- 云端备份集成

---

**文档版本**: 1.0.0
**最后更新**: 2025-01-03
**作者**: Repo Wiki Generator 项目团队
