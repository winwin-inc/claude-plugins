#!/usr/bin/env bash
# Wiki 配置文件路径解析库
# 版本: 1.0.0
# 功能: 统一管理配置文件路径的查找和解析逻辑

# 查找配置文件
# 用法: find_config_file [output_dir]
# 输出: 找到的配置文件绝对路径，如果未找到则输出空字符串
find_config_file() {
    local output_dir=${1:-"docs"}
    local config_file=""

    # 优先级 1: 环境变量 WIKI_CONFIG（用户明确指定）
    if [ -n "$WIKI_CONFIG" ] && [ -f "$WIKI_CONFIG" ]; then
        echo "$WIKI_CONFIG"
        return 0
    fi

    # 如果设置了 WIKI_CONFIG 但文件不存在，发出警告但继续查找
    if [ -n "$WIKI_CONFIG" ] && [ ! -f "$WIKI_CONFIG" ]; then
        echo "⚠️  WIKI_CONFIG 指定的文件不存在: $WIKI_CONFIG" >&2
        echo "💡 提示: 尝试查找其他位置的配置文件..." >&2
    fi

    # 优先级 2: 指定的 output_dir 或默认位置
    config_file="$output_dir/wiki-config.json"

    if [ -f "$config_file" ]; then
        echo "$config_file"
        return 0
    fi

    # 未找到配置文件
    echo ""
    return 1
}

# 初始化配置文件
# 用法: init_config_file [output_dir]
# 输出: 配置文件的绝对路径
init_config_file() {
    local output_dir=${1:-"docs"}
    local config_file="$output_dir/wiki-config.json"

    # 创建输出目录
    mkdir -p "$output_dir"

    # 检查配置文件是否已存在
    if [ -f "$config_file" ]; then
        echo "$config_file"
        return 0
    fi

    # 从模板复制配置文件
    local template_file="plugins/templates/wiki-generate/wiki-config.json.template"

    if [ -f "$template_file" ]; then
        cp "$template_file" "$config_file"

        # 更新 output_dir 字段
        python3 - <<PYTHON_EOF 2>/dev/null
import json
from pathlib import Path

config_path = Path("$config_file")
template_path = Path("$template_file")

# 读取模板
with open(template_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# 更新 output_dir 和版本
config['output_dir'] = "$output_dir"
config['version'] = '1.0.2'

# 保存配置
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)
PYTHON_EOF

        echo "✅ 已创建配置文件: $config_file" >&2
    else
        # 创建默认配置
        cat > "$config_file" <<EOF
{
  "output_dir": "$output_dir",
  "language": "zh",
  "version": "1.0.2",
  "exclude_patterns": [
    "node_modules",
    "dist",
    "build",
    ".git",
    "coverage"
  ],
  "template_dir": ".claude-plugin/templates/wiki-generate",
  "quality_threshold": 80,
  "diagrams": {
    "enabled": true,
    "detail_level": "medium"
  },
  "modules": {
    "auto_detect": true,
    "patterns": ["src/*", "lib/*", "app/*"]
  }
}
EOF
        echo "✅ 已创建默认配置文件: $config_file" >&2
    fi

    echo "$config_file"
}

# 导出配置文件路径到环境变量
# 用法: export_config_path [output_dir]
# 输出: 配置文件的绝对路径
export_config_path() {
    local output_dir=${1:-"docs"}
    local config_file=""

    config_file=$(find_config_file "$output_dir")

    if [ -z "$config_file" ]; then
        echo "❌ 未找到配置文件" >&2
        echo "💡 提示: 请先运行 init_config_file 创建配置文件" >&2
        return 1
    fi

    export WIKI_CONFIG="$config_file"
    echo "$config_file"
}

# 验证配置文件
# 用法: validate_config [config_file]
# 输出: 验证结果（0=成功，1=失败）
validate_config() {
    local config_file=${1:-"$WIKI_CONFIG"}

    if [ -z "$config_file" ]; then
        echo "❌ 配置文件路径为空" >&2
        return 1
    fi

    if [ ! -f "$config_file" ]; then
        echo "❌ 配置文件不存在: $config_file" >&2
        return 1
    fi

    # 验证 JSON 格式
    if ! python3 -c "import json; json.load(open('$config_file'))" 2>/dev/null; then
        echo "❌ 配置文件格式错误（无效的 JSON）: $config_file" >&2
        return 1
    fi

    echo "✅ 配置文件验证通过: $config_file"
    return 0
}
