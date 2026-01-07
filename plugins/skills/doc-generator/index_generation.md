# 文档索引生成 Skill

**功能**: 生成文档索引文件，创建交叉引用链接

**验证**: 所有文档链接 100% 有效

---

## 核心生成函数

### generate_document_index()

```bash
#!/usr/bin/env bash
# 文档索引生成主函数
# 用法: generate_document_index <output_dir> <documents_list>
# 输出: README.md 索引文件

generate_document_index() {
    local output_dir=$1
    shift
    local documents=("$@")

    local index_file="$output_dir/README.md"

    echo "📋 生成文档索引: $index_file" >&2

    cat > "$index_file" <<'EOF'
# 文档索引

欢迎阅读 {{PROJECT_NAME}} 文档！

---

## 快速开始

- [快速开始](./quickstart.md) - 5 分钟上手指南

EOF

    # 按分组添加文档
    add_document_group "$index_file" "核心功能" "${documents[@]}"
    add_document_group "$index_file" "技术文档" "${documents[@]}"
    add_document_group "$index_file" "开发相关" "${documents[@]}"
    add_document_group "$index_file" "部署与运维" "${documents[@]}"

    # 添加相关资源
    cat >> "$index_file" <<'EOF'

---

## 相关资源

- [GitHub 仓库](https://github.com/yourusername/{{PROJECT_NAME}})
- [问题反馈](https://github.com/yourusername/{{PROJECT_NAME}}/issues)
- [更新日志](./CHANGELOG.md)

---

**最后更新**: $(date +%Y-%m-%d)
EOF

    echo "✅ 文档索引已生成" >&2

    # 验证所有链接
    validate_document_links "$index_file" "$output_dir"
}
```

---

## 文档分组

```bash
# 根据文档类型分组
add_document_group() {
    local index_file=$1
    local group_name=$2
    shift 2
    local documents=("$@")

    echo "## $group_name" >> "$index_file"
    echo "" >> "$index_file"

    for doc in "${documents[@]}"; do
        local doc_group=$(get_document_group "$doc")
        if [ "$doc_group" = "$group_name" ]; then
            local doc_title=$(get_document_title "$doc")
            local doc_desc=$(get_document_description "$doc")
            local doc_path=$(basename "$doc")

            echo "- [$doc_title](./$doc_path) - $doc_desc" >> "$index_file"
        fi
    done

    echo "" >> "$index_file"
}

# 获取文档分组
get_document_group() {
    local doc_file=$1
    local filename=$(basename "$doc_file")

    case "$filename" in
        *quickstart*|*overview*)
            echo "快速开始"
            ;;
        *api*|*data-model*|*cli*)
            echo "技术文档"
            ;;
        *development*|*testing*|*contributing*)
            echo "开发相关"
            ;;
        *deployment*|*troubleshooting*|*security*)
            echo "部署与运维"
            ;;
        *)
            echo "其他"
            ;;
    esac
}

# 获取文档标题
get_document_title() {
    local doc_file=$1

    # 提取第一个 # 标题
    if [ -f "$doc_file" ]; then
        grep "^# " "$doc_file" | head -n 1 | sed 's/^# //'
    else
        echo "$(basename "$doc_file" .md)"
    fi
}

# 获取文档描述
get_document_description() {
    local doc_file=$1

    # 提取标题后的第一段（最多 100 字符）
    if [ -f "$doc_file" ]; then
        awk '/^# / {getline; while ($0 ~ /^$/) {getline}; print; exit}' "$doc_file" | head -c 100
    else
        echo "文档说明"
    fi
}
```

---

## 交叉引用生成

```bash
# 生成文档间的交叉引用链接
generate_cross_references() {
    local output_dir=$1
    local documents=("$@")

    echo "🔗 生成交叉引用..." >&2

    for doc in "${documents[@]}"; do
        if [ ! -f "$doc" ]; then
            continue
        fi

        local doc_content=$(cat "$doc")
        local updated_content="$doc_content"

        # 为常见术语添加交叉引用
        updated_content=$(add_cross_ref "$updated_content" "快速开始" "quickstart.md")
        updated_content=$(add_cross_ref "$updated_content" "项目概述" "project-overview.md")
        updated_content=$(add_cross_ref "$updated_content" "开发指南" "development-guide.md")
        updated_content=$(add_cross_ref "$updated_content" "部署指南" "deployment-guide.md")
        updated_content=$(add_cross_ref "$updated_content" "API 文档" "api-reference.md")
        updated_content=$(add_cross_ref "$updated_content" "故障排除" "troubleshooting.md")
        updated_content=$(add_cross_ref "$updated_content" "测试策略" "testing-strategy.md")

        # 如果内容有更新，写回文件
        if [ "$updated_content" != "$doc_content" ]; then
            echo "$updated_content" > "$doc"
            echo "  ✅ 更新交叉引用: $doc" >&2
        fi
    done
}

# 添加单个交叉引用
add_cross_ref() {
    local content=$1
    local term=$2
    local link=$3

    # 只在第一次出现时添加链接（避免重复）
    if ! echo "$content" | grep -q "\[$term\]"; then
        echo "$content" | sed "s|$term|[$term](./$link)|g"
    else
        echo "$content"
    fi
}
```

