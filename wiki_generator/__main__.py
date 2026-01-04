#!/usr/bin/env python3
"""
Wiki Generator CLI 主入口

通过 `uvx wiki-generator` 或 `python -m wiki_generator` 调用。
"""

import argparse
import sys
from wiki_generator import __version__, InstallerError
from wiki_generator.installer import install_cli_files, check_write_permission
from wiki_generator.config import generate_config


def main() -> int:
    """主函数：解析命令行参数并执行安装

    Returns:
        int: 退出码（0=成功，1=错误，2=回滚失败）
    """
    parser = argparse.ArgumentParser(
        prog="wiki-generator",
        description="Wiki Generator CLI 安装工具 - 一键安装 Claude Code Wiki 命令和模板",
        epilog="更多信息请访问: https://github.com/user/repo-wiki",
    )

    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="强制覆盖已存在的文件",
    )

    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="显示将要安装的文件，不实际复制",
    )

    parser.add_argument(
        "--target-dir",
        "-d",
        default=".",
        help="目标安装目录（默认: 当前目录）",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="显示详细输出",
    )

    args = parser.parse_args()

    try:
        # 显示开始消息
        if args.verbose:
            print(f"🚀 Wiki Generator CLI 安装工具 v{__version__}")
            print(f"目标目录: {args.target_dir}")
            print()

        # 1. 权限检查
        if args.verbose:
            print("🔍 检查目录权限...")

        if not check_write_permission(args.target_dir):
            print(f"❌ 错误: 目录 '{args.target_dir}' 无写入权限")
            print("💡 提示: 请检查目录权限或使用 sudo 运行")
            return 1

        if args.verbose:
            print("✅ 权限检查通过")
            print()

        # 2. 安装 CLI 文件
        if args.dry_run:
            print("🔍 Dry-run 模式 - 将要安装的文件:")
            install_cli_files(
                target_dir=args.target_dir,
                force=args.force,
                dry_run=True,
                verbose=args.verbose,
            )
            print()
            print("💡 提示: 使用 --force 选项强制覆盖已存在文件")
            return 0

        print("📦 正在安装 .claude/ 目录...")
        installed_files = install_cli_files(
            target_dir=args.target_dir,
            force=args.force,
            dry_run=False,
            verbose=args.verbose,
        )

        if args.verbose:
            print(f"✅ 已安装 {len(installed_files)} 个文件")
            print()

        # 3. 生成配置文件
        print("⚙️  生成 wiki-config.json...")
        config = generate_config(target_dir=args.target_dir, overwrite=False)
        if args.verbose:
            print(f"✅ 配置文件已生成: output_dir={config['output_dir']}")
            print()

        # 4. 显示成功消息
        print("✅ 安装完成！")
        print()
        print("📚 下一步:")
        print("   1. 运行 /wiki-overview 生成项目概览文档")
        print("   2. 运行 /wiki-module <模块路径> 为特定模块生成文档")
        print("   3. 编辑 wiki-config.json 自定义配置")
        print()

        return 0

    except InstallerError as e:
        print(f"❌ 错误: {e.message}")
        if e.details and args.verbose:
            print(f"📋 详情: {e.details}")
        return 1

    except Exception as e:
        print(f"❌ 未知错误: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
