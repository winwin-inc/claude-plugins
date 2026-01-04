# 文件冲突处理决策树

本文档提供可视化决策流程，帮助理解冲突处理的完整逻辑。

---

## 主决策流程图

```mermaid
flowchart TD
    Start([开始检测文件冲突]) --> CheckExists{文件是否存在?}

    CheckExists -->|否| Install[直接安装]
    Install --> End1([完成: action=installed])

    CheckExists -->|是| CheckHash{内容是否相同?<br/>SHA-256}

    CheckHash -->|是| Skip[跳过安装]
    Skip --> End2([完成: action=skipped<br/>reason=identical])

    CheckHash -->|否| IdentifyType[识别文件类型]

    IdentifyType --> FileType{文件类型?}

    FileType -->|命令文件<br/>.md| CommandPath
    FileType -->|配置文件<br/>.json| ConfigPath
    FileType -->|模板文件<br/>.template| TemplatePath
    FileType -->|其他文件| OtherPath

    %% 命令文件处理
    CommandPath --> CheckUserModified{用户是否修改?<br/>时间戳检查}

    CheckUserModified -->|否| BackupCommand[备份后覆盖]
    CheckUserModified -->|是| CheckCommandStrategy{用户策略?}

    CheckCommandStrategy -->|force| ForceCommand[强制覆盖]
    CheckCommandStrategy -->|backup| BackupCommand
    CheckCommandStrategy -->|skip| SkipCommand[跳过]
    CheckCommandStrategy -->|ask| AskCommand[交互式询问]

    BackupCommand --> End3([完成: action=backup])
    ForceCommand --> End4([完成: action=overwrite])
    SkipCommand --> End5([完成: action=skipped])
    AskCommand --> UserDecision1{用户选择}
    UserDecision1 -->|覆盖| ForceCommand
    UserDecision1 -->|备份| BackupCommand
    UserDecision1 -->|跳过| SkipCommand

    %% 配置文件处理
    ConfigPath --> IsJson{是否JSON格式?}

    IsJson -->|是| MergeConfig[智能合并配置]
    IsJson -->|否| CheckConfigStrategy{用户策略?}

    MergeConfig --> ValidateMerge{验证合并结果}
    ValidateMerge -->|成功| End6([完成: action=merged])
    ValidateMerge -->|失败| FallbackMerge[降级到备份策略]

    CheckConfigStrategy -->|force| ForceConfig[强制覆盖]
    CheckConfigStrategy -->|keep| KeepConfig[保留现有]
    CheckConfigStrategy -->|ask| AskConfig[交互式询问]

    FallbackMerge --> BackupCommand
    ForceConfig --> End7([完成: action=overwrite])
    KeepConfig --> End8([完成: action=skipped])
    AskConfig --> UserDecision2{用户选择}
    UserDecision2 -->|覆盖| ForceConfig
    UserDecision2 -->|保留| KeepConfig
    UserDecision2 -->|合并| MergeConfig

    %% 模板文件处理
    TemplatePath --> HasCustomRegion{是否有用户<br/>自定义区域?}

    HasCustomRegion -->|是| RegionMerge[区域合并]
    HasCustomRegion -->|否| CheckTemplateStrategy{用户策略?}

    RegionMerge --> End9([完成: action=region-merged])

    CheckTemplateStrategy -->|force| ForceTemplate[强制覆盖]
    CheckTemplateStrategy -->|backup| BackupTemplate[备份后覆盖]
    CheckTemplateStrategy -->|keep| KeepTemplate[保留现有]
    CheckTemplateStrategy -->|ask| AskTemplate[交互式询问]

    ForceTemplate --> End10([完成: action=overwrite])
    BackupTemplate --> End11([完成: action=backup])
    KeepTemplate --> End12([完成: action=skipped])
    AskTemplate --> UserDecision3{用户选择}
    UserDecision3 -->|覆盖| ForceTemplate
    UserDecision3 -->|备份| BackupTemplate
    UserDecision3 -->|保留| KeepTemplate

    %% 其他文件处理
    OtherPath --> CheckOtherStrategy{用户策略?}

    CheckOtherStrategy -->|force| ForceOther[强制覆盖]
    CheckOtherStrategy -->|默认 skip| SkipOther[跳过]
    CheckOtherStrategy -->|ask| AskOther[交互式询问]

    ForceOther --> End13([完成: action=overwrite])
    SkipOther --> End14([完成: action=skipped])
    AskOther --> UserDecision4{用户选择}
    UserDecision4 -->|覆盖| ForceOther
    UserDecision4 -->|跳过| SkipOther

    %% 样式定义
    classDef success fill:#90EE90,stroke:#333,stroke-width:2px
    classDef warning fill:#FFD700,stroke:#333,stroke-width:2px
    classDef danger fill:#FF6B6B,stroke:#333,stroke-width:2px
    classDef info fill:#87CEEB,stroke:#333,stroke-width:2px
    classDef decision fill:#FFE4B5,stroke:#333,stroke-width:2px

    class Install,End1,End2,End3,End4,End5,End6,End7,End8,End9,End10,End11,End12,End13,End14 success
    class Skip warning
    class ForceCommand,ForceConfig,ForceTemplate,ForceOther danger
    class BackupCommand,BackupTemplate,MergeConfig,RegionMerge info
    class CheckExists,CheckHash,FileType,CheckUserModified,CheckCommandStrategy,CheckConfigStrategy,IsJson,ValidateMerge,HasCustomRegion,CheckTemplateStrategy,CheckOtherStrategy,UserDecision1,UserDecision2,UserDecision3,UserDecision4 decision
```

