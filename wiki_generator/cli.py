#!/usr/bin/env python3
"""
Wiki Generator 安装工具

这是一个独立的 Python CLI 工具，用于安装 wiki-generate.md 命令和模板到 Claude Code 项目。

使用方法：
    uvx wiki-generator

当运行时，该工具会将 wiki-generator 项目中的 .claude/ 目录内容
复制到当前工作目录下，实现一键安装。

示例：
    cd /path/to/your/project
    uvx wiki-generator
    # 将 .claude/ 目录复制到 /path/to/your/project/
"""

import click
import sys
import os
import shutil
from pathlib import Path


def get_package_claude_dir():
    """
    获取 wiki-generator 包内的 .claude/ 目录路径

    .claude 目录位于 wiki_generator 包内，开发模式和安装模式路径一致。

    Returns:
        Path: .claude/ 目录的绝对路径

    Raises:
        RuntimeError: 如果 .claude/ 目录不存在
    """
    # 获取 wiki_generator 包目录
    package_dir = Path(__file__).parent.resolve()
    claude_dir = package_dir / ".claude"

    if not claude_dir.exists():
        raise RuntimeError(
            f"找不到 .claude/ 目录：{claude_dir}\n"
            "请确保 wiki-generator 项目结构正确"
        )

    return claude_dir


# 添加项目根目录到 Python 路径（用于导入工具模块）
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from wiki_generator.utils.formatter import format_success, format_info, format_warning, format_error
from wiki_generator.utils.validator import validate_claude_directory
from wiki_generator.utils.file_helper import calculate_directory_size, format_size


def copy_claude_directory(source_dir: Path, target_dir: Path, overwrite: bool = False) -> dict:
    """
    复制 .claude/ 目录到目标位置

    Args:
        source_dir: 源 .claude/ 目录
        target_dir: 目标项目目录
        overwrite: 是否覆盖已存在的文件

    Returns:
        dict: 复制结果
            - success (bool): 是否成功
            - files_copied (list): 复制的文件列表
            - files_skipped (list): 跳过的文件列表
            - errors (list): 错误列表
            - total_size (int): 总字节数
    """
    result = {
        "success": True,
        "files_copied": [],
        "files_skipped": [],
        "errors": [],
        "total_size": 0
    }

    try:
        # 创建目标 .claude/ 目录
        target_claude_dir = target_dir / ".claude"
        target_claude_dir.mkdir(parents=True, exist_ok=True)

        # 遍历源目录中的所有文件和目录
        for item in source_dir.iterdir():
            if item.name == ".gitkeep":
                # 跳过 .gitkeep 文件
                continue

            target_item = target_claude_dir / item.name

            try:
                if item.is_file():
                    # 处理文件
                    if target_item.exists():
                        if overwrite:
                            # 计算文件大小
                            size = item.stat().st_size
                            shutil.copy2(item, target_item)
                            result["files_copied"].append(str(item.relative_to(source_dir)))
                            result["total_size"] += size
                        else:
                            result["files_skipped"].append(str(item.relative_to(source_dir)))
                    else:
                        # 复制新文件
                        size = item.stat().st_size
                        shutil.copy2(item, target_item)
                        result["files_copied"].append(str(item.relative_to(source_dir)))
                        result["total_size"] += size

                elif item.is_dir():
                    # 处理目录（递归复制）
                    if target_item.exists():
                        if overwrite:
                            # 删除现有目录并复制
                            shutil.rmtree(target_item)
                            shutil.copytree(item, target_item)
                            # 计算目录大小
                            size = calculate_directory_size(item)
                            result["files_copied"].append(f"{item.name}/ (目录)")
                            result["total_size"] += size
                        else:
                            result["files_skipped"].append(f"{item.name}/ (目录)")
                    else:
                        # 复制新目录
                        shutil.copytree(item, target_item)
                        size = calculate_directory_size(item)
                        result["files_copied"].append(f"{item.name}/ (目录)")
                        result["total_size"] += size

            except Exception as e:
                result["errors"].append(f"处理 {item.name} 时出错: {str(e)}")
                result["success"] = False

    except Exception as e:
        result["success"] = False
        result["errors"].append(f"复制操作失败: {str(e)}")

    return result


