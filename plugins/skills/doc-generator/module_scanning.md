# 业务模块扫描 Skill

**功能**: 自动识别项目的业务模块（服务层、页面层、API 层、模型层）

**扫描方法**: 使用 `find` 扫描常见目录结构，统计文件数量和代码行数

**性能目标**: 识别时间 < 30 秒（大型项目）

**文件统计范围**: 只统计源代码文件（.py, .js, .tsx, .ts, .jsx），排除 test/、tests/、__pycache__/ 等

---

## 核心扫描函数

### identify_business_modules()

```bash
#!/usr/bin/env bash
# 业务模块识别主函数
# 用法: identify_business_modules <project_dir>

identify_business_modules() {
    local project_dir=$1
    local modules=()

    # 1. 服务层识别
    modules+=($(identify_service_modules "$project_dir"))

    # 2. 页面层识别
    modules+=($(identify_page_modules "$project_dir"))

    # 3. API 路由识别
    modules+=($(identify_api_modules "$project_dir"))

    # 4. 模型层识别
    modules+=($(identify_model_modules "$project_dir"))

    echo "${modules[@]}"
}
```

---

## 1. 服务层识别

**扫描路径优先级**：
1. `src/services/`
2. `app/services/`
3. `services/`（根目录）

```bash
identify_service_modules() {
    local project_dir=$1
    local service_modules=()
    local scan_paths=("src/services" "app/services" "services")

    for path in "${scan_paths[@]}"; do
        local full_path="$project_dir/$path"

        if [ -d "$full_path" ]; then
            echo "📂 扫描服务层: $path" >&2

            # 查找所有子目录（每个子目录视为一个独立模块）
            while IFS= read -r -d '' module_dir; do
                local module_name=$(basename "$module_dir")
                local file_count=$(count_source_files "$module_dir")

                # 只包含有源代码文件的模块
                if [ "$file_count" -gt 0 ]; then
                    service_modules+=("$path|$module_name|$file_count|$module_dir")
                fi
            done < <(find "$full_path" -mindepth 1 -maxdepth 1 -type d -print0)

            break  # 找到第一个存在的路径后停止
        fi
    done

    echo "${service_modules[@]}"
}
```

---

## 2. 页面层识别

**扫描路径优先级**：
1. `pages/`
2. `app/pages/`
3. `src/pages/`

```bash
identify_page_modules() {
    local project_dir=$1
    local page_modules=()
    local scan_paths=("pages" "app/pages" "src/pages")

    for path in "${scan_paths[@]}"; do
        local full_path="$project_dir/$path"

        if [ -d "$full_path" ]; then
            echo "📄 扫描页面层: $path" >&2

            while IFS= read -r -d '' module_dir; do
                local module_name=$(basename "$module_dir")
                local file_count=$(count_source_files "$module_dir")

                if [ "$file_count" -gt 0 ]; then
                    page_modules+=("$path|$module_name|$file_count|$module_dir")
                fi
            done < <(find "$full_path" -mindepth 1 -maxdepth 1 -type d -print0)

            break
        fi
    done

    echo "${page_modules[@]}"
}
```

---

## 3. API 路由识别

**扫描路径优先级**：
1. `api/`
2. `routers/`
3. `app/views/`（Django）
4. `src/api/`

```bash
identify_api_modules() {
    local project_dir=$1
    local api_modules=()
    local scan_paths=("api" "routers" "app/views" "src/api")

    for path in "${scan_paths[@]}"; do
        local full_path="$project_dir/$path"

        if [ -d "$full_path" ]; then
            echo "🌐 扫描 API 层: $path" >&2

            while IFS= read -r -d '' module_dir; do
                local module_name=$(basename "$module_dir")
                local file_count=$(count_source_files "$module_dir")

                if [ "$file_count" -gt 0 ]; then
                    api_modules+=("$path|$module_name|$file_count|$module_dir")
                fi
            done < <(find "$full_path" -mindepth 1 -maxdepth 1 -type d -print0)

            break
        fi
    done

    echo "${api_modules[@]}"
}
```

---

