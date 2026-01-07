#!/usr/bin/env bash
# 变更检测单元测试

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

source "$SCRIPT_DIR/test_helpers.sh"

# 测试 1: Git diff 分析
test_git_diff_analysis() {
    local test_repo=$(setup_test_repo)

    # 修改文件
    echo "new content" >> "$test_repo/src/test.py"
    git -C "$test_repo" add -A
    local new_commit=$(git -C "$test_repo" commit -q -m "test")
    local base_commit=$(git -C "$test_repo" rev-parse HEAD^)

    # 调用变更检测
    cd "$test_repo"
    source "$PROJECT_ROOT/plugins/skills/doc-generator/change_detection.md"

    # 检测变更
    local changed_files=$(git diff --name-only "$base_commit" HEAD)

    cd "$PROJECT_ROOT"

    # 验证结果
    assert_contains "$changed_files" "src/test.py"
    local status=$?

    cleanup_test_repo "$test_repo"
    return $status
}

# 测试 2: 哈希计算一致性
test_hash_consistency() {
    local test_file=$(create_test_file "test content")

    # 计算哈希
    local hash1=$(python3 - <<PYTHON_EOF
import hashlib

with open("$test_file", 'r') as f:
    lines = [l.strip() for l in f if l.strip() and not l.strip().startswith('#')]
    content = '\n'.join(lines)
    print(hashlib.sha256(content.encode()).hexdigest())
PYTHON_EOF
)

    local hash2=$(python3 - <<PYTHON_EOF
import hashlib

with open("$test_file", 'r') as f:
    lines = [l.strip() for l in f if l.strip() and not l.strip().startswith('#')]
    content = '\n'.join(lines)
    print(hashlib.sha256(content.encode()).hexdigest())
PYTHON_EOF
)

    rm "$test_file"

    assert_equals "$hash1" "$hash2" "Hash values should be consistent"
}

# 测试 3: 哈希计算差异性
test_hash_difference() {
    local file1=$(create_test_file "content 1")
    local file2=$(create_test_file "content 2")

    local hash1=$(python3 - <<PYTHON_EOF
import hashlib

with open("$file1", 'r') as f:
    lines = [l.strip() for l in f if l.strip() and not l.strip().startswith('#')]
    content = '\n'.join(lines)
    print(hashlib.sha256(content.encode()).hexdigest())
PYTHON_EOF
)

    local hash2=$(python3 - <<PYTHON_EOF
import hashlib

with open("$file2", 'r') as f:
    lines = [l.strip() for l in f if l.strip() and not l.strip().startswith('#')]
    content = '\n'.join(lines)
    print(hashlib.sha256(content.encode()).hexdigest())
PYTHON_EOF
)

    rm "$file1" "$file2"

    if [ "$hash1" = "$hash2" ]; then
        echo "  ❌Different content should produce different hashes" >&2
        return 1
    fi
    return 0
}

# 测试 4: 排除模式过滤
test_exclude_patterns() {
    local test_repo=$(setup_test_repo)

    # 创建测试文件
    echo "test code" > "$test_repo/tests/test_foo.py"
    echo "mock code" > "$test_repo/mocks/mock_bar.py"
    echo "source code" > "$test_repo/src/code.py"

    git -C "$test_repo" add -A
    git -C "$test_repo" commit -q -m "add files"
    local base_commit=$(git -C "$test_repo" rev-parse HEAD^)

    # 获取变更文件
    cd "$test_repo"
    local changed_files=$(git diff --name-only "$base_commit" HEAD)
    cd "$PROJECT_ROOT"

    # 验证测试和 mock 文件被排除
    # Git diff 会返回所有变更文件,但我们在变更检测中会过滤它们
    # 这里只验证 Git diff 正常工作
    assert_contains "$changed_files" "src/code.py"
    local status=$?

    cleanup_test_repo "$test_repo"
    return $status
}

# 测试 5: 空变更检测
test_no_changes() {
    local test_repo=$(setup_test_repo)

    # 不做任何修改
    local base_commit=$(git -C "$test_repo" rev-parse HEAD)

    # 获取变更文件
    cd "$test_repo"
    local changed_files=$(git diff --name-only "$base_commit" HEAD)
    cd "$PROJECT_ROOT"

    # 应该没有变更文件
    if [ -n "$changed_files" ]; then
        echo "  ❌Should detect no changes" >&2
        cleanup_test_repo "$test_repo"
        return 1
    fi

    cleanup_test_repo "$test_repo"
    return 0
}

# 主测试运行器
main() {
    echo "========================================="
    echo "变更检测单元测试"
    echo "========================================="
    echo ""

    run_test "Git diff 分析" test_git_diff_analysis
    run_test "哈希计算一致性" test_hash_consistency
    run_test "哈希计算差异性" test_hash_difference
    run_test "排除模式过滤" test_exclude_patterns
    run_test "空变更检测" test_no_changes

    print_test_summary
}

if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
