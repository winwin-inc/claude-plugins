#!/bin/bash
# 数据迁移脚本: docs/claude-sessions/ → docs/plans/sessions/

set -e

echo "🔄 开始数据迁移..."
echo ""

# 1. 备份现有数据
if [ -d "docs/claude-sessions" ]; then
    echo "📦 备份现有数据..."
    backup_dir="docs/claude-sessions.backup.$(date +%Y%m%d_%H%M%S)"
    cp -r docs/claude-sessions "$backup_dir"
    echo "✅ 备份完成: $backup_dir"
else
    echo "⚠️  未找到 docs/claude-sessions/ 目录"
    echo "ℹ️  如果这是新安装，可以忽略此消息"
    exit 0
fi

# 2. 创建新目录结构
echo ""
echo "📁 创建新目录结构..."
mkdir -p docs/plans/sessions

# 3. 迁移会话文件
echo ""
echo "📦 迁移会话文件..."
cp -r docs/claude-sessions/* docs/plans/sessions/

# 4. 更新月度 README 中的链接
echo ""
echo "🔧 更新内部链接..."
python3 << 'PYTHON_EOF'
import glob
import os

readme_files = glob.glob("docs/plans/sessions/**/README.md", recursive=True)
updated_count = 0

for readme_file in readme_files:
    try:
        with open(readme_file, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        content = content.replace('../../plans/', '../../')

        if content != original_content:
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(content)
            updated_count += 1
            print(f"  ✅ Updated: {readme_file}")
    except Exception as e:
        print(f"  ❌ Error updating {readme_file}: {e}")

print(f"✅ 共更新了 {updated_count} 个文件")
PYTHON_EOF

# 5. 验证迁移
echo ""
echo "🔍 验证迁移结果..."
session_count=$(find docs/plans/sessions -name "session_*.md" | wc -l)
readme_count=$(find docs/plans/sessions -name "README.md" | wc -l)

echo "✅ 迁移了 ${session_count} 个会话文件"
echo "✅ 迁移了 ${readme_count} 个索引文件"

# 6. 显示迁移摘要
echo ""
echo "🎉 迁移完成!"
echo ""
echo "📋 迁移摘要:"
echo "  - 源目录: docs/claude-sessions/"
echo "  - 目标目录: docs/plans/sessions/"
echo "  - 备份目录: $backup_dir"
echo ""
echo "⚠️  请手动验证:"
echo "  1. 检查迁移的文件: ls -R docs/plans/sessions/"
echo "  2. 验证链接有效性: grep -r '\.\./' docs/plans/sessions/"
echo "  3. 确认无误后删除旧目录: rm -rf docs/claude-sessions"
echo "  4. 删除执行日志（如果存在）: rm -rf docs/execution-logs"
echo ""
echo "📚 查看迁移结果:"
echo "  - 查看会话文件: ls -la docs/plans/sessions/$(date +%Y%m)/"
echo "  - 查看月度索引: cat docs/plans/sessions/$(date +%Y%m)/README.md"
