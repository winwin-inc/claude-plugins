# 变更检测 Skill

**功能**: 检测代码变更并映射到受影响的文档

**版本**: 3.1.0

---

## 概述

变更检测 skill 通过以下三种方式检测代码变更：
1. **Git diff 分析** - 检测自上次生成以来变更的文件
2. **哈希值比较** - 识别实质性内容变化（排除空格、注释）
3. **模块依赖分析** - 建立文档与源文件的映射关系

---

## 核心函数

### detect_changes()

**功能**: 检测代码变更并返回受影响的文档列表

**用法**:
```bash
detect_changes <project_dir> [base_commit]
```

**参数**:
- `project_dir`: 项目根目录
- `base_commit`: 可选，基准 commit（默认：上次生成的 commit）

**输出**: JSON 格式的变更信息

```bash
#!/usr/bin/env bash
# 变更检测主函数
# 用法: detect_changes <project_dir> [base_commit]

detect_changes() {
    local project_dir=$1
    local base_commit=$2

    # 1. 获取上次生成的 commit（如果未提供）
    if [ -z "$base_commit" ]; then
        base_commit=$(get_last_commit)
        if [ -z "$base_commit" ]; then
            # 首次生成，使用当前 commit 的父提交
            base_commit=$(git -C "$project_dir" rev-parse HEAD^ 2>/dev/null || echo "")
        fi
    fi

    local current_commit=$(git -C "$project_dir" rev-parse HEAD)

    # 如果没有基准 commit，视为首次生成
    if [ -z "$base_commit" ]; then
        cat <<EOF
{
  "base_commit": "",
  "current_commit": "$current_commit",
  "is_initial": true,
  "changed_files": [],
  "affected_documents": "all",
  "deleted_files": []
}
EOF
        return 0
    fi

    # 2. Git diff 分析
    local changed_files=$(git -C "$project_dir" diff --name-only "$base_commit" "$current_commit" 2>/dev/null)

    # 3. 过滤源代码文件
    local source_files=$(filter_source_files "$changed_files")

    # 4. 计算哈希值
    local hashes_json=$(calculate_batch_hashes_json "$source_files")

    # 5. 映射到受影响的文档
    local affected_docs=$(map_to_documents "$source_files" "$project_dir")

    # 6. 输出 JSON 结果
    cat <<EOF
{
  "base_commit": "$base_commit",
  "current_commit": "$current_commit",
  "is_initial": false,
  "changed_files": $(echo "$source_files" | jq -R -s -c 'split("\n")[:-1]'),
  "file_hashes": $hashes_json,
  "affected_documents": $affected_docs,
  "deleted_files": []
}
EOF
}
```

---

## 辅助函数

### filter_source_files()

**功能**: 过滤只包含源代码文件（排除测试、mocks 等）

```bash
#!/usr/bin/env bash
# 过滤源代码文件
# 用法: filter_source_files <file_list>
# 注意: WIKI_CONFIG 环境变量由调用方设置（通过 config_resolver.sh）

filter_source_files() {
    local file_list=$1

    # 从配置读取排除模式
    # WIKI_CONFIG 环境变量由 config_resolver.sh 管理
    # 配置文件位置: {output_dir}/wiki-config.json
    local exclude_patterns=$(python3 - <<PYTHON_EOF
import json
from pathlib import Path

config_path = Path("$WIKI_CONFIG")
if config_path.exists():
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        patterns = config.get('change_detection', {}).get('exclude_patterns', [])
        print('|'.join(patterns))
else:
    print('tests/**|*.test.*|mocks/**')
PYTHON_EOF
)

    # 过滤文件
    echo "$file_list" | grep -E '\.(py|js|ts|tsx|jsx|go|java|rs|rb|php|cs|swift|kt)$' | \
        grep -v -E '(test_|_test\.|\.test\.)' | \
        grep -v -E "$exclude_patterns" || true
}
```

### calculate_batch_hashes_json()

**功能**: 批量计算文件哈希值

