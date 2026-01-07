#!/usr/bin/env bash
# 元数据追踪函数库
# 版本: 3.1.0
# 用法: source plugins/libs/metadata_tracker.sh

# WIKI_CONFIG 由调用方设置（通过 config_resolver.sh）
if [ -z "$WIKI_CONFIG" ]; then
    # 如果未设置，尝试导入配置解析库
    if [ -f "$(dirname "${BASH_SOURCE[0]}")/config_resolver.sh" ]; then
        source "$(dirname "${BASH_SOURCE[0]}")/config_resolver.sh"
        WIKI_CONFIG=$(find_config_file)
    fi

    # 如果仍然未找到，报错
    if [ -z "$WIKI_CONFIG" ]; then
        echo "❌ 错误: WIKI_CONFIG 环境变量未设置" >&2
        echo "💡 提示: 请先运行配置初始化流程" >&2
        return 1
    fi

    export WIKI_CONFIG
fi

# 获取元数据文件路径（根据配置）
# 元数据文件存储在用户配置的 output_dir 下的 .wiki-metadata/ 子目录
get_metadata_file() {
    local config_file="$WIKI_CONFIG"

    # 读取 output_dir 配置
    local output_dir=$(python3 - <<PYTHON_EOF
import json
from pathlib import Path

config_path = Path("$config_file")
if config_path.exists():
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        print(config.get('output_dir', 'docs'))
else:
    print('docs')
PYTHON_EOF
)

    # 元数据文件放在输出目录的 .wiki-metadata/ 子目录
    echo "$output_dir/.wiki-metadata/metadata.json"
}

# 初始化元数据文件
init_metadata() {
    local metadata_file=$(get_metadata_file)
    local metadata_dir=$(dirname "$metadata_file")

    # 创建目录
    mkdir -p "$metadata_dir"

    if [ ! -f "$metadata_file" ]; then
        cat > "$metadata_file" <<'EOF'
{
  "version": "3.1.0",
  "last_generation": {
    "commit": "",
    "timestamp": ""
  },
  "document_mappings": {}
}
EOF
        echo "✅ 已初始化元数据文件: $metadata_file"
    fi
}

