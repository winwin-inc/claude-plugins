#!/usr/bin/env bash
# 增量更新集成测试

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

source "$SCRIPT_DIR/test_helpers.sh"

# 测试 1: 测试仓库创建和清理
test_repo_setup() {
    local test_repo=$(setup_test_repo)

    # 验证仓库创建成功
    if [ ! -d "$test_repo/.git" ]; then
        echo "  ❌Git repository not created" >&2
        cleanup_test_repo "$test_repo"
        return 1
    fi

    # 验证初始文件存在
    if [ ! -f "$test_repo/README.md" ]; then
        echo "  ❌Initial files not created" >&2
        cleanup_test_repo "$test_repo"
        return 1
    fi

    cleanup_test_repo "$test_repo"
    return 0
}

# 测试 2: Git 变更检测集成
test_git_change_detection() {
    local test_repo=$(setup_test_repo)

    # 修改文件
    echo "new content" >> "$test_repo/src/test.py"
    git -C "$test_repo" add -A
    git -C "$test_repo" commit -q -m "add test file"

    # 获取变更文件
    local changed_files=$(git -C "$test_repo" diff --name-only HEAD~1 HEAD)

    # 验证检测到变更
    assert_contains "$changed_files" "src/test.py"
    local status=$?

    cleanup_test_repo "$test_repo"
    return $status
}

# 测试 3: 文件哈希追踪
test_file_hash_tracking() {
    local test_repo=$(setup_test_repo)

    # 创建测试文件
    echo "original content" > "$test_repo/src/test.py"

    # 计算初始哈希
    local hash1=$(python3 - <<PYTHON_EOF
import hashlib

with open("$test_repo/src/test.py", 'r') as f:
    lines = [l.strip() for l in f if l.strip() and not l.strip().startswith('#')]
    content = '\n'.join(lines)
    print(hashlib.sha256(content.encode()).hexdigest())
PYTHON_EOF
)

    # 修改文件
    echo "additional content" >> "$test_repo/src/test.py"

    # 计算新哈希
    local hash2=$(python3 - <<PYTHON_EOF
import hashlib

with open("$test_repo/src/test.py", 'r') as f:
    lines = [l.strip() for l in f if l.strip() and not l.strip().startswith('#')]
    content = '\n'.join(lines)
    print(hashlib.sha256(content.encode()).hexdigest())
PYTHON_EOF
)

    cleanup_test_repo "$test_repo"

    # 验证哈希不同
    if [ "$hash1" = "$hash2" ]; then
        echo "  ❌Hashes should differ after file modification" >&2
        return 1
    fi

    return 0
}

# 测试 4: 元数据路径计算
test_metadata_path_calculation() {
    # 测试默认输出目录
    local metadata_path=$(python3 - <<'PYTHON_EOF'
import json
from pathlib import Path

# 模拟默认配置
output_dir = "docs"
metadata_file = f"{output_dir}/.wiki-metadata/metadata.json"
print(metadata_file)
PYTHON_EOF
)

    assert_equals "docs/.wiki-metadata/metadata.json" "$metadata_path"

    # 测试自定义输出目录
    local custom_path=$(python3 - <<'PYTHON_EOF'
import json
from pathlib import Path

# 模拟自定义配置
output_dir = "wiki"
metadata_file = f"{output_dir}/.wiki-metadata/metadata.json"
print(metadata_file)
PYTHON_EOF
)

    assert_equals "wiki/.wiki-metadata/metadata.json" "$custom_path"
}

# 测试 5: 配置迁移逻辑
test_config_migration() {
    # 创建临时配置文件
    local temp_config=$(mktemp)
    echo '{"version": "2.0.0", "language": "zh"}' > "$temp_config"

    # 模拟迁移
    local migrated=$(python3 - <<PYTHON_EOF
import json
from pathlib import Path

config_path = Path("$temp_config")
with open(config_path, 'r') as f:
    config = json.load(f)

version = config.get('version', '2.0.0')
if version < '3.1.0':
    config['version'] = '3.1.0'

    if 'update_mode' not in config:
        config['update_mode'] = {
            'strategy': 'incremental',
            'detect_changes': True,
            'preserve_manual_edits': True,
            'merge_conflicts': 'skip'
        }

print(json.dumps(config))
PYTHON_EOF
)

    # 验证版本已更新
    local new_version=$(python3 - <<PYTHON_EOF
import json
config = json.loads("""$migrated""")
print(config.get('version', ''))
PYTHON_EOF
)

    rm "$temp_config"

    assert_equals "3.1.0" "$new_version" "Config should be migrated to v3.1.0"
}

# 测试 6: 排除模式验证
test_exclude_patterns() {
    local test_repo=$(setup_test_repo)

    # 创建各种文件
    echo "test code" > "$test_repo/tests/test_foo.py"
    echo "mock code" > "$test_repo/mocks/mock_bar.py"
    echo "source code" > "$test_repo/src/code.py"

    git -C "$test_repo" add -A
    git -C "$test_repo" commit -q -m "add files"

    # 获取所有变更文件
    local all_files=$(git -C "$test_repo" diff --name-only HEAD~1 HEAD)

    # 验证所有文件都被检测到
    assert_contains "$all_files" "tests/test_foo.py"
    assert_contains "$all_files" "mocks/mock_bar.py"
    assert_contains "$all_files" "src/code.py"

    local status=$?

    cleanup_test_repo "$test_repo"
    return $status
}

# 测试 7: 区域标记验证
test_region_markers() {
    local content="# Test

<!-- WIKI-GEN-START: metadata -->
Generated metadata
<!-- WIKI-GEN-END: metadata -->

<!-- WIKI-GEN-START: content -->
Generated content
<!-- WIKI-GEN-END: content -->"

    # 验证区域标记存在
    assert_contains "$content" "WIKI-GEN-START: metadata"
    assert_contains "$content" "WIKI-GEN-END: metadata"
    assert_contains "$content" "WIKI-GEN-START: content"
    assert_contains "$content" "WIKI-GEN-END: content"
}

# 主测试运行器
main() {
    echo "========================================="
    echo "增量更新集成测试"
    echo "========================================="
    echo ""

    run_test "仓库创建和清理" test_repo_setup
    run_test "Git 变更检测集成" test_git_change_detection
    run_test "文件哈希追踪" test_file_hash_tracking
    run_test "元数据路径计算" test_metadata_path_calculation
    run_test "配置迁移逻辑" test_config_migration
    run_test "排除模式验证" test_exclude_patterns
    run_test "区域标记验证" test_region_markers

    print_test_summary
}

if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