## 4. 模型层识别

**扫描路径优先级**：
1. `src/models/`
2. `app/models/`
3. `models/`

```bash
identify_model_modules() {
    local project_dir=$1
    local model_modules=()
    local scan_paths=("src/models" "app/models" "models")

    for path in "${scan_paths[@]}"; do
        local full_path="$project_dir/$path"

        if [ -d "$full_path" ]; then
            echo "🗄️ 扫描模型层: $path" >&2

            while IFS= read -r -d '' module_dir; do
                local module_name=$(basename "$module_dir")
                local file_count=$(count_source_files "$module_dir")

                if [ "$file_count" -gt 0 ]; then
                    model_modules+=("$path|$module_name|$file_count|$module_dir")
                fi
            done < <(find "$full_path" -mindepth 1 -maxdepth 1 -type d -print0)

            break
        fi
    done

    echo "${model_modules[@]}"
}
```

---

## 文件统计函数

**只统计源代码文件**，排除：
- 测试文件：`test/`、`tests/`、`test_*.py`、`*_test.py`
- 缓存目录：`__pycache__/`、`.pytest_cache/`
- 配置文件：`*.ini`、`*.cfg`、`*.conf`
- 构建文件：`dist/`、`build/`、`*.egg-info/`

```bash
# 统计源代码文件数量
count_source_files() {
    local module_dir=$1
    local count=0

    # 统计 Python、JavaScript、TypeScript 文件
    count=$(find "$module_dir" -type f \
        \( -name "*.py" -o -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" \) \
        ! -path "*/test/*" \
        ! -path "*/tests/*" \
        ! -path "*/__pycache__/*" \
        ! -path "*/.pytest_cache/*" \
        ! -path "*/node_modules/*" \
        ! -path "*/dist/*" \
        ! -path "*/build/*" \
        ! -name "test_*.py" \
        ! -name "*_test.py" \
        ! -name "test_*.js" \
        ! -name "*_test.js" \
        ! -name "*.test.ts" \
        ! -name "*.test.tsx" \
        | wc -l)

    echo "$count"
}

# 统计代码行数
count_lines() {
    local module_dir=$1
    local lines=0

    lines=$(find "$module_dir" -type f \
        \( -name "*.py" -o -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" \) \
        ! -path "*/test/*" \
        ! -path "*/tests/*" \
        ! -path "*/__pycache__/*" \
        ! -path "*/node_modules/*" \
        ! -name "test_*.py" \
        ! -name "*_test.py" \
        -exec cat {} \; \
        | wc -l)

    echo "$lines"
}

# 统计依赖复杂度（导入语句数量）
count_dependencies() {
    local module_dir=$1
    local deps=0

    deps=$(find "$module_dir" -name "*.py" \
        ! -path "*/test/*" \
        ! -path "*/tests/*" \
        ! -path "*/__pycache__/*" \
        -exec grep -h "^import\|^from" {} \; \
        | sort -u \
        | wc -l)

    echo "$deps"
}
```

---

## 模块规模评估

根据文件数量、代码行数、依赖复杂度计算模块规模。

**规模分级**：
- 小型模块：1-4 文件（1 层文档）
- 中型模块：5-20 文件（2 层文档）
- 大型模块：21-50 文件（3 层文档）
- 超大型模块：>50 文件（4 层文档）

```bash
calculate_module_scale() {
    local module_dir=$1
    local file_count=$(count_source_files "$module_dir")
    local line_count=$(count_lines "$module_dir")
    local dep_count=$(count_dependencies "$module_dir")

    # 加权评分
    # 文件数量权重 60%，代码行数权重 30%，依赖复杂度权重 10%
    local score=$((file_count * 10 + line_count / 100 * 3 + dep_count * 2))

    local scale=""
    local depth=0

    if [ "$file_count" -le 4 ]; then
        scale="small"
        depth=1
    elif [ "$file_count" -le 20 ]; then
        scale="medium"
        depth=2
    elif [ "$file_count" -le 50 ]; then
        scale="large"
        depth=3
    else
        scale="xlarge"
        depth=4
    fi

    echo "$scale|$depth|$file_count|$line_count|$dep_count|$score"
}
```