# 记录文档生成信息
# 用法: record_document <doc_name> <source_files_json> <commit_hash>
record_document() {
    local doc_name=$1
    local source_files=$2  # JSON 数组字符串
    local commit_hash=$3
    local metadata_file=$(get_metadata_file)

    # 使用内联 Python 计算哈希并更新 JSON
    python3 - <<PYTHON_EOF
import json
import hashlib
from pathlib import Path
from datetime import datetime

metadata_file = Path("$metadata_file")
doc_name = "$doc_name"
source_files = json.loads("""$source_files""")
commit_hash = "$commit_hash"

# 加载元数据
with open(metadata_file, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

# 计算文件哈希
file_hashes = {}
for file_path in source_files:
    if Path(file_path).exists():
        try:
            with open(file_path, 'rb') as f:
                # 只计算实质性内容（排除空行和注释）
                content = f.read().decode('utf-8', errors='ignore')
                lines = [l for l in content.split('\n')
                        if l.strip() and not l.strip().startswith('#')]
                content_hash = hashlib.sha256('\n'.join(lines).encode()).hexdigest()
                file_hashes[file_path] = content_hash
        except Exception as e:
            print(f"⚠️  无法读取文件 {file_path}: {e}", file=__stderr__)

# 记录文档信息
metadata['document_mappings'][doc_name] = {
    'source_files': source_files,
    'hashes': file_hashes,
    'generated_at': datetime.utcnow().isoformat() + 'Z',
    'commit': commit_hash
}

# 保存元数据
with open(metadata_file, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print(f"✅ 已记录文档元数据: {doc_name}", file=__stderr__)
PYTHON_EOF
}

# 检查文档是否需要更新
# 用法: needs_update <doc_name>
# 输出: "UPDATE_NEEDED" | "NO_UPDATE" | "NEW_DOCUMENT" | "ERROR: ..."
needs_update() {
    local doc_name=$1
    local metadata_file=$(get_metadata_file)

    # 检查元数据文件是否存在
    if [ ! -f "$metadata_file" ]; then
        echo "NEW_DOCUMENT"
        return 0
    fi

    # 使用内联 Python 检查
    local result=$(python3 - <<PYTHON_EOF
import json
import hashlib
from pathlib import Path

metadata_file = Path("$metadata_file")
doc_name = "$doc_name"

try:
    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    doc_info = metadata['document_mappings'].get(doc_name)
    if not doc_info:
        print("NEW_DOCUMENT")
        exit(0)

    # 检查文件哈希
    stored_hashes = doc_info.get('hashes', {})
    for file_path, stored_hash in stored_hashes.items():
        if Path(file_path).exists():
            try:
                with open(file_path, 'rb') as f:
                    content = f.read().decode('utf-8', errors='ignore')
                    lines = [l for l in content.split('\n')
                            if l.strip() and not l.strip().startswith('#')]
                    current_hash = hashlib.sha256('\n'.join(lines).encode()).hexdigest()

                    if current_hash != stored_hash:
                        print(f"UPDATE_NEEDED ({file_path})")
                        exit(0)
            except Exception:
                # 文件读取失败，视为需要更新
                print(f"UPDATE_NEEDED (error reading {file_path})")
                exit(0)
        else:
            # 文件不存在，视为需要更新
            print(f"UPDATE_NEEDED ({file_path} not found)")
            exit(0)

    print("NO_UPDATE")
except Exception as e:
    print(f"ERROR: {e}")
PYTHON_EOF
)

    echo "$result"
}

# 更新全局生成信息
# 用法: update_global_metadata <commit_hash>
update_global_metadata() {
    local commit_hash=$1
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    local metadata_file=$(get_metadata_file)

    python3 - <<PYTHON_EOF
import json
from pathlib import Path

metadata_file = Path("$metadata_file")

# 确保文件存在
if not metadata_file.exists():
    metadata_file.parent.mkdir(parents=True, exist_ok=True)
    with open(metadata_file, 'w') as f:
        json.dump({
            "version": "3.1.0",
            "last_generation": {"commit": "", "timestamp": ""},
            "document_mappings": {}
        }, f)

with open(metadata_file, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

metadata['last_generation']['commit'] = "$commit_hash"
metadata['last_generation']['timestamp'] = "$timestamp"

with open(metadata_file, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)
PYTHON_EOF

    echo "✅ 已更新全局元数据 (commit: $commit_hash)"
}

# 获取上次生成的 commit hash
# 用法: get_last_commit
get_last_commit() {
    local metadata_file=$(get_metadata_file)

    if [ ! -f "$metadata_file" ]; then
        echo ""
        return 1
    fi

    python3 - <<PYTHON_EOF
import json
from pathlib import Path

metadata_file = Path("$metadata_file")
try:
    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
        print(metadata.get('last_generation', {}).get('commit', ''))
except:
    print('')
PYTHON_EOF
}

# 获取文档关联的源文件列表
# 用法: get_document_sources <doc_name>
get_document_sources() {
    local doc_name=$1
    local metadata_file=$(get_metadata_file)

    if [ ! -f "$metadata_file" ]; then
        echo "[]"
        return 1
    fi

    python3 - <<PYTHON_EOF
import json
from pathlib import Path

metadata_file = Path("$metadata_file")
doc_name = "$doc_name"

try:
    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
        doc_info = metadata['document_mappings'].get(doc_name, {})
        sources = doc_info.get('source_files', [])
        print(json.dumps(sources))
except:
    print('[]')
PYTHON_EOF
}

# 列出所有已记录的文档
# 用法: list_documents
list_documents() {
    local metadata_file=$(get_metadata_file)

    if [ ! -f "$metadata_file" ]; then
        echo "⚠️  元数据文件不存在"
        return 1
    fi

    python3 - <<PYTHON_EOF
import json
from pathlib import Path

metadata_file = Path("$metadata_file")

try:
    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
        docs = metadata.get('document_mappings', {}).keys()

        if docs:
            print("📚 已记录的文档:")
            for doc in sorted(docs):
                print(f"  - {doc}")
        else:
            print("📭 暂无已记录的文档")
except Exception as e:
    print(f"❌ 读取失败: {e}")
PYTHON_EOF
}

# 清理文档元数据
# 用法: remove_document <doc_name>
remove_document() {
    local doc_name=$1
    local metadata_file=$(get_metadata_file)

    if [ ! -f "$metadata_file" ]; then
        echo "⚠️  元数据文件不存在"
        return 1
    fi

    python3 - <<PYTHON_EOF
import json
from pathlib import Path

metadata_file = Path("$metadata_file")
doc_name = "$doc_name"

try:
    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    if doc_name in metadata.get('document_mappings', {}):
        del metadata['document_mappings'][doc_name]

        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"✅ 已删除文档元数据: {doc_name}")
    else:
        print(f"⚠️  文档不存在: {doc_name}")
except Exception as e:
    print(f"❌ 删除失败: {e}")
PYTHON_EOF
}

# 备份元数据文件
# 用法: backup_metadata
backup_metadata() {
    local metadata_file=$(get_metadata_file)

    if [ ! -f "$metadata_file" ]; then
        echo "⚠️  元数据文件不存在，无需备份"
        return 1
    fi

    local backup_dir="${metadata_file}.backup"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="${backup_dir}/metadata_${timestamp}.json"

    mkdir -p "$backup_dir"
    cp "$metadata_file" "$backup_file"

    echo "✅ 元数据已备份到: $backup_file"
}

# 恢复元数据文件
# 用法: restore_metadata <backup_file>
restore_metadata() {
    local backup_file=$1
    local metadata_file=$(get_metadata_file)

    if [ ! -f "$backup_file" ]; then
        echo "❌ 备份文件不存在: $backup_file"
        return 1
    fi

    cp "$backup_file" "$metadata_file"
    echo "✅ 元数据已从备份恢复"
}