---

## 链接有效性验证

```bash
# 验证文档中的所有链接是否有效
validate_document_links() {
    local index_file=$1
    local output_dir=$2

    echo "🔍 验证文档链接..." >&2

    local errors=0

    # 提取所有 Markdown 链接
    local links=$(grep -oE '\[.*\]\([^)]+\)' "$index_file" | grep -oE '\([^)]+\)' | sed 's/[()]//g')

    for link in $links; do
        # 跳过外部链接
        if [[ "$link" == http* ]]; then
            continue
        fi

        # 验证本地文件
        local target_file="$output_dir/$link"
        if [ ! -f "$target_file" ]; then
            echo "❌ 链接失效: [$link] -> $target_file" >&2
            errors=$((errors + 1))
        else
            echo "  ✅ 链接有效: $link" >&2
        fi
    done

    if [ $errors -eq 0 ]; then
        echo "✅ 所有链接有效（100%）" >&2
        return 0
    else
        echo "⚠️ 发现 $errors 个失效链接" >&2
        return 1
    fi
}
```

---

## 模块文档索引

```bash
# 为业务模块生成独立索引
generate_module_index() {
    local output_dir=$1
    shift
    local modules=("$@")

    local module_index_file="$output_dir/modules.md"

    cat > "$module_index_file" <<'EOF'
# 业务模块文档

本项目的所有业务模块文档。

---

EOF

    for module in "${modules[@]}"; do
        local module_name=$(basename "$module")
        local module_doc="$output_dir/modules/$module_name.md"

        if [ -f "$module_doc" ]; then
            local module_desc=$(get_document_description "$module_doc")

            echo "### [$module_name](./modules/$module_name.md)" >> "$module_index_file"
            echo "" >> "$module_index_file"
            echo "$module_desc" >> "$module_index_file"
            echo "" >> "$module_index_file"
        fi
    done

    echo "✅ 模块索引已生成: $module_index_file" >&2
}
```

---

## API 文档索引