---

## 策略选择流程图

```mermaid
flowchart LR
    Start([需要安装文件]) --> Strategy{选择策略}

    Strategy -->|新文件| Direct[直接安装]
    Strategy -->|可能冲突| Decision{如何处理?}

    Decision -->|安全优先| Safe[跳过 Skip]
    Decision -->|更新为主| Backup[备份后覆盖 Backup]
    Decision -->|用户控制| Interactive[交互式询问 Ask]
    Decision -->|强制执行| Force[强制覆盖 Force]

    Safe --> Result1{适用场景}
    Backup --> Result2{适用场景}
    Interactive --> Result3{适用场景}
    Force --> Result4{适用场景}

    Result1 --> R1[✅ 批量安装<br>✅ 默认策略<br>✅ 保护用户数据]
    Result2 --> R2[✅ 命令更新<br>✅ 模板更新<br>✅ 可回滚]
    Result3 --> R3[✅ 重要文件<br>✅ 单个操作<br>✅ 用户自定义]
    Result4 --> R4[⚠️ 明确要求<br>⚠️ 内容相同<br>⚠️ 系统文件]

    Direct --> End([完成])
    R1 --> End
    R2 --> End
    R3 --> End
    R4 --> End

    classDef safe fill:#90EE90,stroke:#333,stroke-width:2px
    classDef moderate fill:#FFD700,stroke:#333,stroke-width:2px
    classDef risky fill:#FF6B6B,stroke:#333,stroke-width:2px
    classDef result fill:#87CEEB,stroke:#333,stroke-width:2px

    class Direct,Safe,R1 safe
    class Backup,Interactive,R2,R3 moderate
    class Force,R4 risky
    class Result1,Result2,Result3,Result4,End result
```

---

## 文件类型处理策略矩阵

```mermaid
graph TD
    Types[文件类型分类] --> System[系统文件]
    Types --> User[用户文件]

    System --> Commands[命令文件<br/>.claude/commands/*.md]
    System --> Templates[模板文件<br/>.claude/templates/*]
    System --> Configs[配置文件<br/>.claude/*.json]

    User --> CustomCommands[用户自定义命令]
    User --> CustomTemplates[用户修改的模板]
    User --> CustomConfigs[用户配置文件]

    %% 系统文件策略
    Commands --> CmdStrategy[默认: backup<br>选项: force/skip/ask]
    Templates --> TmplStrategy[默认: backup<br>选项: force/skip/ask]
    Configs --> CfgStrategy[默认: merge<br>选项: force/keep/ask]

    %% 用户文件策略
    CustomCommands --> UserCmdStrategy[默认: ask<br>选项: force/skip]
    CustomTemplates --> UserTmplStrategy[默认: ask<br>选项: force/skip]
    CustomConfigs --> UserCfgStrategy[默认: keep<br>选项: merge/force]

    %% 样式
    classDef system fill:#87CEEB,stroke:#333,stroke-width:2px
    classDef user fill:#FFD700,stroke:#333,stroke-width:2px
    classDef strategy fill:#90EE90,stroke:#333,stroke-width:2px

    class System,Commands,Templates,Configs system
    class User,CustomCommands,CustomTemplates,CustomConfigs user
    class CmdStrategy,TmplStrategy,CfgStrategy,UserCmdStrategy,UserTmplStrategy,UserCfgStrategy strategy
```

