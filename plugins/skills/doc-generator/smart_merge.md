# 智能合并 Skill

**功能**: 合并现有文档和新生成内容，保留手动编辑

**版本**: 3.1.0

---

## 概述

智能合并 skill 通过以下策略保留用户手动编辑：
1. **区域标记识别** - 提取 `<!-- WIKI-GEN-START/END -->` 包裹的自动生成区域
2. **手动编辑检测** - 识别 `<!-- MANUAL-EDIT -->` 或 `<!-- KEEP -->` 标记
3. **智能合并** - 保留手动编辑区域，更新自动生成区域

---

## 核心策略

### 策略 1: 区域标记

文档中的自动生成区域使用以下标记包裹：

```markdown
<!-- WIKI-GEN-START: region-name -->
自动生成的内容
<!-- WIKI-GEN-END: region-name -->
```

### 策略 2: 手动编辑保护

用户可以通过以下方式保护内容：

```markdown
<!-- MANUAL-EDIT -->
这部分内容永远不会被覆盖
<!-- END-MANUAL-EDIT -->
```

或使用简化标记：

```markdown
<!-- KEEP -->
保留此内容
<!-- END-KEEP -->
```

### 策略 3: 合并规则

| 情况 | 行为 |
|------|------|
| 区域有 `MANUAL-EDIT` 标记 | 完全保留现有内容 |
| 区域有 `KEEP` 标记 | 完全保留现有内容 |
| 区域内容变化 >20% | 标记为 `WIKI-GEN-PRESERVED` |
| 区域无手动标记 | 使用新生成的内容 |
| 区域外内容 | 完全保留 |

---

## 核心函数

### smart_merge()

**功能**: 合并现有文档和新内容，保留手动编辑

**用法**:
```bash
smart_merge <existing_doc_path> <new_content> [output_path]
```

**参数**:
- `existing_doc_path`: 现有文档路径
- `new_content`: 新生成的内容（字符串）
- `output_path`: 可选，输出路径（默认覆盖现有文档）

**输出**: 合并后的文档内容

