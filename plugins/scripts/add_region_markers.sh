#!/usr/bin/env bash
# 批量为模板添加区域标记
# 用法: ./plugins/scripts/add_region_markers.sh [template_file]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}ℹ${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# 检查是否已包含区域标记
has_region_markers() {
    local file=$1
    grep -q "<!-- WIKI-GEN-START:" "$file"
}

# 为模板添加区域标记
add_markers_to_template() {
    local template_file=$1
    local backup_file="${template_file}.backup"

    # 跳过已处理的文件
    if has_region_markers "$template_file"; then
        log_info "跳过（已包含标记）: $template_file"
        return 0
    fi

    log_info "处理: $template_file"

    # 备份原文件
    cp "$template_file" "$backup_file"

    # 使用 Python 处理模板
    python3 - "$template_file" <<'PYTHON_EOF'
import sys
import re
from pathlib import Path

template_file = Path(sys.argv[1])

with open(template_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 定义需要添加标记的模式
# 格式: (模式, 区域名称)
patterns = [
    # 元数据区域（文件开头）
    (r'^(---\n.*?\n---)\n', 'metadata'),

    # 目录
    (r'(## 目录\n)(.*?)(\n## )', 'toc'),

    # 简介章节
    (r'(## 简介\n)(.*?)(\n\*\*Section sources\*\*)', 'overview'),

    # 常见可配置章节
    (r'(## (.+?)\n)(<!-- Claude:.*?\n)(\{[^}]+\}\n)', None),  # 动态命名区域
]

# 简化处理：只为主要章节添加标记
# 1. 保留原有的 cite 块和元数据
content = re.sub(
    r'(^---\n)',
    r'<!-- WIKI-GEN-START: metadata -->\n\1',
    content,
    flags=re.MULTILINE
)

content = re.sub(
    r'(\n---\n)',
    r'\1\n<!-- WIKI-GEN-END: metadata -->',
    content,
    count=1,
    flags=re.MULTILINE
)

# 2. 添加目录标记
content = re.sub(
    r'(## 目录\n)',
    r'<!-- WIKI-GEN-START: toc -->\n\1',
    content,
    count=1
)

content = re.sub(
    r'(\n## [^\\n]+\n)(?!\s*<!-- WIKI-GEN-END)',
    r'\1<!-- WIKI-GEN-END: toc -->\n',
    content,
    count=1
)

# 3. 为主要章节添加标记（示例）
# 这里需要根据实际模板结构定制

# 写回文件
with open(template_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ 已处理: {template_file.name}")
PYTHON_EOF

    # 如果失败，恢复备份
    if [ $? -ne 0 ]; then
        log_error "处理失败，恢复备份: $template_file"
        mv "$backup_file" "$template_file"
        return 1
    fi

    # 删除备份
    rm "$backup_file"
    log_info "✅ 完成: $template_file"
}

# 主函数
main() {
    local target=${1:-"$PROJECT_ROOT/plugins/templates/wiki-generate"}

    # 检查目录
    if [ ! -d "$target" ]; then
        log_error "目录不存在: $target"
        exit 1
    fi

    log_info "开始批量添加区域标记..."
    log_info "目标目录: $target"

    # 查找所有 .template 文件
    local template_files=$(find "$target" -name "*.template" -type f)

    if [ -z "$template_files" ]; then
        log_warn "未找到模板文件"
        exit 0
    fi

    local count=0
    while IFS= read -r template_file; do
        add_markers_to_template "$template_file"
        ((count++))
    done <<< "$template_files"

    log_info "✅ 处理完成！共处理 $count 个文件"
    log_warn "⚠️  请检查生成的模板，确保区域标记正确"
    log_warn "⚠️  如有问题，可从 .backup 文件恢复"
}

# 如果直接执行脚本
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