---

## 冲突严重程度评估

```mermaid
flowchart TD
    Conflict([检测到冲突]) --> Analyze[分析冲突]

    Analyze --> WhatChanged{改变了什么?}

    WhatChanged -->|元数据| Low[低严重性<br>版本号、日期等]
    WhatChanged -->|注释| Low
    WhatChanged -->|格式| Low[空白、缩进等]

    WhatChanged -->|少量代码| Medium[中严重性<br>< 10% 变更]
    WhatChanged -->|配置项| Medium
    WhatChanged -->|依赖| Medium

    WhatChanged -->|核心逻辑| High[高严重性<br>> 50% 变更]
    WhatChanged -->|结构变化| High[文件移动、重命名]
    WhatChanged -->|不兼容| High[API 破坏性变更]

    %% 处理策略
    Low --> Auto[自动处理<br>默认策略]
    Medium --> Semi[半自动<br>需要确认]
    High --> Manual[手动处理<br>必须用户决策]

    %% 最终决策
    Auto --> Decision1{自动策略}
    Decision1 -->|内容相同| SkipAuto[跳过]
    Decision1 -->|内容不同| BackupAuto[备份后覆盖]

    Semi --> AskUser[询问用户<br>显示差异]
    Manual --> RequireUser[必须用户选择<br>强制交互]

    AskUser --> UserChoice1{用户选择}
    UserChoice1 -->|覆盖| BackupSemi[备份后覆盖]
    UserChoice1 -->|跳过| SkipSemi[跳过]

    RequireUser --> UserChoice2{用户选择}
    UserChoice2 -->|理解变更| MergeManual[合并或覆盖]
    UserChoice2 -->|不理解| KeepManual[保留现有]

    %% 样式
    classDef low fill:#90EE90,stroke:#333,stroke-width:2px
    classDef medium fill:#FFD700,stroke:#333,stroke-width:2px
    classDef high fill:#FF6B6B,stroke:#333,stroke-width:2px
    classDef action fill:#87CEEB,stroke:#333,stroke-width:2px

    class Low low
    class Medium medium
    class High high
    class Auto,Auto,Semi,Manual,Decision1,AskUser,RequireUser,UserChoice1,UserChoice2,SkipAuto,BackupAuto,BackupSemi,SkipSemi,MergeManual,KeepManual action
```

---

## 备份管理流程

```mermaid
flowchart TD
    BackupTrigger([触发备份]) --> CreateBackup[创建备份]

    CreateBackup --> GenName[生成备份文件名<br>原文件.backup.YYYYMMDD-HHMMSS]

    GenName --> CopyFile[复制原文件]

    CopyFile --> RecordBackup[记录备份信息<br>→ 安装记录]

    RecordBackup --> WriteNew[写入新文件]

    WriteNew --> CheckCount{备份数量<br>> 限制?}

    CheckCount -->|否| Done([备份完成])
    CheckCount -->|是| Cleanup[清理旧备份]

    Cleanup --> CheckAge{备份过期?<br>> max_age_days}

    CheckAge -->|是| DeleteOld[删除旧备份]
    CheckAge -->|否| DeleteExcess[删除额外备份<br>保留最新 max_count 个]

    DeleteOld --> Done
    DeleteExcess --> Done

    %% 样式
    classDef normal fill:#87CEEB,stroke:#333,stroke-width:2px
    classDef warning fill:#FFD700,stroke:#333,stroke-width:2px
    classDef success fill:#90EE90,stroke:#333,stroke-width:2px

    class BackupTrigger,CreateBackup,GenName,CopyFile,RecordBackup,WriteNew,Done normal
    class CheckCount,Cleanup,CheckAge warning
    class DeleteOld,DeleteExcess success
```

---

## 智能合并流程（JSON 配置）