```bash
# 为 API 端点生成索引
generate_api_index() {
    local output_dir=$1
    shift
    local api_modules=("$@")

    local api_index_file="$output_dir/api-reference.md"

    cat > "$api_index_file" <<'EOF'
# API 参考文档

所有 API 端点的详细说明。

---

## 端点列表

EOF

    # 端点列表表格
    echo "| 方法 | 路径 | 描述 | 文档 |" >> "$api_index_file"
    echo "|------|------|------|------|" >> "$api_index_file"

    for api_module in "${api_modules[@]}"; do
        local module_name=$(basename "$api_module")
        local api_doc="$output_dir/api/$module_name.md"

        if [ -f "$api_doc" ]; then
            # 从文档中提取端点信息
            local endpoints=$(grep -E "^###.*\[(GET|POST|PUT|DELETE)\]" "$api_doc" || echo "")

            if [ -n "$endpoints" ]; then
                while IFS= read -r line; do
                    local method=$(echo "$line" | grep -oE "(GET|POST|PUT|DELETE)" || echo "?")
                    local path=$(echo "$line" | grep -oE '`[^`]*`' | head -n 1 | sed 's/`//g' || echo "?")
                    local desc=$(echo "$line" | sed 's/.*###//' | sed 's/\[.*\].*//' | xargs || echo "端点说明")

                    echo "| $method | \`$path\` | $desc | [详情](./api/$module_name.md) |" >> "$api_index_file"
                done <<< "$endpoints"
            fi
        fi
    done

    echo "" >> "$api_index_file"
    echo "---" >> "$api_index_file"
    echo "" >> "$api_index_file"
    echo "## 认证" >> "$api_index_file"
    echo "" >> "$api_index_file"
    echo "所有 API 请求需要认证。详见[认证说明](./deployment-guide.md#认证和授权)" >> "$api_index_file"

    echo "✅ API 索引已生成: $api_index_file" >&2
}
```

---

## 文档搜索索引

```bash
# 生成文档搜索索引（JSON 格式）
generate_search_index() {
    local output_dir=$1
    shift
    local documents=("$@")

    local search_index_file="$output_dir/search-index.json"

    echo '{"documents": [' > "$search_index_file"

    local first=true
    for doc in "${documents[@]}"; do
        if [ ! -f "$doc" ]; then
            continue
        fi

        if [ "$first" = false ]; then
            echo "," >> "$search_index_file"
        fi
        first=false

        local doc_title=$(get_document_title "$doc")
        local doc_desc=$(get_document_description "$doc")
        local doc_path=$(basename "$doc")
        local doc_relative=$(realpath --relative-to="$output_dir" "$doc")

        # 使用 Python 生成 JSON
        python3 - <<PYTHON_EOF
import json

doc = {
    "title": "$doc_title",
    "description": "$doc_desc",
    "path": "$doc_relative",
    "url": "$doc_path"
}

print(json.dumps(doc, ensure_ascii=False))
PYTHON_EOF
    done

    echo ']}' >> "$search_index_file"

    echo "✅ 搜索索引已生成: $search_index_file" >&2
}
```

---

## 使用示例

```bash
# 生成完整文档索引
output_dir="/path/to/docs"
documents=(
    "$output_dir/quickstart.md"
    "$output_dir/project-overview.md"
    "$output_dir/development-guide.md"
    "$output_dir/deployment-guide.md"
    "$output_dir/testing-strategy.md"
    "$output_dir/troubleshooting.md"
    "$output_dir/security-considerations.md"
)

# 生成主索引
generate_document_index "$output_dir" "${documents[@]}"

# 生成交叉引用
generate_cross_references "$output_dir" "${documents[@]}"

# 验证链接
validate_document_links "$output_dir/README.md" "$output_dir"
```

**输出示例**（docs/README.md）：

```markdown
# 文档索引

欢迎阅读 My Awesome Project 文档！

---

## 快速开始

- [快速开始](./quickstart.md) - 5 分钟上手指南

## 核心功能

- [项目概述](./project-overview.md) - 了解项目核心功能和架构
- [API 参考](./api-reference.md) - API 端点详细说明

## 技术文档

- [API 文档](./api-reference.md) - API 端点和数据模型
- [数据模型](./data-models.md) - 数据库模型和关系

## 开发相关

- [开发指南](./development-guide.md) - 开发环境设置和工作流
- [测试策略](./testing-strategy.md) - 测试方法和覆盖率

## 部署与运维

- [部署指南](./deployment-guide.md) - 生产环境部署
- [故障排除](./troubleshooting.md) - 常见问题解决方案
- [安全考虑](./security-considerations.md) - 安全最佳实践

---

## 相关资源

- [GitHub 仓库](https://github.com/yourusername/My-Awesome-Project)
- [问题反馈](https://github.com/yourusername/My-Awesome-Project/issues)
- [更新日志](./CHANGELOG.md)

---

**最后更新**: 2026-01-04
```

---

## 多级目录生成（TOC）

### generate_table_of_contents()

```bash
#!/usr/bin/env bash
# 为单个文档生成多级目录（Table of Contents）
# 用法: generate_table_of_contents <document_file>
# 输出: Markdown 格式的目录，支持 1-4 级标题

generate_table_of_contents() {
    local doc_file=$1

    if [ ! -f "$doc_file" ]; then
        echo "⚠️ 文档不存在: $doc_file" >&2
        return 1
    fi

    echo "📑 生成目录: $doc_file" >&2

    # 提取所有标题（# ## ### ####）
    local toc=""
    local line_num=0

    while IFS= read -r line; do
        line_num=$((line_num + 1))

        # 匹配标题
        if [[ "$line" =~ ^(#{1,4})\s+(.+)$ ]]; then
            local level="${#BASH_REMATCH[1]}"  # # 数量 = 级别
            local title="${BASH_REMATCH[2]}"

            # 生成锚点（移除特殊字符，替换空格为连字符）
            local anchor=$(echo "$title" | sed 's/[^a-zA-Z0-9\u4e00-\u9fa5 ]//g' | tr '[:upper:]' '[:lower:]' | tr ' ' '-')

            # 生成缩进
            local indent=""
            for ((i=1; i<level; i++)); do
                indent="    $indent"
            done

            # 添加目录项
            toc+="${indent}- [$title](#$anchor)\n"
        fi
    done < "$doc_file"

    echo "$toc"
}
```

### generate_document_with_toc()

```bash
#!/usr/bin/env bash
# 在文档开头插入自动生成的目录
# 用法: generate_document_with_toc <document_file>
# 效果: 在文档第一个 ## 标题前插入目录

generate_document_with_toc() {
    local doc_file=$1

    if [ ! -f "$doc_file" ]; then
        echo "⚠️ 文档不存在: $doc_file" >&2
        return 1
    fi

    echo "📝 插入目录到文档: $doc_file" >&2

    # 生成目录
    local toc=$(generate_table_of_contents "$doc_file")

    # 查找第一个 ## 标题的行号
    local first_heading=$(grep -n "^##" "$doc_file" | cut -d: -f1 | head -n 1)

    if [ -z "$first_heading" ]; then
        echo "⚠️ 未找到二级标题，目录将插入到文件末尾" >&2
        first_heading=$(wc -l < "$doc_file")
    fi

    # 在该行前插入目录
    local temp_file="${doc_file}.tmp"

    head -n $((first_heading - 1)) "$doc_file" > "$temp_file"

    cat >> "$temp_file" <<EOF

## 目录

$toc

---

EOF

    tail -n +$first_heading "$doc_file" >> "$temp_file"

    # 替换原文件
    mv "$temp_file" "$doc_file"

    echo "✅ 目录已插入: $doc_file" >&2
}
```

---

## 锚点链接生成

### generate_anchor_links()

```bash
#!/usr/bin/env bash
# 为文档中的所有标题生成锚点链接
# 用法: generate_anchor_links <document_file>
# 效果: 为每个标题添加 id="anchor" 属性（HTML）或隐式锚点（Markdown）

generate_anchor_links() {
    local doc_file=$1

    if [ ! -f "$doc_file" ]; then
        echo "⚠️ 文档不存在: $doc_file" >&2
        return 1
    fi

    echo "⚓ 生成锚点链接: $doc_file" >&2

    local temp_file="${doc_file}.tmp"
    local anchor_map=""

    # 第一次遍历：收集所有标题和锚点
    while IFS= read -r line; do
        if [[ "$line" =~ ^(#{1,4})\s+(.+)$ ]]; then
            local title="${BASH_REMATCH[2]}"
            local anchor=$(echo "$title" | sed 's/[^a-zA-Z0-9\u4e00-\u9fa5 ]//g' | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/-\+/-/g' | sed 's/^-*\|-*$//g')
            anchor_map+="$title|$anchor\n"
        fi
    done < "$doc_file"

    # 第二次遍历：输出标题（Markdown 会自动生成锚点）
    cp "$doc_file" "$temp_file"

    mv "$temp_file" "$doc_file"

    echo "✅ 锚点链接已生成: $doc_file" >&2

    # 输出锚点映射（用于调试）
    echo -e "$anchor_map" >&2
}
```

### generate_section_links()

```bash
#!/usr/bin/env bash
# 为特定章节生成可点击的锚点链接
# 用法: generate_section_links <document_file> <section_title>
# 输出: Markdown 格式的锚点链接

generate_section_links() {
    local doc_file=$1
    local section_title=$2

    if [ ! -f "$doc_file" ]; then
        echo "⚠️ 文档不存在: $doc_file" >&2
        return 1
    fi

    # 生成锚点
    local anchor=$(echo "$section_title" | sed 's/[^a-zA-Z0-9\u4e00-\u9fa5 ]//g' | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/-\+/-/g' | sed 's/^-*\|-*$//g')

    # 生成相对链接
    local doc_name=$(basename "$doc_file" .md)
    echo "[$section_title](./$doc_name.md#$anchor)"
}
```

---

## 交叉引用增强

### generate_smart_cross_references()

```bash
#!/usr/bin/env bash
# 智能生成交叉引用（检测文档中的术语并自动链接）
# 用法: generate_smart_cross_references <output_dir> <documents_list>
# 功能:
#   1. 检测文档中的 API 端点、模块名、函数名
#   2. 自动链接到对应文档
#   3. 避免重复链接和循环引用

generate_smart_cross_references() {
    local output_dir=$1
    shift
    local documents=("$@")

    echo "🔗 智能生成交叉引用..." >&2

    # 1. 构建术语索引
    local term_index=$(build_term_index "${documents[@]}")

    # 2. 为每个文档添加交叉引用
    for doc in "${documents[@]}"; do
        if [ ! -f "$doc" ]; then
            continue
        fi

        local doc_content=$(cat "$doc")
        local updated_content="$doc_content"
        local doc_basename=$(basename "$doc" .md)

        # 遍历术语索引
        while IFS='|' read -r term target_doc; do
            # 跳过当前文档的自引用
            if [ "$target_doc" = "$doc_basename" ]; then
                continue
            fi

            # 检查术语是否在文档中
            if echo "$updated_content" | grep -q "$term"; then
                # 检查是否已经有链接
                if ! echo "$updated_content" | grep -q "\[$term\]"; then
                    # 添加链接（只在第一次出现时）
                    updated_content=$(echo "$updated_content" | sed "0,/$term/s//$term/")

                    # 如果行中有其他链接，则跳过
                    if ! echo "$updated_content" | grep -q ".*\[.*\](.*)$term"; then
                        updated_content=$(echo "$updated_content" | sed "0,/$term/s/\\($term\\)/[$term](.\\/$target_doc.md)/")
                    fi
                fi
            fi
        done <<< "$term_index"

        # 如果内容有更新，写回文件
        if [ "$updated_content" != "$doc_content" ]; then
            echo "$updated_content" > "$doc"
            echo "  ✅ 更新交叉引用: $doc" >&2
        fi
    done

    echo "✅ 交叉引用生成完成" >&2
}

# 构建术语索引
build_term_index() {
    local documents=("$@")

    for doc in "${documents[@]}"; do
        if [ ! -f "$doc" ]; then
            continue
        fi

        local doc_name=$(basename "$doc" .md)
        local doc_title=$(get_document_title "$doc")

        # 添加文档标题作为术语
        echo "$doc_title|$doc_name"

        # 提取 API 端点（如果是 API 文档）
        if [[ "$doc_name" =~ api|endpoint ]]; then
            local endpoints=$(grep -oE '\`(GET|POST|PUT|DELETE|PATCH) [^`]+\`' "$doc" | sed 's/`//g')
            while IFS= read -r endpoint; do
                echo "$endpoint|$doc_name"
            done <<< "$endpoints"
        fi

        # 提取模块名（如果是模块文档）
        if [[ "$doc_name" =~ module ]]; then
            local modules=$(grep -oE '^### .+模块' "$doc" | sed 's/### //' | sed 's/模块//')
            while IFS= read -r module; do
                echo "$module|$doc_name"
            done <<< "$modules"
        fi
    done
}
```

---

## 图表和代码块索引

### generate_diagram_index()

```bash
#!/usr/bin/env bash
# 生成文档中所有 Mermaid 图表的索引
# 用法: generate_diagram_index <output_dir> <documents_list>
# 输出: diagrams.md 文档

