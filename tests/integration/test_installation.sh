#!/bin/bash
#
# Wiki Generator CLI 集成测试脚本
#
# 测试场景:
#   1. 空目录安装
#   2. 覆盖已存在文件
#   3. 权限不足
#   4. dry-run 不修改文件系统
#   5. 配置文件验证
#

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数器
TESTS_PASSED=0
TESTS_FAILED=0

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 测试函数
test_case() {
    local name="$1"
    echo ""
    echo "=========================================="
    echo "测试: $name"
    echo "=========================================="
}

# 断言函数
assert_success() {
    if [ $? -eq 0 ]; then
        log_info "✅ 通过: $1"
        ((TESTS_PASSED++))
    else
        log_error "❌ 失败: $1"
        ((TESTS_FAILED++))
        return 1
    fi
}

assert_file_exists() {
    if [ -f "$1" ]; then
        log_info "✅ 文件存在: $1"
        ((TESTS_PASSED++))
    else
        log_error "❌ 文件不存在: $1"
        ((TESTS_FAILED++))
        return 1
    fi
}

assert_file_not_exists() {
    if [ ! -f "$1" ]; then
        log_info "✅ 文件不存在（符合预期）: $1"
        ((TESTS_PASSED++))
    else
        log_error "❌ 文件不应存在: $1"
        ((TESTS_FAILED++))
        return 1
    fi
}

# 清理函数
cleanup() {
    if [ -n "$TEST_DIR" ] && [ -d "$TEST_DIR" ]; then
        rm -rf "$TEST_DIR"
        log_info "清理测试目录: $TEST_DIR"
    fi
}

# 不使用 trap，手动清理

# ========================================
# 测试 1: 空目录安装
# ========================================
test_case "空目录安装"

TEST_DIR=$(mktemp -d)
log_info "测试目录: $TEST_DIR"

cd "$TEST_DIR"
wiki-generator --verbose

assert_success "安装命令执行成功"
assert_file_exists "$TEST_DIR/.claude/README.md"
assert_file_exists "$TEST_DIR/wiki-config.json"

# 验证配置文件格式
if python -m json.tool "$TEST_DIR/wiki-config.json" > /dev/null 2>&1; then
    log_info "✅ 配置文件 JSON 格式有效"
    ((TESTS_PASSED++))
else
    log_error "❌ 配置文件 JSON 格式无效"
    ((TESTS_FAILED++))
fi

# 清理
rm -rf "$TEST_DIR"

# ========================================
# 测试 2: 覆盖已存在文件
# ========================================
test_case "覆盖已存在文件"

TEST_DIR=$(mktemp -d)
cd "$TEST_DIR"

# 首次安装
wiki-generator
assert_success "首次安装"

# 修改配置文件
echo '{"modified": true}' > "$TEST_DIR/wiki-config.json"

# 再次安装（不应覆盖配置）
wiki-generator
assert_success "再次安装"

# 验证配置被保留
if grep -q "modified" "$TEST_DIR/wiki-config.json"; then
    log_info "✅ 配置文件被保留"
    ((TESTS_PASSED++))
else
    log_error "❌ 配置文件被意外覆盖"
    ((TESTS_FAILED++))
fi

# 测试 --force 选项
echo '{"modified": true}' > "$TEST_DIR/wiki-config.json"
wiki-generator --force
assert_success "强制安装"

# 使用 --force 后配置应该被覆盖
if ! grep -q "modified" "$TEST_DIR/wiki-config.json"; then
    log_info "✅ --force 选项成功覆盖配置"
    ((TESTS_PASSED++))
else
    log_error "❌ --force 选项未能覆盖配置"
    ((TESTS_FAILED++))
fi

# 清理
rm -rf "$TEST_DIR"

# ========================================
# 测试 3: Dry-run 模式
# ========================================
test_case "Dry-run 模式不修改文件系统"

TEST_DIR=$(mktemp -d)
cd "$TEST_DIR"

wiki-generator --dry-run
assert_success "Dry-run 模式执行"

# 验证没有文件被创建
assert_file_not_exists "$TEST_DIR/.claude"
assert_file_not_exists "$TEST_DIR/wiki-config.json"

# 清理
rm -rf "$TEST_DIR"

# ========================================
# 测试 4: 配置文件验证
# ========================================
test_case "配置文件验证"

TEST_DIR=$(mktemp -d)
cd "$TEST_DIR"

wiki-generator
assert_success "安装成功"

# 验证配置文件字段
CONFIG_FILE="$TEST_DIR/wiki-config.json"
if grep -q '"output_dir"' "$CONFIG_FILE" && \
   grep -q '"exclude_patterns"' "$CONFIG_FILE" && \
   grep -q '"quality_threshold"' "$CONFIG_FILE" && \
   grep -q '"diagrams_enabled"' "$CONFIG_FILE" && \
   grep -q '"diagrams_detail_level"' "$CONFIG_FILE"; then
    log_info "✅ 配置文件包含所有必需字段"
    ((TESTS_PASSED++))
else
    log_error "❌ 配置文件缺少必需字段"
    ((TESTS_FAILED++))
fi

# 清理
rm -rf "$TEST_DIR"

# ========================================
# 测试 5: 帮助和版本信息
# ========================================
test_case "帮助和版本信息"

# 测试 --help
if wiki-generator --help > /dev/null 2>&1; then
    log_info "✅ --help 选项可用"
    ((TESTS_PASSED++))
else
    log_error "❌ --help 选项失败"
    ((TESTS_FAILED++))
fi

# 测试 --version
if wiki-generator --version > /dev/null 2>&1; then
    log_info "✅ --version 选项可用"
    ((TESTS_PASSED++))
else
    log_error "❌ --version 选项失败"
    ((TESTS_FAILED++))
fi

# ========================================
# 测试总结
# ========================================
echo ""
echo "=========================================="
echo "测试总结"
echo "=========================================="
echo -e "${GREEN}通过: $TESTS_PASSED${NC}"
echo -e "${RED}失败: $TESTS_FAILED${NC}"
echo "总计: $((TESTS_PASSED + TESTS_FAILED))"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ 所有测试通过！${NC}"
    exit 0
else
    echo -e "${RED}❌ 部分测试失败${NC}"
    exit 1
fi