```bash
#!/usr/bin/env bash
# 批量计算文件哈希
# 用法: calculate_batch_hashes_json <file_list>

calculate_batch_hashes_json() {
    local file_list=$1

    # 转换为 JSON 数组
    local files_json=$(echo "$file_list" | jq -R -s -c 'split("\n")[:-1]')

    # 使用内联 Python 计算哈希
    python3 <<PYTHON_EOF
import json
import hashlib
from pathlib import Path

files = json.loads('''$files_json''')
hashes = {}

for file_path in files:
    if Path(file_path).exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # 提取实质性内容（排除空行和注释）
                lines = [l.strip() for l in f
                        if l.strip() and not l.strip().startswith('#')]
                content = '\n'.join(lines)
                hashes[file_path] = hashlib.sha256(content.encode()).hexdigest()
        except Exception as e:
            hashes[file_path] = None
    else:
        hashes[file_path] = None

print(json.dumps(hashes, indent=2))
PYTHON_EOF
}
```

### map_to_documents()

**功能**: 将变更文件映射到受影响的文档

```bash
#!/usr/bin/env bash
# 映射文件到文档
# 用法: map_to_documents <file_list> <project_dir>

map_to_documents() {
    local file_list=$1
    local project_dir=$2

    # 使用内联 Python 执行映射
    python3 <<PYTHON_EOF
import json
from pathlib import Path
import re

files_str = """$file_list"""
changed_files = [f for f in files_str.split('\n') if f.strip()]

# 文档到源文件的映射规则
document_mappings = {
    'quickstart': ['README.md', 'README.txt', 'README', 'package.json', 'pyproject.toml', 'setup.py', 'pom.xml', 'build.gradle'],
    'overview': ['README.md', 'CONTRIBUTING.md', 'docs/*.md'],
    'techstack': ['package.json', 'requirements.txt', 'pyproject.toml', 'go.mod', 'Cargo.toml', 'pom.xml', 'Gemfile'],
    'architecture': ['src/**/*.py', 'src/**/*.js', 'src/**/*.ts', 'app/**/*.py', 'lib/**/*.py'],
    'datamodel': ['**/models/**/*.py', '**/model/**/*.py', '**/entities/**/*.py', '**/schemas/**/*.py'],
    'api': ['**/api/**/*.py', '**/routes/**/*.py', '**/controllers/**/*.py', '**/handlers/**/*.py'],
    'corefeatures': ['src/**/*.py', 'app/**/*.py', 'lib/**/*.py'],
    'deployment': ['Dockerfile', 'docker-compose.yml', 'k8s/**/*.yaml', '*.deploy.yml', 'deployment/*.yml'],
    'testing': ['tests/**/*.py', 'test/**/*.py', '**/*_test.py', '**/test_*.py'],
    'security': ['**/auth/**/*.py', '**/security/**/*.py', '**/middleware/**/*.py']
}

# 找出受影响的文档
affected_docs = set()

for file_path in changed_files:
    file_name = Path(file_path).name
    file_dir = Path(file_path).parent.as_posix()

    for doc_name, patterns in document_mappings.items():
        for pattern in patterns:
            # 简单模式匹配
            if pattern in file_path:
                affected_docs.add(doc_name)
                break
            # 通配符匹配
            elif '**' in pattern or '*' in pattern:
                # 将 glob 模式转换为正则表达式
                regex_pattern = pattern.replace('**', '.*').replace('*', '[^/]*')
                if re.search(regex_pattern, file_path) or re.search(regex_pattern, file_dir):
                    affected_docs.add(doc_name)
                    break

if affected_docs:
    print(json.dumps(sorted(affected_docs), indent=2))
else:
    print('[]')
PYTHON_EOF
}
```

---

## 使用示例

### 示例 1: 检测自上次生成以来的变更

```bash
# 加载元数据追踪库
source plugins/libs/metadata_tracker.sh

# 检测变更
changes=$(detect_changes ".")

# 解析结果
base_commit=$(echo "$changes" | jq -r '.base_commit')
affected_docs=$(echo "$changes" | jq -r '.affected_documents')

echo "基准 commit: $base_commit"
echo "受影响的文档: $affected_docs"
```

### 示例 2: 与现有文档对比

```bash
# 检测变更
changes=$(detect_changes ".")

# 遍历受影响的文档
for doc in $(echo "$changes" | jq -r '.affected_documents[]'); do
    # 检查文档是否需要更新
    update_status=$(needs_update "$doc")

    if [[ "$update_status" == UPDATE_NEEDED* ]]; then
        echo "📝 文档 '$doc' 需要更新: $update_status"
    fi
done
```

