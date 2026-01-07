#!/usr/bin/env bash
# 配置解析库单元测试
# 版本: 1.0.0

# 设置测试环境
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$TEST_DIR/.." && pwd)"

# 导入被测试的库
source "$PROJECT_ROOT/plugins/libs/config_resolver.sh"

# 测试辅助函数
setup_test_env() {
    local test_dir="$1"
    mkdir -p "$test_dir"
    cd "$test_dir"
}

cleanup_test_env() {
    local test_dir="$1"
    rm -rf "$test_dir"
}

# 测试计数器
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# 断言函数
assert_equals() {
    local expected="$1"
    local actual="$2"
    local message="${3:-断言失败}"

    if [ "$expected" = "$actual" ]; then
        echo "  ✅ PASS: $message"
        ((TESTS_PASSED++))
    else
        echo "  ❌ FAIL: $message"
        echo "     期望: $expected"
        echo "     实际: $actual"
        ((TESTS_FAILED++))
    fi
    ((TESTS_RUN++))
}

assert_file_exists() {
    local file="$1"
    local message="${2:-文件应该存在}"

    if [ -f "$file" ]; then
        echo "  ✅ PASS: $message ($file)"
        ((TESTS_PASSED++))
    else
        echo "  ❌ FAIL: $message ($file)"
        ((TESTS_FAILED++))
    fi
    ((TESTS_RUN++))
}

assert_file_not_exists() {
    local file="$1"
    local message="${2:-文件不应该存在}"

    if [ ! -f "$file" ]; then
        echo "  ✅ PASS: $message ($file)"
        ((TESTS_PASSED++))
    else
        echo "  ❌ FAIL: $message ($file)"
        ((TESTS_FAILED++))
    fi
    ((TESTS_RUN++))
}

# 测试 1: find_config_file - 环境变量优先级（有效文件）
test_find_config_env_var_priority() {
    echo "🧪 测试 1: find_config_file - 环境变量优先级（有效文件）"

    local test_dir="/tmp/test_config_env_$$"
    setup_test_env "$test_dir"

    # 创建默认位置的配置文件
    mkdir -p docs
    echo '{"output_dir": "docs"}' > docs/wiki-config.json

    # 创建自定义位置的配置文件
    mkdir -p custom
    echo '{"output_dir": "custom"}' > custom/config.json

    # 设置环境变量指向存在的文件
    export WIKI_CONFIG="$test_dir/custom/config.json"

    # 测试：应该返回环境变量指定的文件
    local result=$(find_config_file)
    assert_equals "$test_dir/custom/config.json" "$result" "应优先使用环境变量指定的文件"

    cleanup_test_env "$test_dir"
    unset WIKI_CONFIG
    echo ""
}

# 测试 2: find_config_file - 默认位置查找
test_find_config_default_location() {
    echo "🧪 测试 2: find_config_file - 默认位置查找"

    local test_dir="/tmp/test_config_default_$$"
    setup_test_env "$test_dir"

    # 创建默认位置的配置文件
    mkdir -p docs
    echo '{"output_dir": "docs"}' > docs/wiki-config.json

    # 测试：应该找到默认位置的配置文件
    local result=$(find_config_file)
    assert_equals "docs/wiki-config.json" "$result" "应找到默认位置的配置文件"

    cleanup_test_env "$test_dir"
    echo ""
}

# 测试 3: find_config_file - 自定义 output_dir 查找
test_find_config_custom_output_dir() {
    echo "🧪 测试 3: find_config_file - 自定义 output_dir 查找"

    local test_dir="/tmp/test_config_custom_$$"
    setup_test_env "$test_dir"

    # 创建自定义位置的配置文件
    mkdir -p documentation
    echo '{"output_dir": "documentation"}' > documentation/wiki-config.json

    # 测试：应该找到自定义位置的配置文件
    local result=$(find_config_file "documentation")
    assert_equals "documentation/wiki-config.json" "$result" "应找到自定义位置的配置文件"

    cleanup_test_env "$test_dir"
    echo ""
}

# 测试 4: find_config_file - 未找到配置文件
test_find_config_not_found() {
    echo "🧪 测试 4: find_config_file - 未找到配置文件"

    local test_dir="/tmp/test_config_notfound_$$"
    setup_test_env "$test_dir"

    # 不创建任何配置文件

    # 测试：应该返回空
    local result=$(find_config_file)
    assert_equals "" "$result" "未找到配置文件应返回空"

    cleanup_test_env "$test_dir"
    echo ""
}

# 测试 5: init_config_file - 创建配置文件到默认位置
test_init_config_default_location() {
    echo "🧪 测试 5: init_config_file - 创建配置文件到默认位置"

    local test_dir="/tmp/test_init_default_$$"
    setup_test_env "$test_dir"

    # 初始化配置文件
    local result=$(init_config_file)

    # 验证：文件应该创建
    assert_file_exists "docs/wiki-config.json" "配置文件应创建到默认位置"

    # 验证：返回值应该是正确的路径
    assert_equals "docs/wiki-config.json" "$result" "应返回配置文件路径"

    cleanup_test_env "$test_dir"
    echo ""
}

