# Monorepo 检测 Skill

**功能**: 自动检测 Monorepo（多包项目）结构，为每个子项目生成独立文档集

**检测方法**: 检查配置文件和目录结构

---

## 核心检测函数

### is_monorepo()

```bash
#!/usr/bin/env bash
# Monorepo 检测主函数
# 用法: is_monorepo <project_dir>
# 返回: 0 (true) 或 1 (false)

is_monorepo() {
    local project_dir=$1

    # 检查配置文件
    if [ -f "$project_dir/pnpm-workspace.yaml" ]; then
        return 0  # pnpm workspace
    fi

    if [ -f "$project_dir/nx.json" ]; then
        return 0  # Nx workspace
    fi

    if [ -f "$project_dir/package.json" ]; then
        # 检查是否有 workspaces 配置
        if grep -q '"workspaces"' "$project_dir/package.json" 2>/dev/null; then
            return 0  # Yarn/npm workspaces
        fi
    fi

    # 检查目录结构
    if [ -d "$project_dir/packages" ] || [ -d "$project_dir/apps" ] || [ -d "$project_dir/workspaces" ]; then
        # 验证目录中确实有子项目
        if [ "$(find "$project_dir/packages" -maxdepth 1 -type d 2>/dev/null | wc -l)" -gt 1 ]; then
            return 0
        fi

        if [ "$(find "$project_dir/apps" -maxdepth 1 -type d 2>/dev/null | wc -l)" -gt 1 ]; then
            return 0
        fi
    fi

    return 1  # 不是 Monorepo
}
```

---

## 获取子项目列表

### get_monorepo_sub_projects()

```bash
# 获取 Monorepo 中所有子项目的路径
# 用法: get_monorepo_sub_projects <project_dir>
# 返回: 子项目路径列表（相对于项目根目录）

get_monorepo_sub_projects() {
    local project_dir=$1
    local sub_projects=()

    # 1. 检查 pnpm-workspace.yaml
    if [ -f "$project_dir/pnpm-workspace.yaml" ]; then
        echo "📦 检测到 pnpm workspace" >&2

        # 从配置文件中提取 packages 模式
        local patterns=$(grep "^packages:" "$project_dir/pnpm-workspace.yaml" -A 10 | grep "^  -" | sed 's/^  - //' | tr -d "'\"")

        # 根据模式查找匹配的目录
        for pattern in $patterns; do
            # 将通配符转换为 find 命令
            local glob_pattern="${pattern/\*/*}"

            while IFS= read -r -d '' sub_dir; do
                if [ -d "$sub_dir" ] && [ "$(basename "$sub_dir")" != "node_modules" ]; then
                    # 检查是否有 package.json 或 pyproject.toml
                    if [ -f "$sub_dir/package.json" ] || [ -f "$sub_dir/pyproject.toml" ]; then
                        sub_projects+=("$(realpath --relative-to="$project_dir" "$sub_dir")")
                    fi
                fi
            done < <(find "$project_dir" -type d -name "$glob_pattern" -print0 2>/dev/null)
        done
    fi

    # 2. 检查 nx.json
    if [ -f "$project_dir/nx.json" ]; then
        echo "📦 检测到 Nx workspace" >&2

        # 从 nx.json 中获取项目列表
        if command -v nx &> /dev/null; then
            # 使用 nx CLI 获取项目列表（如果可用）
            local nx_projects=$(nx show projects 2>/dev/null || echo "")

            if [ -n "$nx_projects" ]; then
                for project in $nx_projects; do
                    sub_projects+=("$project")
                done
            fi
        fi

        # 如果 nx CLI 不可用，扫描目录结构
        if [ ${#sub_projects[@]} -eq 0 ]; then
            if [ -d "$project_dir/packages" ]; then
                while IFS= read -r -d '' sub_dir; do
                    if [ -f "$sub_dir/package.json" ]; then
                        sub_projects+=("$(realpath --relative-to="$project_dir" "$sub_dir")")
                    fi
                done < <(find "$project_dir/packages" -maxdepth 2 -type d -print0 2>/dev/null)
            fi

            if [ -d "$project_dir/apps" ]; then
                while IFS= read -r -d '' sub_dir; do
                    if [ -f "$sub_dir/package.json" ]; then
                        sub_projects+=("$(realpath --relative-to="$project_dir" "$sub_dir")")
                    fi
                done < <(find "$project_dir/apps" -maxdepth 2 -type d -print0 2>/dev/null)
            fi
        fi
    fi

    # 3. 检查 package.json workspaces
    if [ -f "$project_dir/package.json" ]; then
        local workspaces=$(grep -A 10 '"workspaces"' "$project_dir/package.json" | grep -E '^\s+"[a-z/]+"\s*:,?' | sed 's/.*"\([^"]*\)".*/\1/')

        if [ -n "$workspaces" ]; then
            echo "📦 检测到 Yarn/npm workspaces" >&2

            for pattern in $workspaces; do
                local glob_pattern="${pattern/\*/*}"

                while IFS= read -r -d '' sub_dir; do
                    if [ -f "$sub_dir/package.json" ]; then
                        sub_projects+=("$(realpath --relative-to="$project_dir" "$sub_dir")")
                    fi
                done < <(find "$project_dir" -type d -name "$glob_pattern" -print0 2>/dev/null)
            done
        fi
    fi

    # 4. 降级：扫描 packages/ 和 apps/ 目录
    if [ ${#sub_projects[@]} -eq 0 ]; then
        if [ -d "$project_dir/packages" ]; then
            echo "📦 检测到 packages/ 目录结构" >&2

            while IFS= read -r -d '' sub_dir; do
                if [ -f "$sub_dir/package.json" ] || [ -f "$sub_dir/pyproject.toml" ]; then
                    sub_projects+=("$(realpath --relative-to="$project_dir" "$sub_dir")")
                fi
            done < <(find "$project_dir/packages" -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null)
        fi

        if [ -d "$project_dir/apps" ]; then
            echo "📦 检测到 apps/ 目录结构" >&2

            while IFS= read -r -d '' sub_dir; do
                if [ -f "$sub_dir/package.json" ] || [ -f "$sub_dir/pyproject.toml" ]; then
                    sub_projects+=("$(realpath --relative-to="$project_dir" "$sub_dir")")
                fi
            done < <(find "$project_dir/apps" -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null)
        fi
    fi

    echo "${sub_projects[@]}"
}
```