### 示例 3: 检测特定文件变更

```bash
# 检测特定文件的变更
changes=$(detect_changes "." "abc123")

# 获取变更文件列表
changed_files=$(echo "$changes" | jq -r '.changed_files[]')

for file in $changed_files; do
    echo "📄 变更文件: $file"
done
```

---

## 输出格式

### 首次生成

```json
{
  "base_commit": "",
  "current_commit": "abc123...",
  "is_initial": true,
  "changed_files": [],
  "affected_documents": "all",
  "deleted_files": []
}
```

### 增量更新

```json
{
  "base_commit": "abc123...",
  "current_commit": "def456...",
  "is_initial": false,
  "changed_files": [
    "src/models/user.py",
    "src/services/user_service.py",
    "api/routes/users.py"
  ],
  "file_hashes": {
    "src/models/user.py": "sha256...",
    "src/services/user_service.py": "sha256...",
    "api/routes/users.py": "sha256..."
  },
  "affected_documents": [
    "datamodel",
    "api",
    "corefeatures"
  ],
  "deleted_files": []
}
```

---

## 配置选项

### wiki-config.json

```json
{
  "change_detection": {
    "method": "both",  // "git" | "hash" | "both"
    "base_commit": "",  // 留空自动检测
    "exclude_patterns": [
      "tests/**",
      "*.test.*",
      "mocks/**",
      "**/*.spec.ts",
      "**/*.test.js"
    ]
  }
}
```

---

## 故障排除

### 问题 1: Git 仓库未初始化

**错误**: `fatal: not a git repository`

**解决方案**:
```bash
# 在项目目录中初始化 Git 仓库
git init
git add -A
git commit -m "Initial commit"
```

### 问题 2: 无 commit 历史

**错误**: `fatal: bad revision 'HEAD^'`

**解决方案**: 检测首次生成，返回所有文档：
```bash
if ! git rev-parse HEAD^ >/dev/null 2>&1; then
    echo '{"is_initial": true, "affected_documents": "all"}'
fi
```

### 问题 3: 元数据文件损坏

**解决方案**: 使用备份恢复
```bash
# 恢复最近的备份
restore_metadata "docs/.wiki-metadata/metadata.json.backup/metadata_*.json"
```

---

## 性能优化

### 批量哈希计算

使用并行计算加速哈希计算（如果文件数量大）:

```bash
# 安装 parallel（如果未安装）
# sudo apt-get install parallel

# 并行计算哈希
calculate_parallel_hashes() {
    local files=$1

    echo "$files" | parallel -j 4 'calculate_file_hash {}' | \
        paste -sd,
}
```

### 缓存机制

对于未变更的文件，使用缓存的哈希值：

```bash
# 在元数据中存储哈希缓存
# 只对实际变更的文件重新计算哈希
```

---

## 集成点

### 调用方: wiki-generate 命令

```markdown
### 增量更新模式

1. **加载元数据**
   ```bash
   source plugins/libs/metadata_tracker.sh
   init_metadata
   ```

2. **变更检测**
   ```bash
   changes=$(detect_changes "$PROJECT_DIR")
   affected_docs=$(echo "$changes" | jq -r '.affected_documents')
   ```

3. **选择性生成**
   ```bash
   for doc in $affected_docs; do
       if needs_update "$doc" | grep -q "UPDATE_NEEDED"; then
           # 生成新内容
           new_content=$(generate_document "$doc")

           # 智能合并
           if [ -f "$OUTPUT_DIR/$doc.md" ]; then
               merged=$(smart_merge "$OUTPUT_DIR/$doc.md" "$new_content")
               echo "$merged" > "$OUTPUT_DIR/$doc.md"
           else
               echo "$new_content" > "$OUTPUT_DIR/$doc.md"
           fi
       fi
   done
   ```

4. **更新元数据**
   ```bash
   current_commit=$(git rev-parse HEAD)
   update_global_metadata "$current_commit"
   ```
```

---

**版本**: 3.1.0
**最后更新**: 2026-01-07
