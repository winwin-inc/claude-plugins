#!/usr/bin/env python3
"""
测试构建脚本 - 验证 .claude 目录是否包含在包中
"""
import sys
import zipfile
from pathlib import Path

def check_wheel_contents(wheel_path: Path):
    """检查 wheel 包内容"""
    if not wheel_path.exists():
        print(f"❌ Wheel 文件不存在: {wheel_path}")
        return False

    print(f"✅ 找到 wheel 文件: {wheel_path}")

    with zipfile.ZipFile(wheel_path, 'r') as zf:
        files = zf.namelist()

    print(f"\n📦 Wheel 包内容 ({len(files)} 个文件):\n")

    # 分类显示
    py_files = [f for f in files if f.endswith('.py')]
    claude_files = [f for f in files if '.claude' in f]
    other_files = [f for f in files if f not in py_files and f not in claude_files]

    print(f"Python 文件 ({len(py_files)}):")
    for f in sorted(py_files)[:10]:  # 只显示前 10 个
        print(f"  {f}")
    if len(py_files) > 10:
        print(f"  ... 还有 {len(py_files) - 10} 个文件")

    print(f"\n.claude 文件 ({len(claude_files)}):")
    if claude_files:
        for f in sorted(claude_files):
            print(f"  ✓ {f}")
    else:
        print("  ❌ 未找到 .claude 相关文件")

    print(f"\n其他文件 ({len(other_files)}):")
    for f in sorted(other_files):
        print(f"  {f}")

    # 验证关键文件
    print("\n🔍 关键文件验证:")
    checks = [
        ("wiki_generator/__init__.py", "包初始化文件"),
        (".claude/commands/wiki-generate.md", "命令定义文件"),
        (".claude/templates/", "模板目录"),
        (".claude/wiki-config.json", "配置文件"),
    ]

    all_ok = True
    for pattern, desc in checks:
        found = any(pattern in f for f in files)
        status = "✅" if found else "❌"
        print(f"  {status} {desc} ({pattern})")
        if not found:
            all_ok = False

    return all_ok

if __name__ == "__main__":
    # 查找 wheel 文件
    dist_dir = Path("dist")
    wheel_files = list(dist_dir.glob("*.whl"))

    if not wheel_files:
        print("❌ dist/ 目录中没有找到 wheel 文件")
        sys.exit(1)

    if len(wheel_files) > 1:
        print(f"⚠️  找到多个 wheel 文件，使用第一个: {wheel_files[0]}")

    success = check_wheel_contents(wheel_files[0])

    if success:
        print("\n✅ 所有检查通过！")
        sys.exit(0)
    else:
        print("\n❌ 部分检查失败，请修复打包配置")
        sys.exit(1)