---

## 模块信息输出格式

**返回格式**：`<路径>|<模块名>|<文件数>|<模块目录>|<规模>|<文档深度>`

```bash
# 示例：获取所有模块的完整信息
get_all_modules_info() {
    local project_dir=$1
    local modules=()

    # 获取所有模块
    while IFS=' ' read -ra module_array; do
        for module in "${module_array[@]}"; do
            local path=$(echo "$module" | cut -d'|' -f1)
            local name=$(echo "$module" | cut -d'|' -f2)
            local file_count=$(echo "$module" | cut -d'|' -f3)
            local dir=$(echo "$module" | cut -d'|' -f4)

            # 计算模块规模
            local scale_info=$(calculate_module_scale "$dir")
            local scale=$(echo "$scale_info" | cut -d'|' -f1)
            local depth=$(echo "$scale_info" | cut -d'|' -f2)

            modules+=("$path|$name|$file_count|$dir|$scale|$depth")
        done
    done < <(identify_business_modules "$project_dir")

    echo "${modules[@]}"
}
```

---

## 使用示例

```bash
# 识别项目的所有业务模块
project_dir="/path/to/project"
modules=($(identify_business_modules "$project_dir"))

echo "发现的业务模块:"
for module in "${modules[@]}"; do
    IFS='|' read -r path name file_count dir <<< "$module"
    echo "  - $name ($path): $file_count 个文件"
done
```

**输出示例**：

```
发现的业务模块:
  - user (src/services): 8 个文件
  - order (src/services): 12 个文件
  - product (src/models): 15 个文件
  - auth (api): 3 个文件
```

---

## 边缘情况处理

### 1. 不规范目录结构

如果服务层代码混在根目录（如 `user_service.py` 直接在 `src/` 下）：

```bash
# 启发式扫描：通过文件名模式识别
scan_service_files_in_root() {
    local project_dir=$1
    local src_dir="$project_dir/src"

    if [ ! -d "$src_dir" ]; then
        return
    fi

    echo "🔍 启发式扫描根目录服务文件..." >&2

    find "$src_dir" -maxdepth 1 -type f \
        \( -name "*_service.py" -o -name "*service.py" \) \
        ! -name "test_*" \
        -exec basename {} \;
}
```

### 2. 空模块处理

```bash
# 跳过没有源代码的模块
if [ "$file_count" -eq 0 ]; then
    echo "⚠️ 跳过空模块: $module_name" >&2
    continue
fi
```

### 3. 超大项目优化

```bash
# 限制扫描的最大文件数量（避免性能问题）
MAX_SCAN_FILES=1000

total_files=$(find "$project_dir" -type f \
    \( -name "*.py" -o -name "*.js" -o -name "*.ts" \) \
    ! -path "*/test/*" \
    ! -path "*/node_modules/*" \
    | wc -l)

if [ "$total_files" -gt "$MAX_SCAN_FILES" ]; then
    echo "⚠️ 项目文件数量 ($total_files) 超过限制 ($MAX_SCAN_FILES)" >&2
    echo "💡 建议配置扫描范围或调整 MAX_SCAN_FILES" >&2
fi
```

---

## Monorepo 支持

Monorepo 检测逻辑在单独的 Skill 中实现（见 `monorepo_detection.md`）。

如果检测到 Monorepo 结构，将为每个子项目单独调用业务模块扫描。

```bash
# Monorepo 集成示例
if is_monorepo "$project_dir"; then
    echo "📦 检测到 Monorepo 结构" >&2

    # 获取所有子项目
    sub_projects=$(get_monorepo_sub_projects "$project_dir")

    # 为每个子项目单独扫描
    for sub_project in $sub_projects; do
        echo "🔍 扫描子项目: $sub_project" >&2
        identify_business_modules "$project_dir/$sub_project"
    done
else
    # 单项目扫描
    identify_business_modules "$project_dir"
fi
```

---

**版本**: 1.0.0
**最后更新**: 2026-01-04
