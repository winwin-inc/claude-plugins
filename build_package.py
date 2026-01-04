#!/usr/bin/env python3
"""
简单的包构建脚本
使用标准库构建 wheel 包
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    print(f"执行: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 命令失败:")
        print(result.stderr)
        return False
    print(result.stdout)
    return True

def main():
    """主函数"""
    project_root = Path(__file__).parent

    print("=" * 60)
    print("Wiki Generator 包构建脚本")
    print("=" * 60)
    print()

    # 1. 清理旧的构建产物
    print("🧹 清理旧的构建产物...")
    for dir_name in ["dist", "build", "*.egg-info"]:
        for path in project_root.glob(dir_name):
            if path.is_dir():
                print(f"  删除: {path}")
                shutil.rmtree(path)
    print("✅ 清理完成\n")

    # 2. 检查是否安装了 hatchling
    print("🔍 检查构建工具...")
    try:
        import hatchling
        print(f"✅ 找到 hatchling: {hatchling.__version__}")
        has_hatchling = True
    except ImportError:
        print("⚠️  未安装 hatchling，尝试使用 pip")
        has_hatchling = False

    # 3. 尝试构建
    print("\n🔨 开始构建包...")

    if has_hatchling:
        # 方法 1: 使用 hatchling 直接构建
        print("使用 hatchling 构建中...")
        success = run_command([
            sys.executable, "-m", "hatchling", "build"
        ], cwd=project_root)
    else:
        # 方法 2: 尝试使用 pip install build
        print("尝试安装 build 工具...")
        run_command([sys.executable, "-m", "pip", "install", "-q", "build", "wheel"])

        print("使用 build 模块构建中...")
        success = run_command([
            sys.executable, "-m", "build"
        ], cwd=project_root)

    if not success:
        print("\n❌ 构建失败")
        print("\n💡 建议:")
        print("1. 安装 uv: curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("2. 或安装 build: pip install build")
        print("3. 然后运行: uv build 或 python -m build")
        return 1

    # 4. 检查构建结果
    print("\n📦 检查构建结果...")
    dist_dir = project_root / "dist"
    wheel_files = list(dist_dir.glob("*.whl"))

    if not wheel_files:
        print("❌ 未找到 wheel 文件")
        return 1

    wheel_file = wheel_files[0]
    print(f"✅ 找到 wheel: {wheel_file.name}")
    print(f"   大小: {wheel_file.stat().st_size / 1024:.1f} KB")

    # 5. 验证 wheel 内容
    print("\n🔍 验证 wheel 内容...")
    import zipfile

    with zipfile.ZipFile(wheel_file, 'r') as zf:
        files = zf.namelist()

    py_files = [f for f in files if f.endswith('.py')]
    claude_files = [f for f in files if '.claude' in f]

    print(f"  总文件数: {len(files)}")
    print(f"  Python 文件: {len(py_files)}")
    print(f"  .claude 文件: {len(claude_files)}")

    if claude_files:
        print(f"\n✅ 包含 .claude 文件:")
        for f in sorted(claude_files)[:10]:
            print(f"    {f}")
        if len(claude_files) > 10:
            print(f"    ... 还有 {len(claude_files) - 10} 个文件")
    else:
        print("\n❌ 警告: wheel 包中没有 .claude 文件!")
        print("\n📝 wheel 包内容:")
        for f in sorted(files)[:20]:
            print(f"  {f}")

    print("\n" + "=" * 60)
    if claude_files:
        print("✅ 构建成功！wheel 包包含 .claude 目录")
    else:
        print("⚠️  构建完成，但缺少 .claude 目录")
        print("请检查 pyproject.toml 中的 hatch.build.include 配置")
    print("=" * 60)

    return 0 if claude_files else 1

if __name__ == "__main__":
    sys.exit(main())