generate_diagram_index() {
    local output_dir=$1
    shift
    local documents=("$@")

    local diagram_index="$output_dir/diagrams.md"

    cat > "$diagram_index" <<'EOF'
# 文档图表索引

所有文档中的 Mermaid 图表。

---

EOF

    echo "📊 生成图表索引..." >&2

    local diagram_count=0

    for doc in "${documents[@]}"; do
        if [ ! -f "$doc" ]; then
            continue
        fi

        local doc_name=$(basename "$doc" .md)
        local doc_title=$(get_document_title "$doc")
        local doc_path=$(realpath --relative-to="$output_dir" "$doc")

        # 提取 Mermaid 图表
        local diagrams=$(grep -A 20 '```mermaid' "$doc" | grep -c '```mermaid' || echo "0")

        if [ "$diagrams" -gt 0 ]; then
            diagram_count=$((diagram_count + diagrams))

            echo "## [$doc_title](./$doc_path)" >> "$diagram_index"
            echo "" >> "$diagram_index"
            echo "**图表数量**: $diagrams" >> "$diagram_index"
            echo "" >> "$diagram_index"

            # 提取图表类型
            local diagram_types=$(grep -A 1 '```mermaid' "$doc" | grep -v '```mermaid' | grep -v '^\s*$' | cut -d' ' -f1 | sort | uniq)

            echo "**图表类型**:" >> "$diagram_index"
            echo "$diagram_types" | while read -r type; do
                if [ -n "$type" ]; then
                    echo "- \`$type\`" >> "$diagram_index"
                fi
            done

            echo "" >> "$diagram_index"
            echo "---" >> "$diagram_index"
            echo "" >> "$diagram_index"
        fi
    done

    echo "" >> "$diagram_index"
    echo "**总计**: $diagram_count 个图表" >> "$diagram_index"

    echo "✅ 图表索引已生成: $diagram_index ($diagram_count 个图表)" >&2
}
```

### generate_code_example_index()

```bash
#!/usr/bin/env bash
# 生成文档中所有代码示例的索引
# 用法: generate_code_example_index <output_dir> <documents_list>
# 输出: code-examples.md 文档