```bash
#!/usr/bin/env bash
# 智能合并主函数
# 用法: smart_merge <existing_doc_path> <new_content> [output_path]

smart_merge() {
    local existing_doc=$1
    local new_content=$2
    local output_path=${3:-$existing_doc}

    # 检查现有文档是否存在
    if [ ! -f "$existing_doc" ]; then
        # 文档不存在，直接创建
        echo "$new_content" > "$output_path"
        echo "✅ 已创建新文档: $output_path"
        return 0
    fi

    # 使用内联 Python 执行合并
    local merged=$(python3 <<'PYTHON_EOF'
import re
import sys
import json

def extract_regions(content):
    """提取所有标记区域"""
    regions = {}
    pattern = r'<!-- WIKI-GEN-START: ([\w-]+) -->(.*?)<!-- WIKI-GEN-END: \1 -->'
    matches = re.finditer(pattern, content, re.DOTALL)
    for match in matches:
        name = match.group(1)
        region_content = match.group(2).strip()
        regions[name] = region_content
    return regions

def detect_manual_edit(region_content):
    """检测是否有手动编辑标记"""
    manual_markers = [
        '<!-- MANUAL-EDIT -->',
        '<!-- KEEP -->',
        '<!-- END-MANUAL-EDIT -->',
        '<!-- END-KEEP -->'
    ]
    for marker in manual_markers:
        if marker in region_content:
            return True
    return False

def calculate_content_similarity(content1, content2):
    """计算内容相似度（简单方法）"""
    if not content1 or not content2:
        return 0.0

    lines1 = set(content1.split('\n'))
    lines2 = set(content2.split('\n'))

    if not lines1 or not lines2:
        return 0.0

    intersection = len(lines1 & lines2)
    union = len(lines1 | lines2)

    return intersection / union if union > 0 else 0.0

def merge_documents(existing, new):
    """合并两个文档"""
    existing_regions = extract_regions(existing)
    new_regions = extract_regions(new)

    merged_lines = []
    in_region = False
    current_region = None
    region_content = []

    lines = existing.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # 检测区域开始
        start_match = re.match(r'<!-- WIKI-GEN-START: ([\w-]+) -->', line)
        if start_match:
            in_region = True
            current_region = start_match.group(1)
            region_content = []
            i += 1
            continue

        # 检测区域结束
        end_match = re.match(r'<!-- WIKI-GEN-END: [\w-]+ -->', line)
        if end_match and in_region:
            in_region = False

            existing_content = '\n'.join(region_content)
            new_content = new_regions.get(current_region, '')

            # 决策：使用哪个版本
            use_existing = False
            reason = ""

            if detect_manual_edit(existing_content):
                use_existing = True
                reason = "MANUAL_EDIT"
            elif not new_content:
                # 新内容中没有该区域，保留现有
                use_existing = True
                reason = "NOT_IN_NEW"
            else:
                # 计算相似度
                similarity = calculate_content_similarity(existing_content, new_content)
                if similarity < 0.8:  # 相似度低于 80%
                    use_existing = True
                    reason = f"LOW_SIMILARITY({similarity:.2f})"

            # 添加标记和内容
            if use_existing:
                merged_lines.append(f"<!-- WIKI-GEN-PRESERVED: {current_region} --> ({reason})")
                merged_lines.append(existing_content)
            else:
                merged_lines.append(f"<!-- WIKI-GEN-UPDATED: {current_region} -->")
                merged_lines.append(new_content)

            merged_lines.append(f"<!-- WIKI-GEN-END: {current_region} -->")
            current_region = None
            i += 1
            continue

        # 收集区域内容
        if in_region:
            region_content.append(line)
        else:
            merged_lines.append(line)

        i += 1

    return '\n'.join(merged_lines)

# 生成合并报告
def generate_merge_report(existing, new, merged):
    """生成合并报告"""
    existing_regions = extract_regions(existing)
    new_regions = extract_regions(new)

    all_regions = set(existing_regions.keys()) | set(new_regions.keys())

    report = {
        'total_regions': len(all_regions),
        'preserved_regions': 0,
        'updated_regions': 0,
        'new_regions': 0,
        'deleted_regions': 0,
        'regions_detail': []
    }

    for region in all_regions:
        existing_content = existing_regions.get(region, '')
        new_content = new_regions.get(region, '')

        if not existing_content and new_content:
            report['new_regions'] += 1
            report['regions_detail'].append({
                'region': region,
                'status': 'new'
            })
        elif existing_content and not new_content:
            report['deleted_regions'] += 1
            report['regions_detail'].append({
                'region': region,
                'status': 'deleted'
            })
        elif detect_manual_edit(existing_content):
            report['preserved_regions'] += 1
            report['regions_detail'].append({
                'region': region,
                'status': 'preserved',
                'reason': 'manual_edit'
            })
        else:
            similarity = calculate_content_similarity(existing_content, new_content)
            if similarity < 0.8:
                report['preserved_regions'] += 1
                report['regions_detail'].append({
                    'region': region,
                    'status': 'preserved',
                    'reason': f'low_similarity({similarity:.2f})'
                })
            else:
                report['updated_regions'] += 1
                report['regions_detail'].append({
                    'region': region,
                    'status': 'updated'
                })

    return report

# 主逻辑
if len(sys.argv) < 3:
    print("Usage: smart_merge <existing_doc> <new_content>", file=sys.stderr)
    sys.exit(1)

existing_path = sys.argv[1]
new_content = sys.argv[2]

try:
    with open(existing_path, 'r', encoding='utf-8') as f:
        existing = f.read()
except Exception as e:
    print(f"Error reading existing document: {e}", file=sys.stderr)
    print(new_content)  # 返回新内容
    sys.exit(0)

merged = merge_documents(existing, new_content)
report = generate_merge_report(existing, new_content, merged)

# 输出合并后的内容
print(merged)

# 输出报告到 stderr
print(json.dumps(report, indent=2, ensure_ascii=False), file=sys.stderr)
PYTHON_EOF
)

    # 写入文件
    echo "$merged" > "$output_path"

    # 提取合并报告（stderr）
    local report=$(python3 <<'PYTHON_EOF'
import sys
import json

# 读取 stderr 中的报告
report_data = []
for line in sys.stderr:
    try:
        data = json.loads(line)
        report_data.append(data)
    except:
        continue

if report_data:
    print(json.dumps(report_data[0], indent=2, ensure_ascii=False))
PYTHON_EOF
)

    # 输出报告
    if [ -n "$report" ]; then
        local total=$(echo "$report" | jq '.total_regions')
        local preserved=$(echo "$report" | jq '.preserved_regions')
        local updated=$(echo "$report" | jq '.updated_regions')

        echo "📊 合并报告:"
        echo "  - 总区域数: $total"
        echo "  - 保留区域: $preserved"
        echo "  - 更新区域: $updated"

        # 显示详细信息
        if [ "$preserved" -gt 0 ]; then
            echo "🔒 保留的区域:"
            echo "$report" | jq -r '.regions_detail[] | select(.status == "preserved") | "  - \(.region): \(.reason)"'
        fi
    fi

    echo "✅ 文档已合并: $output_path"
}
```

---

## 辅助函数

### extract_regions()

**功能**: 提取文档中的所有标记区域

```python
import re

def extract_regions(content):
    """提取所有标记区域"""
    regions = {}
    pattern = r'<!-- WIKI-GEN-START: ([\w-]+) -->(.*?)<!-- WIKI-GEN-END: \1 -->'
    matches = re.finditer(pattern, content, re.DOTALL)
    for match in matches:
        name = match.group(1)
        region_content = match.group(2).strip()
        regions[name] = region_content
    return regions
```

### detect_manual_edit()

**功能**: 检测区域是否有手动编辑标记

```python
def detect_manual_edit(region_content):
    """检测是否有手动编辑标记"""
    manual_markers = [
        '<!-- MANUAL-EDIT -->',
        '<!-- KEEP -->'
    ]
    for marker in manual_markers:
        if marker in region_content:
            return True
    return False
```

