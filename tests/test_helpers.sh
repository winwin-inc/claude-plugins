#!/usr/bin/env bash
# 测试辅助函数库
# 用法: source tests/test_helpers.sh

# 测试计数器
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 创建临时测试仓库
setup_test_repo() {
    local temp_dir=$(mktemp -d)
    cd "$temp_dir"
    git init -q
    git config user.email "test@example.com"
    git config user.name "Test User"

    # 创建基础文件结构
    mkdir -p src/models src/services tests
    echo "# Test Project" > README.md
    git add -A
    git commit -q -m "Initial commit"

    echo "$temp_dir"
}

# 清理测试仓库
cleanup_test_repo() {
    local test_repo=$1
    if [ -d "$test_repo" ]; then
        rm -rf "$test_repo"
    fi
}

# 创建测试文件
create_test_file() {
    local content=$1
    local test_file=$(mktemp)
    echo "$content" > "$test_file"
    echo "$test_file"
}

# 断言函数
assert_equals() {
    local expected=$1
    local actual=$2
    local message=${3:-"Expected '$expected', got '$actual'"}

    if [ "$expected" = "$actual" ]; then
        return 0
    else
        echo "  ❌Assertion failed: $message" >&2
        return 1
    fi
}

assert_contains() {
    local haystack=$1
    local needle=$2
    local message=${3:-"Expected '$haystack' to contain '$needle'"}

    if echo "$haystack" | grep -qF "$needle"; then
        return 0
    else
        echo "  ❌Assertion failed: $message" >&2
        return 1
    fi
}

assert_not_empty() {
    local value=$1
    local message=${2:-"Expected non-empty value"}

    if [ -n "$value" ]; then
        return 0
    else
        echo "  ❌Assertion failed: $message" >&2
        return 1
    fi
}

assert_json_key() {
    local json=$1
    local key=$2
    local expected=$3

    # 使用内联 Python 提取 JSON 键值
    local actual=$(python3 - <<PYTHON_EOF
import json
import sys

try:
    data = json.loads("""$json""")
    value = data.get("$key", "")

    # 处理嵌套键 (如 "metadata.version")
    keys = "$key".split(".")
    value = data
    for k in keys:
        value = value.get(k, "")

    print(value)
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_EOF
)

    assert_equals "$expected" "$actual" "JSON key '$key' should be '$expected', got '$actual'"
}

# 测试运行器
run_test() {
    local test_name=$1
    local test_function=$2

    ((TESTS_RUN++))

    echo -n "  $test_name ... "

    if $test_function; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

# 打印测试摘要
print_test_summary() {
    echo ""
    echo "========================================="
    echo "测试摘要"
    echo "========================================="
    echo "总计:   $TESTS_RUN"
    echo -e "通过:   ${GREEN}$TESTS_PASSED${NC}"
    echo -e "失败:   ${RED}$TESTS_FAILED${NC}"
    echo "========================================="

    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}所有测试通过！${NC}"
        return 0
    else
        echo -e "${RED}有测试失败${NC}"
        return 1
    fi
}