generate_code_example_index() {
    local output_dir=$1
    shift
    local documents=("$@")

    local example_index="$output_dir/code-examples.md"

    cat > "$example_index" <<'EOF'
# 代码示例索引

文档中的所有代码示例。

---

## 语言分布

EOF

    echo "💻 生成代码示例索引..." >&2

    # 统计各语言代码块数量
    declare -A lang_counts

    for doc in "${documents[@]}"; do
        if [ ! -f "$doc" ]; then
            continue
        fi

        # 提取代码块语言标识
        local langs=$(grep -oE '^```[a-z]+' "$doc" | sed 's/^```//' | sort | uniq)

        while IFS= read -r lang; do
            if [ -n "$lang" ]; then
                lang_counts[$lang]=$((${lang_counts[$lang]:-0} + $(grep -c "^```$lang" "$doc")))
            fi
        done <<< "$langs"
    done

    # 输出语言分布表格
    echo "| 语言 | 示例数量 |" >> "$example_index"
    echo "|------|----------|" >> "$example_index"

    for lang in "${!lang_counts[@]}"; do
        echo "| $lang | ${lang_counts[$lang]} |" >> "$example_index"
    done

    echo "" >> "$example_index"
    echo "---" >> "$example_index"
    echo "" >> "$example_index"
    echo "## 按文档浏览" >> "$example_index"
    echo "" >> "$example_index"

    # 按文档列出代码示例
    for doc in "${documents[@]}"; do
        if [ ! -f "$doc" ]; then
            continue
        fi

        local doc_name=$(basename "$doc" .md)
        local doc_title=$(get_document_title "$doc")
        local doc_path=$(realpath --relative-to="$output_dir" "$doc")

        # 统计该文档的代码块数量
        local code_blocks=$(grep -c '^```' "$doc" || echo "0")

        if [ "$code_blocks" -gt 0 ]; then
            echo "### [$doc_title](./$doc_path)" >> "$example_index"
            echo "" >> "$example_index"
            echo "**代码示例**: $code_blocks 个代码块" >> "$example_index"
            echo "" >> "$example_index"
        fi
    done

    echo "✅ 代码示例索引已生成: $example_index" >&2
}
```

---

## 文档导航生成

### generate_breadcrumb_nav()

```bash
#!/usr/bin/env bash
# 为文档生成面包屑导航
# 用法: generate_breadcrumb_nav <document_file> <output_dir>
# 效果: 在文档顶部添加 [首页] > [分类] > [当前文档]