@click.command()
@click.version_option(version="1.0.0", prog_name="wiki-generator")
@click.option("--target", "-t", type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
              default=None, help="目标项目目录（默认为当前工作目录）")
@click.option("--overwrite", "-o", is_flag=True, help="覆盖已存在的文件")
@click.option("--dry-run", "-n", is_flag=True, help="预览操作，不实际复制文件")
def cli(target, overwrite, dry_run):
    """
    Wiki Generator 安装工具

    将 wiki-generator 项目中的 .claude/ 目录复制到你的项目目录，
    实现 Claude Code 自定义命令和模板的快速安装。

    默认情况下，文件会被复制到当前工作目录。

    示例：

        # 在当前项目中安装
        uvx wiki-generator

        # 在指定目录中安装
        uvx wiki-generator --target /path/to/project

        # 覆盖已存在的文件
        uvx wiki-generator --overwrite

        # 预览将要复制的内容
        uvx wiki-generator --dry-run
    """
    try:
        # 确定目标目录
        if target is None:
            target_dir = Path.cwd()
        else:
            target_dir = target

        format_info(f"目标目录: {target_dir}")

        # 获取源 .claude/ 目录
        source_dir = get_package_claude_dir()
        format_info(f"源目录: {source_dir}")

        # 检查目标目录的 .claude/ 目录状态
        target_claude_dir = target_dir / ".claude"

        if target_claude_dir.exists():
            if overwrite:
                format_warning("目标 .claude/ 目录已存在，将覆盖文件（--overwrite）")
            else:
                format_warning("目标 .claude/ 目录已存在，将跳过已存在的文件")
                format_info("使用 --overwrite 选项覆盖现有文件")
        else:
            format_success("将创建新的 .claude/ 目录")

        # 显示将要复制的内容
        format_info("\n将要复制的内容：")
        for item in sorted(source_dir.iterdir()):
            if item.name == ".gitkeep":
                continue
            if item.is_file():
                size = item.stat().st_size
                click.echo(f"  📄 {item.name} ({format_size(size)})")
            elif item.is_dir():
                size = calculate_directory_size(item)
                click.echo(f"  📁 {item.name}/ ({format_size(size)})")

        # 如果是预览模式，只显示信息不执行
        if dry_run:
            format_warning("\n预览模式：未实际复制文件")
            format_info("移除 --dry-run 选项以执行实际安装")
            return

        # 执行复制
        click.echo()  # 空行
        format_info("开始复制...")

        result = copy_claude_directory(source_dir, target_dir, overwrite=overwrite)

        # 显示结果
        click.echo()  # 空行

        if result["success"]:
            format_success("✓ 安装成功！\n")

            if result["files_copied"]:
                click.echo(f"  复制的文件/目录 ({len(result['files_copied'])}):")
                for file in result["files_copied"]:
                    click.echo(f"    ✓ {file}")

            if result["files_skipped"]:
                click.echo(f"\n  跳过的文件/目录 ({len(result['files_skipped'])}):")
                for file in result["files_skipped"]:
                    click.echo(f"    ⊘ {file}")

            if result["errors"]:
                click.echo(f"\n  错误 ({len(result['errors'])}):")
                for error in result["errors"]:
                    click.echo(f"    ✗ {error}")

            click.echo(f"\n  总计: {format_size(result['total_size'])}")
            click.echo(f"\n  📁 安装位置: {target_dir / '.claude'}")
            click.echo(f"  🎉 现在你可以在项目中使用 Claude Code Wiki 命令了！")

        else:
            format_error("✗ 安装失败\n")
            for error in result["errors"]:
                click.echo(f"  ✗ {error}")
            sys.exit(1)

    except RuntimeError as e:
        format_error(f"错误: {str(e)}")
        sys.exit(1)
    except Exception as e:
        format_error(f"未预期的错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
