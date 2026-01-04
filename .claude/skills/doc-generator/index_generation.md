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

**版本**: 1.0.0
**最后更新**: 2026-01-04