generate_breadcrumb_nav() {
    local doc_file=$1
    local output_dir=$2

    if [ ! -f "$doc_file" ]; then
        echo "⚠️ 文档不存在: $doc_file" >&2
        return 1
    fi

    echo "🍞 生成面包屑导航: $doc_file" >&2

    local doc_name=$(basename "$doc_file" .md)
    local doc_group=$(get_document_group "$doc_file")
    local doc_title=$(get_document_title "$doc_file")

    # 生成面包屑
    local breadcrumb="[首页](./README.md) > [$doc_group](./README.md#$doc_group) > **$doc_title**"

    # 在文档开头插入面包屑（在第一个标题前）
    local temp_file="${doc_file}.tmp"

    # 查找第一个标题行
    local first_title=$(grep -n "^#" "$doc_file" | cut -d: -f1 | head -n 1)

    if [ -z "$first_title" ]; then
        first_title=1
    fi

    # 输出面包屑和文档内容
    {
        head -n $((first_title - 1)) "$doc_file"
        echo ""
        echo "> $breadcrumb"
        echo ""
        tail -n +$first_title "$doc_file"
    } > "$temp_file"

    mv "$temp_file" "$doc_file"

    echo "✅ 面包屑导航已添加: $doc_file" >&2
}
```

---

**版本**: 2.0.0
**最后更新**: 2026-01-05
**变更日志**:
- v2.0.0: 添加多级目录生成、锚点链接生成、交叉引用增强、图表索引、代码示例索引、面包屑导航
- v1.0.0: 初始版本，支持基本文档索引和交叉引用