# 测试 6: init_config_file - 创建配置文件到自定义位置
test_init_config_custom_location() {
    echo "🧪 测试 6: init_config_file - 创建配置文件到自定义位置"

    local test_dir="/tmp/test_init_custom_$$"
    setup_test_env "$test_dir"

    # 初始化配置文件到自定义位置
    local result=$(init_config_file "wiki")

    # 验证：文件应该创建
    assert_file_exists "wiki/wiki-config.json" "配置文件应创建到自定义位置"

    # 验证：返回值应该是正确的路径
    assert_equals "wiki/wiki-config.json" "$result" "应返回配置文件路径"

    cleanup_test_env "$test_dir"
    echo ""
}

# 测试 7: init_config_file - 配置文件已存在
test_init_config_already_exists() {
    echo "🧪 测试 7: init_config_file - 配置文件已存在"

    local test_dir="/tmp/test_init_exists_$$"
    setup_test_env "$test_dir"

    # 创建配置文件
    mkdir -p docs
    echo '{"old": true}' > docs/wiki-config.json

    # 初始化配置文件
    local result=$(init_config_file)

    # 验证：旧文件应该保留
    local content=$(cat docs/wiki-config.json)
    if [[ "$content" == *"old"* ]]; then
        echo "  ✅ PASS: 已存在的配置文件应保留"
        ((TESTS_PASSED++))
    else
        echo "  ❌ FAIL: 已存在的配置文件被覆盖"
        ((TESTS_FAILED++))
    fi
    ((TESTS_RUN++))

    cleanup_test_env "$test_dir"
    echo ""
}

# 测试 8: validate_config - 验证有效配置
test_validate_config_valid() {
    echo "🧪 测试 8: validate_config - 验证有效配置"

    local test_dir="/tmp/test_validate_valid_$$"
    setup_test_env "$test_dir"

    # 创建有效配置文件
    mkdir -p docs
    echo '{"output_dir": "docs", "version": "3.1.0"}' > docs/wiki-config.json

    export WIKI_CONFIG="$test_dir/docs/wiki-config.json"

    # 验证配置文件
    if validate_config >/dev/null 2>&1; then
        echo "  ✅ PASS: 有效配置文件应验证通过"
        ((TESTS_PASSED++))
    else
        echo "  ❌ FAIL: 有效配置文件验证失败"
        ((TESTS_FAILED++))
    fi
    ((TESTS_RUN++))

    cleanup_test_env "$test_dir"
    unset WIKI_CONFIG
    echo ""
}

# 测试 9: validate_config - 验证无效 JSON
test_validate_config_invalid_json() {
    echo "🧪 测试 9: validate_config - 验证无效 JSON"

    local test_dir="/tmp/test_validate_invalid_$$"
    setup_test_env "$test_dir"

    # 创建无效的 JSON 文件
    mkdir -p docs
    echo '{invalid json}' > docs/wiki-config.json

    export WIKI_CONFIG="$test_dir/docs/wiki-config.json"

    # 验证配置文件
    if ! validate_config >/dev/null 2>&1; then
        echo "  ✅ PASS: 无效 JSON 应验证失败"
        ((TESTS_PASSED++))
    else
        echo "  ❌ FAIL: 无效 JSON 验证通过（应该失败）"
        ((TESTS_FAILED++))
    fi
    ((TESTS_RUN++))

    cleanup_test_env "$test_dir"
    unset WIKI_CONFIG
    echo ""
}

# 测试 10: validate_config - 配置文件不存在
test_validate_config_not_exists() {
    echo "🧪 测试 10: validate_config - 配置文件不存在"

    export WIKI_CONFIG="/nonexistent/config.json"

    # 验证配置文件
    if ! validate_config >/dev/null 2>&1; then
        echo "  ✅ PASS: 不存在的配置文件应验证失败"
        ((TESTS_PASSED++))
    else
        echo "  ❌ FAIL: 不存在的配置文件验证通过（应该失败）"
        ((TESTS_FAILED++))
    fi
    ((TESTS_RUN++))

    unset WIKI_CONFIG
    echo ""
}

# 主测试运行器
main() {
    echo "========================================"
    echo "配置解析库单元测试"
    echo "========================================"
    echo ""

    # 运行所有测试
    test_find_config_env_var_priority
    test_find_config_default_location
    test_find_config_custom_output_dir
    test_find_config_not_found
    test_init_config_default_location
    test_init_config_custom_location
    test_init_config_already_exists
    test_validate_config_valid
    test_validate_config_invalid_json
    test_validate_config_not_exists

    # 输出测试结果
    echo "========================================"
    echo "测试结果汇总"
    echo "========================================"
    echo "总计: $TESTS_RUN 个测试"
    echo "通过: $TESTS_PASSED 个 ✅"
    echo "失败: $TESTS_FAILED 个 ❌"
    echo ""

    if [ $TESTS_FAILED -eq 0 ]; then
        echo "🎉 所有测试通过！"
        return 0
    else
        echo "⚠️  有测试失败，请检查"
        return 1
    fi
}

# 运行测试
main "$@"