```mermaid
flowchart TD
    Start([JSON 配置冲突]) --> Parse[解析 JSON]

    Parse --> Validate{是否有效 JSON?}

    Validate -->|否| Fail[合并失败<br>降级到备份策略]
    Validate -->|是| Compare[比较结构]

    Compare --> DeepMerge[深度合并对象]

    DeepMerge --> MergeRules[应用合并规则:<br/>• 新默认值 + 用户自定义<br/>• 新增字段使用新值<br/>• 删除字段保留用户值]

    MergeRules --> ValidateResult{验证结果}

    ValidateResult -->|有效 JSON| AddMetadata[添加合并元数据]
    ValidateResult -->|无效| Fail

    AddMetadata --> Write[写入配置文件]

    Write --> LogChanges[记录变更日志]

    LogChanges --> Success([合并成功])

    Fail --> Backup[降级: 备份后覆盖]

    Backup --> End([完成])

    %% 样式
    classDef process fill:#87CEEB,stroke:#333,stroke-width:2px
    classDef decision fill:#FFE4B5,stroke:#333,stroke-width:2px
    classDef success fill:#90EE90,stroke:#333,stroke-width:2px
    classDef fail fill:#FF6B6B,stroke:#333,stroke-width:2px

    class Start,Parse,Compare,DeepMerge,MergeRules,AddMetadata,Write,LogChanges,End process
    class Validate,ValidateResult decision
    class Success success
    class Fail,Backup fail
```

---

## 交互式冲突解决流程

```mermaid
flowchart TD
    Start([检测到冲突]) --> ShowInfo[显示冲突信息]

    ShowInfo --> FileInfo[文件路径、类型]
    ShowInfo --> VersionInfo[现有版本、新版本]
    ShowInfo --> ChangeInfo[变更统计]

    FileInfo,VersionInfo,ChangeInfo --> ShowOptions[显示选项]

    ShowOptions --> UserChoice{用户选择}

    UserChoice -->|1: 跳过| Skip[保留现有文件]
    UserChoice -->|2: 备份后更新| Backup[创建备份并更新]
    UserChoice -->|3: 强制覆盖| Force[直接覆盖]
    UserChoice -->|4: 查看差异| Diff[显示详细差异]
    UserChoice -->|5: 全部应用相同| ApplyAll[记录全局策略]
    UserChoice -->|6: 取消| Cancel[取消操作]

    Diff --> ShowOptions

    ApplyAll --> BatchMode[进入批量模式<br>后续冲突使用相同策略]

    BatchMode --> Process[执行操作]

    Skip --> Process
    Backup --> Process
    Force --> Process

    Process --> RecordAction[记录操作]

    RecordAction --> NextConflict{还有冲突?}

    NextConflict -->|是| ShowInfo
    NextConflict -->|否| Summary[生成摘要报告]

    Cancel --> Rollback[清理临时文件]

    Summary --> End([完成])
    Rollback --> End

    %% 样式
    classDef info fill:#87CEEB,stroke:#333,stroke-width:2px
    classDef choice fill:#FFE4B5,stroke:#333,stroke-width:2px
    classDef action fill:#90EE90,stroke:#333,stroke-width:2px
    classDef cancel fill:#FF6B6B,stroke:#333,stroke-width:2px

    class ShowInfo,FileInfo,VersionInfo,ChangeInfo,ShowOptions info
    class UserChoice,NextConflict choice
    class Skip,Backup,Force,Process,RecordAction,ApplyAll,BatchMode,Summary action
    class Diff,Cancel,Rollback cancel
```

---

## 批量安装冲突处理流程

```mermaid
flowchart TD
    Start([批量安装开始]) --> SetStrategy[设置全局策略<br>默认: skip]

    SetStrategy --> Scan[扫描所有文件]

    Scan --> Classify[分类文件]

    Classify --> NoConflict[无冲突文件]
    Classify --> HasConflict[冲突文件]

    NoConflict --> InstallDirect[直接安装]

    HasConflict --> ApplyStrategy[应用全局策略]

    ApplyStrategy --> Strategy{全局策略}

    Strategy -->|skip| SkipAll[跳过所有冲突]
    Strategy -->|backup| BackupAll[备份所有冲突]
    Strategy -->|force| ForceAll[覆盖所有冲突]
    Strategy -->|ask| AskEach[逐个询问]

    SkipAll --> RecordSkip
    BackupAll --> RecordBackup
    ForceAll --> RecordForce
    AskEach --> RecordAsk
    InstallDirect --> RecordSuccess

    RecordSkip[记录: 跳过]
    RecordBackup[记录: 备份并覆盖]
    RecordForce[记录: 强制覆盖]
    RecordAsk[记录: 用户决策]
    RecordSuccess[记录: 成功安装]

    RecordSkip,RecordBackup,RecordForce,RecordAsk,RecordSuccess --> NextFile

    NextFile{还有文件?}

    NextFile -->|是| Classify
    NextFile -->|否| GenerateReport[生成摘要报告]

    GenerateReport --> Report[报告内容:<br/>• 总数统计<br/>• 成功/跳过/失败<br/>• 冲突列表<br/>• 备份位置]

    Report --> ShowNextSteps[显示后续步骤]

    ShowNextSteps --> End([完成])

    %% 样式
    classDef start fill:#87CEEB,stroke:#333,stroke-width:2px
    classDef process fill:#FFE4B5,stroke:#333,stroke-width:2px
    classDef success fill:#90EE90,stroke:#333,stroke-width:2px
    classDef warning fill:#FFD700,stroke:#333,stroke-width:2px
    classDef report fill:#DDA0DD,stroke:#333,stroke-width:2px

    class Start,SetStrategy,Scan,Classify,End start
    class InstallDirect,ApplyStrategy,Strategy,AskEach process
    class RecordSuccess success
    class SkipAll,BackupAll,ForceAll warning
    class RecordSkip,RecordBackup,RecordForce,RecordAsk,NextFile,GenerateReport,Report,ShowNextSteps report
```