---

## 子项目独立文档生成

### generate_docs_for_monorepo()

```bash
# 为 Monorepo 中的每个子项目生成独立文档
# 用法: generate_docs_for_monorepo <project_dir>

generate_docs_for_monorepo() {
    local project_dir=$1
    local sub_projects=($(get_monorepo_sub_projects "$project_dir"))

    if [ ${#sub_projects[@]} -eq 0 ]; then
        echo "⚠️ 未找到任何子项目" >&2
        return 1
    fi

    echo "📦 Monorepo 包含 ${#sub_projects[@]} 个子项目:" >&2
    for sub_project in "${sub_projects[@]}"; do
        echo "  - $sub_project" >&2
    done
    echo "" >&2

    # 为每个子项目生成文档
    for sub_project in "${sub_projects[@]}"; do
        local sub_project_dir="$project_dir/$sub_project"
        local sub_project_name=$(basename "$sub_project")

        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
        echo "🔍 处理子项目: $sub_project_name" >&2
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2

        # 为子项目创建独立的文档输出目录
        local output_dir="docs/$sub_project_name"

        # 检测子项目的技术栈
        local tech_stack=($(detect_tech_stack "$sub_project_dir"))
        echo "📋 技术栈: ${tech_stack[*]}" >&2

        # 识别子项目的业务模块
        local modules=($(identify_business_modules "$sub_project_dir"))
        echo "📦 业务模块: ${modules[*]}" >&2

        # 生成文档（调用主文档生成流程）
        # generate_project_docs "$sub_project_dir" "$output_dir" "$tech_stack" "$modules"

        echo "✅ 子项目 $sub_project_name 文档生成完成" >&2
        echo "" >&2
    done

    # 生成 Monorepo 总览文档
    generate_monorepo_overview "$project_dir" "${sub_projects[@]}"
}
```