### calculate_content_similarity()

**功能**: 计算两个内容的相似度

```python
def calculate_content_similarity(content1, content2):
    """计算内容相似度（简单方法）"""
    if not content1 or not content2:
        return 0.0

    lines1 = set(content1.split('\n'))
    lines2 = set(content2.split('\n'))

    if not lines1 or not lines2:
        return 0.0

    intersection = len(lines1 & lines2)
    union = len(lines1 | lines2)

    return intersection / union if union > 0 else 0.0
```

---

## 使用示例

### 示例 1: 基本合并

```bash
# 现有文档: docs/zh/概述.md
# 新内容: $NEW_CONTENT

smart_merge "docs/zh/概述.md" "$NEW_CONTENT"
```

**输出**:
```
📊 合并报告:
  - 总区域数: 5
  - 保留区域: 1
  - 更新区域: 4
🔒 保留的区域:
  - concepts: manual_edit
✅ 文档已合并: docs/zh/概述.md
```

### 示例 2: 输出到不同文件

```bash
# 生成预览版本
smart_merge "docs/zh/概述.md" "$NEW_CONTENT" "docs/zh/概述.preview.md"
```

### 示例 3: 批量合并

```bash
# 遍历所有受影响的文档
for doc in "${affected_docs[@]}"; do
    existing_doc="docs/zh/$doc.md"
    new_content=$(generate_document "$doc")

    if [ -f "$existing_doc" ]; then
        smart_merge "$existing_doc" "$new_content"
    else
        echo "$new_content" > "$existing_doc"
    fi
done
```

---

## 合并报告格式

```json
{
  "total_regions": 5,
  "preserved_regions": 1,
  "updated_regions": 4,
  "new_regions": 0,
  "deleted_regions": 0,
  "regions_detail": [
    {
      "region": "metadata",
      "status": "updated"
    },
    {
      "region": "concepts",
      "status": "preserved",
      "reason": "manual_edit"
    },
    {
      "region": "usage",
      "status": "updated"
    }
  ]
}
```

---

## 配置选项

### wiki-config.json

```json
{
  "smart_merge": {
    "enabled": true,
    "region_markers": {
      "start": "<!-- WIKI-GEN-START: {name} -->",
      "end": "<!-- WIKI-GEN-END: {name} -->"
    },
    "manual_edit_markers": [
      "<!-- MANUAL-EDIT -->",
      "<!-- KEEP -->"
    ],
    "similarity_threshold": 0.8,
    "merge_conflicts": "skip"  // "skip" | "overwrite" | "ask"
  }
}
```

---

## 故障排除

### 问题 1: 合并后文档格式错乱

**原因**: 区域标记不匹配

**解决方案**:
```bash
# 检查文档中的区域标记
grep "<!-- WIKI-GEN" docs/zh/概述.md
```

确保每个 `<!-- WIKI-GEN-START -->` 都有对应的 `<!-- WIKI-GEN-END -->`

### 问题 2: 手动编辑内容被覆盖

**原因**: 未添加手动编辑标记

**解决方案**: 在需要保护的内容前后添加标记：
```markdown
<!-- MANUAL-EDIT -->
这部分内容不会被覆盖
<!-- END-MANUAL-EDIT -->
```

### 问题 3: 相似度检测不准确

**原因**: 简单的行匹配算法不够精确

**解决方案**: 调整相似度阈值
```json
{
  "smart_merge": {
    "similarity_threshold": 0.9  // 提高阈值到 90%
  }
}
```

---

## 最佳实践

### 1. 使用有意义的区域名称

```markdown
<!-- WIKI-GEN-START: user-authentication -->
用户认证内容...
<!-- WIKI-GEN-END: user-authentication -->
```

避免使用 `region1`, `region2` 等通用名称。

### 2. 保护关键配置

```markdown
## 环境变量

<!-- MANUAL-EDIT -->
以下环境变量必须手动配置：
- API_KEY: 从控制台获取
- SECRET_KEY: 使用强密码生成器
<!-- END-MANUAL-EDIT -->
```

### 3. 定期检查合并报告

```bash
# 生成合并后查看报告
smart_merge "docs/zh/概述.md" "$NEW_CONTENT" | tee report.txt
```

---

## 集成点

### 调用方: wiki-generate 命令

```markdown
### 增量更新流程

1. **检测变更**
   ```bash
   changes=$(detect_changes "$PROJECT_DIR")
   ```

2. **生成新内容**
   ```bash
   new_content=$(generate_document "$doc_name")
   ```

3. **智能合并**
   ```bash
   if [ -f "$OUTPUT_DIR/$doc_name.md" ]; then
       smart_merge "$OUTPUT_DIR/$doc_name.md" "$new_content"
   else
       echo "$new_content" > "$OUTPUT_DIR/$doc_name.md"
   fi
   ```

4. **记录元数据**
   ```bash
   source_files=$(get_document_sources "$doc_name")
   record_document "$doc_name" "$source_files" "$current_commit"
   ```
```

---

**版本**: 3.1.0
**最后更新**: 2026-01-07
