# 配置迁移指南

**版本**: 2.0.0
**最后更新**: 2025-01-04

---

## 概述

本指南说明如何从 Wiki Generator v1.0 迁移到 v2.0。

---

## v1.0 → v2.0 变更

### 配置文件结构变更

| 字段 | v1.0 | v2.0 | 说明 |
|------|------|------|------|
| `lang` | ✅ | ❌ | 重命名为 `language` |
| `language` | ❌ | ✅ | 新字段，替代 `lang` |
| `output_dir` | ❌ | ✅ | 新增，默认 `"docs"` |
| `structure_template` | ❌ | ✅ | 新增，默认 `"reference"` |
| `include_sources` | ❌ | ✅ | 新增，默认 `true` |
| `generate_toc` | ❌ | ✅ | 新增，默认 `true` |
| `version` | ❌ | ✅ | 新增，当前版本号 |

### 迁移规则

1. **字段重命名**: `lang` → `language`
2. **添加默认值**: 为所有新字段添加合理的默认值
3. **版本标记**: 添加 `version` 字段为 `"2.0.0"`

---

## 自动迁移

### 使用命令行工具

```bash
# 迁移配置文件（自动备份）
wiki-generator --migrate

# 指定配置文件路径
wiki-generator --migrate --config .claude/wiki-config.json

# 不创建备份（不推荐）
wiki-generator --migrate --no-backup
```

### 迁移步骤

1. **检测当前版本**
   ```bash
   wiki-generator --validate
   ```

2. **备份原文件**（自动完成）
   - 备份文件名: `wiki-config.json.backup`
   - 位置: 与原文件相同目录

3. **应用迁移规则**
   - 重命名字段
   - 添加新字段
   - 更新版本号

4. **验证迁移结果**
   ```bash
   wiki-generator --validate
   ```

---

## 手动迁移

如果你需要手动迁移配置文件，请按照以下步骤：

### 步骤 1: 备份原文件

```bash
cp .claude/wiki-config.json .claude/wiki-config.json.backup
```

### 步骤 2: 更新配置

**v1.0 配置示例**:
```json
{
  "lang": "zh"
}
```

**v2.0 配置示例**:
```json
{
  "output_dir": "docs",
  "language": "zh",
  "structure_template": "reference",
  "include_sources": true,
  "generate_toc": true,
  "version": "2.0.0"
}
```

### 步骤 3: 验证配置

```bash
wiki-generator --validate
```

---

## 迁移后验证

### 验证清单

- [ ] 配置文件验证通过
- [ ] 所有必需字段存在
- [ ] `version` 字段为 `"2.0.0"`
- [ ] `language` 字段值有效（`"zh"`, `"en"`, 或 `"both"`）
- [ ] 备份文件已创建

### 测试命令

```bash
# 验证配置
wiki-generator --validate

# 检查版本
cat .claude/wiki-config.json | grep version

# 检查语言配置
cat .claude/wiki-config.json | grep language
```

---

## 回滚

如果迁移后出现问题，可以从备份恢复：

```bash
# 恢复备份
cp .claude/wiki-config.json.backup .claude/wiki-config.json

# 验证恢复的配置
wiki-generator --validate
```

---

## 常见问题

### Q1: 迁移失败怎么办？

**A**: 检查错误消息：
1. 确保配置文件格式正确（有效的 JSON）
2. 确保有文件写入权限
3. 检查是否有足够的磁盘空间

### Q2: 迁移后配置不符合预期？

**A**:
1. 从备份恢复原文件
2. 手动编辑配置文件
3. 使用 `wiki-generator --validate` 验证

### Q3: 可以跳过版本迁移吗？

**A**: 不建议。迁移工具支持逐步迁移：
- v1.0 → v2.0
- 未来: v2.0 → v3.0

### Q4: 迁移会影响已生成的文档吗？

**A**: 不会。迁移只修改配置文件，不影响已生成的文档。

---

## 故障排除

### 问题 1: 无法检测版本

**症状**: `无法检测配置文件版本`

**解决方案**:
```bash
# 手动添加版本字段
echo '{"version": "1.0", "lang": "zh"}' > .claude/wiki-config.json
# 然后重新迁移
wiki-generator --migrate
```

### 问题 2: 备份失败

**症状**: `备份文件失败`

**解决方案**:
```bash
# 手动备份
cp .claude/wiki-config.json .claude/wiki-config.json.backup
# 然后使用 --no-backup 迁移
wiki-generator --migrate --no-backup
```

### 问题 3: 迁移后验证失败

**症状**: 配置验证错误

**解决方案**:
检查配置文件是否符合 v2.0 规范：
- `language` 必须是 `"zh"`, `"en"`, 或 `"both"`
- `structure_template` 必须是 `"reference"`, `"simple"`, 或 `"custom"`
- 如果使用 `"custom"` 模式，必须定义 `sections`

---

## 技术细节

### 迁移规则实现

迁移规则定义在 [wiki_generator/core/migrations.py](../wiki_generator/core/migrations.py)：

```python
MIGRATION_RULES = {
    "1.0": ("2.0", migrate_1_to_2),
}
```

### 迁移流程

1. **版本检测**: 读取配置文件的 `version` 字段
2. **查找规则**: 根据 `version` 查找适用的迁移规则
3. **备份文件**: 创建原文件的备份副本
4. **应用规则**: 执行迁移函数，转换配置数据
5. **写入文件**: 将迁移后的配置写回原文件
6. **生成报告**: 创建详细的迁移报告

---

## 支持

如果遇到迁移问题：

1. 查看本文档的"常见问题"和"故障排除"部分
2. 检查迁移报告（自动生成）
3. 提交 Issue: [GitHub Issues](https://github.com/winwin-inc/claude-plugins/issues)

---

**版本**: 2.0.0
**最后更新**: 2025-01-04