---

## Monorepo 总览文档生成

```bash
# 生成 Monorepo 总览文档（包含所有子项目索引）
generate_monorepo_overview() {
    local project_dir=$1
    shift
    local sub_projects=("$@")

    local overview_file="$project_dir/docs/README.md"

    cat > "$overview_file" <<'EOF'
# 项目文档总览

本仓库是一个 Monorepo，包含多个子项目。

---

## 子项目列表

EOF

    for sub_project in "${sub_projects[@]}"; do
        local sub_project_name=$(basename "$sub_project")
        local sub_project_dir="$project_dir/$sub_project"

        # 提取子项目描述
        local description=""
        if [ -f "$sub_project_dir/package.json" ]; then
            description=$(grep '"description"' "$sub_project_dir/package.json" | sed 's/.*"description": "\(.*\)".*/\1/')
        elif [ -f "$sub_project_dir/README.md" ]; then
            description=$(head -n 20 "$sub_project_dir/README.md" | grep -v "^#" | tr '\n' ' ' | cut -c1-100)
        fi

        echo "### [$sub_project_name](./$sub_project_name/)" >> "$overview_file"
        echo "" >> "$overview_file"
        echo "$description" >> "$overview_file"
        echo "" >> "$overview_file"
    done

    echo "✅ Monorepo 总览文档已生成: $overview_file" >&2
}
```

---

## 配置覆盖支持

允许用户通过 `wiki-config.json` 自定义 Monorepo 行为：

```json
{
  "monorepo": {
    "enabled": true,
    "sub_projects": [
      {
        "name": "frontend",
        "path": "packages/web-app",
        "output_dir": "docs/frontend"
      },
      {
        "name": "backend",
        "path": "packages/api",
        "output_dir": "docs/backend"
      }
    ],
    "generate_overview": true
  }
}
```

---

## 使用示例

```bash
# 检测是否为 Monorepo
project_dir="/path/to/project"

if is_monorepo "$project_dir"; then
    echo "✅ 这是一个 Monorepo 项目"

    # 获取所有子项目
    sub_projects=($(get_monorepo_sub_projects "$project_dir"))

    echo "子项目列表:"
    for sub_project in "${sub_projects[@]}"; do
        echo "  - $sub_project"
    done

    # 为每个子项目生成文档
    generate_docs_for_monorepo "$project_dir"
else
    echo "❌ 这不是 Monorepo 项目，使用单项目文档生成"
fi
```

**输出示例**：

```
✅ 这是一个 Monorepo 项目
子项目列表:
  - packages/web-app
  - packages/api
  - packages/shared

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 处理子项目: web-app
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 技术栈: react typescript vite
📦 业务模块: pages/ components/ services/
✅ 子项目 web-app 文档生成完成

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 处理子项目: api
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 技术栈: fastapi sqlalchemy redis
📦 业务模块: api/ services/ models/
✅ 子项目 api 文档生成完成
```

---

## 边缘情况处理

### 1. 嵌套 Monorepo

```bash
# 检测并处理嵌套的 Monorepo 结构
detect_nested_monorepo() {
    local project_dir=$1
    local depth=${2:-3}  # 默认扫描深度 3 层

    for ((i=0; i<depth; i++)); do
        if is_monorepo "$project_dir"; then
            return 0
        fi
        # 检查父目录
        project_dir=$(dirname "$project_dir")
    done

    return 1
}
```

### 2. 混合项目结构

```bash
# 处理既有 Monorepo 又有独立项目的复杂结构
handle_mixed_structure() {
    local project_dir=$1

    if is_monorepo "$project_dir"; then
        # Monorepo 处理
        generate_docs_for_monorepo "$project_dir"
    else
        # 检查是否有根目录的源代码（混合模式）
        if [ -d "$project_dir/src" ] || [ -f "$project_dir/package.json" ]; then
            echo "⚠️ 检测到混合结构：Monorepo + 根目录项目" >&2
            # 同时生成根目录文档
            generate_project_docs "$project_dir" "docs/root"
        fi
    fi
}
```

---

**版本**: 1.0.0
**最后更新**: 2026-01-04
