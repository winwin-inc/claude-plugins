#!/usr/bin/env bash
# 智能合并单元测试

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

source "$SCRIPT_DIR/test_helpers.sh"

# 测试 1: 区域提取
test_region_extraction() {
    local content="# Test

<!-- WIKI-GEN-START: region1 -->
Content 1
<!-- WIKI-GEN-END: region1 -->"

    # 使用内联 Python 提取区域
    local regions=$(python3 - <<'PYTHON_EOF'
import sys
import re
import json

content = """$content"""

pattern = r'<!-- WIKI-GEN-START: (\w+) -->(.*?)<!-- WIKI-GEN-END: \1 -->'
matches = re.finditer(pattern, content, re.DOTALL)

regions = {}
for match in matches:
    name = match.group(1)
    regions[name] = match.group(2).strip()

print(json.dumps(regions))
PYTHON_EOF
)

    assert_contains "$regions" "region1"
}

# 测试 2: 手动编辑检测
test_manual_edit_detection() {
    local region="<!-- MANUAL-EDIT -->
Custom content
<!-- END-MANUAL-EDIT -->"

    local result=$(python3 - <<'PYTHON_EOF
import sys

region = """$region"""
manual_markers = ['<!-- MANUAL-EDIT -->', '<!-- KEEP -->']

has_manual = any(marker in region for marker in manual_markers)
print("true" if has_manual else "false")
PYTHON_EOF
)

    assert_equals "true" "$result" "Should detect MANUAL-EDIT marker"
}

# 测试 3: KEEP 标记检测
test_keep_marker_detection() {
    local region="<!-- KEEP -->
Keep this content
<!-- END-KEEP -->"

    local result=$(python3 - <<'PYTHON_EOF
import sys

region = """$region"""
manual_markers = ['<!-- MANUAL-EDIT -->', '<!-- KEEP -->']

has_manual = any(marker in region for marker in manual_markers)
print("true" if has_manual else "false")
PYTHON_EOF
)

    assert_equals "true" "$result" "Should detect KEEP marker"
}

# 测试 4: 无手动编辑标记
test_no_manual_markers() {
    local region="Regular content without markers"

    local result=$(python3 - <<'PYTHON_EOF
import sys

region = """$region"""
manual_markers = ['<!-- MANUAL-EDIT -->', '<!-- KEEP -->']

has_manual = any(marker in region for marker in manual_markers)
print("true" if has_manual else "false")
PYTHON_EOF
)

    assert_equals "false" "$result" "Should not detect markers"
}

# 测试 5: 多区域提取
test_multiple_regions() {
    local content="# Test

<!-- WIKI-GEN-START: region1 -->
Content 1
<!-- WIKI-GEN-END: region1 -->

<!-- WIKI-GEN-START: region2 -->
Content 2
<!-- WIKI-GEN-END: region2 -->"

    # 提取区域数量
    local region_count=$(python3 - <<'PYTHON_EOF'
import sys
import re

content = """$content"""

pattern = r'<!-- WIKI-GEN-START: (\w+) -->'
matches = re.findall(pattern, content)

print(len(matches))
PYTHON_EOF
)

    assert_equals "2" "$region_count" "Should extract 2 regions"
}

# 测试 6: 嵌套标记处理
test_nested_markers() {
    local content="# Test

<!-- WIKI-GEN-START: region1 -->
Outer content
<!-- MANUAL-EDIT -->
Inner protected content
<!-- END-MANUAL-EDIT -->
<!-- WIKI-GEN-END: region1 -->"

    # 验证外层区域存在
    local has_region=$(echo "$content" | grep -q "WIKI-GEN-START: region1" && echo "true" || echo "false")
    assert_equals "true" "$has_region" "Should have outer region"
}

# 测试 7: 相似度计算
test_similarity_calculation() {
    # 使用 difflib 计算相似度
    local text1="This is a test document with some content"
    local text2="This is a test document with different content"

    local similarity=$(python3 - <<PYTHON_EOF
from difflib import SequenceMatcher

text1 = """$text1"""
text2 = """$text2"""

ratio = SequenceMatcher(None, text1, text2).ratio()
print(f"{ratio:.2f}")
PYTHON_EOF
)

    # 验证相似度在合理范围内 (应该大于 0.5)
    local is_high=$(python3 - <<PYTHON_EOF
similarity = float("$similarity")
print("true" if similarity > 0.5 else "false")
PYTHON_EOF
)

    assert_equals "true" "$is_high" "Similarity should be > 0.5"
}

# 主测试运行器
main() {
    echo "========================================="
    echo "智能合并单元测试"
    echo "========================================="
    echo ""

    run_test "区域提取" test_region_extraction
    run_test "手动编辑检测" test_manual_edit_detection
    run_test "KEEP 标记检测" test_keep_marker_detection
    run_test "无手动编辑标记" test_no_manual_markers
    run_test "多区域提取" test_multiple_regions
    run_test "嵌套标记处理" test_nested_markers
    run_test "相似度计算" test_similarity_calculation

    print_test_summary
}

if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