---

## 回滚流程

```mermaid
flowchart TD
    Start([触发回滚]) --> FindBackup[查找备份]

    FindBackup --> BackupExists{备份存在?}

    BackupExists -->|否| Error[错误: 无备份]
    BackupExists -->|是| ValidateBackup{备份有效?}

    ValidateBackup -->|否| Error
    ValidateBackup -->|是| ShowBackup[显示备份信息]

    ShowBackup --> Confirm[确认回滚操作]

    Confirm --> UserConfirm{用户确认?}

    UserConfirm -->|否| Cancel[取消回滚]
    UserConfirm -->|是| CreateSnapshot[创建当前快照<br>用于撤销回滚]

    CreateSnapshot --> Restore[恢复备份文件]

    Restore --> ValidateRestore{验证恢复结果}

    ValidateRestore -->|失败| RollbackRollback[回滚回滚操作<br>恢复快照]
    ValidateRestore -->|成功| RecordRollback[记录回滚]

    RecordRollback --> Cleanup[清理备份?<br>可选]

    Cleanup --> Success([回滚成功])

    RollbackRollback --> Error2[回滚失败]
    Cancel --> End([结束])
    Error --> End
    Error2 --> End

    %% 样式
    classDef process fill:#87CEEB,stroke:#333,stroke-width:2px
    classDef decision fill:#FFE4B5,stroke:#333,stroke-width:2px
    classDef success fill:#90EE90,stroke:#333,stroke-width:2px
    classDef error fill:#FF6B6B,stroke:#333,stroke-width:2px

    class Start,FindBackup,ShowBackup,Confirm,CreateSnapshot,Restore,RecordRollback,Cleanup,End process
    class BackupExists,ValidateBackup,UserConfirm,ValidateRestore decision
    class Success success
    class Error,Error2,Cancel,RollbackRollback error
```

---

## 使用这些决策图

### 如何阅读

1. **从上到下**：按照箭头方向阅读流程
2. **菱形框**：表示决策点，根据条件选择路径
3. **颜色编码**：
   - 🟢 绿色：安全操作
   - 🟡 黄色：需要注意的决策点
   - 🔴 红色：危险操作
   - 🔵 蓝色：常规处理流程

### 在实现中应用

1. **代码结构**：每个决策图对应一个或多个函数
2. **状态机**：使用状态机模式跟踪当前决策状态
3. **日志记录**：在每个决策点记录决策理由
4. **测试覆盖**：为每个决策路径编写测试用例

### 示例：实现"主决策流程"

```javascript
class ConflictResolver {
  async resolve(filePath, newContent, options) {
    // 对应决策图：文件是否存在?
    if (!fs.existsSync(filePath)) {
      return { action: 'installed' };
    }

    // 对应决策图：内容是否相同?
    const existingHash = await computeHash(filePath);
    const newHash = await hashContent(newContent);

    if (existingHash === newHash) {
      return { action: 'skipped', reason: 'identical' };
    }

    // 对应决策图：识别文件类型
    const fileType = this.detectFileType(filePath);

    // 对应决策图：根据文件类型处理
    return this.resolveByType(fileType, filePath, newContent, options);
  }
}
```

---

**文档版本**: 1.0.0
**最后更新**: 2025-01-03
**相关文档**:
- `file-conflict-strategy-research.md` (完整研究报告)
- `EXECUTIVE_SUMMARY.md` (执行摘要)
- `spec.md` (功能规范)
