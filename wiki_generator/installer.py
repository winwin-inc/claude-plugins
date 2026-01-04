"""
Wiki Generator 安装器核心逻辑

负责将 .claude/ 目录及其内容复制到目标项目目录。
包含文件复制、权限检查、回滚机制等功能。
"""

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import List
from wiki_generator import InstallerError, RollbackError


@dataclass
class InstalledFile:
    """已安装文件信息

    用于跟踪安装过程中的文件，支持回滚操作。
    """

    source_path: str  # 源文件路径（包内路径）
    dest_path: str  # 目标文件路径（项目内路径）
    is_backup: bool = False  # 是否是已存在文件的备份
    backup_path: str | None = None  # 备份文件路径（如果 is_backup=True）


def check_write_permission(target_dir: str) -> bool:
    """检查目标目录是否有写入权限

    Args:
        target_dir: 目标目录路径

    Returns:
        bool: 有写入权限返回 True，否则返回 False
    """
    try:
        target_path = Path(target_dir).resolve()
        # 尝试创建临时文件测试权限
        test_file = target_path / ".write_test_{}".format(os.getpid())
        test_file.touch()
        test_file.unlink()
        return True
    except (OSError, PermissionError):
        return False


def get_package_claude_dir() -> Path:
    """获取包内的 .claude/ 目录路径

    Returns:
        Path: .claude/ 目录的绝对路径
    """
    # 获取当前文件所在目录的父目录（wiki_generator/）
    current_dir = Path(__file__).parent.resolve()
    # .claude/ 目录应该在 wiki_generator/.claude/
    claude_dir = current_dir / ".claude"
    return claude_dir


def collect_files_to_copy(
    source_dir: Path, relative_dir: str = ""
) -> List[tuple[str, str]]:
    """递归收集所有需要复制的文件

    Args:
        source_dir: 源目录路径
        relative_dir: 相对路径（用于递归）

    Returns:
        List[tuple[str, str]]: (源文件路径, 目标相对路径) 列表
    """
    files = []
    for item in source_dir.iterdir():
        if item.is_file():
            # 跳过备份目录
            if "backups" in item.parts or ".backup" in item.name:
                continue
            # 跳过隐藏文件（除了 .claude 本身）
            if item.name.startswith(".") and item.name != ".claude":
                continue
            rel_path = str(Path(relative_dir) / item.name) if relative_dir else item.name
            files.append((str(item), rel_path))
        elif item.is_dir() and item.name != "__pycache__":
            # 递归处理子目录
            subdir = Path(relative_dir) / item.name if relative_dir else item.name
            files.extend(collect_files_to_copy(item, str(subdir)))
    return files


def install_cli_files(
    target_dir: str = ".",
    force: bool = False,
    dry_run: bool = False,
    verbose: bool = False,
) -> List[InstalledFile]:
    """安装 .claude/ 目录到目标目录

    Args:
        target_dir: 目标目录路径（默认: 当前目录）
        force: 强制覆盖已存在文件（默认: False）
        dry_run: 显示将要安装的文件，不实际复制（默认: False）
        verbose: 显示详细输出（默认: False）

    Returns:
        List[InstalledFile]: 已安装的文件列表

    Raises:
        PermissionError: 目标目录无写入权限
        OSError: 文件复制失败
        RollbackError: 回滚失败（严重错误）
    """
    installed_files: List[InstalledFile] = []
    target_path = Path(target_dir).resolve()

    # 获取源目录
    source_claude_dir = get_package_claude_dir()
    if not source_claude_dir.exists():
        raise InstallerError(
            message=f"包内 .claude/ 目录不存在: {source_claude_dir}",
            details="请确保包已正确安装",
        )

    # 收集所有需要复制的文件
    file_mappings = collect_files_to_copy(source_claude_dir)

    if verbose or dry_run:
        print(f"找到 {len(file_mappings)} 个文件需要安装")
        if dry_run:
            for src, rel_path in file_mappings:
                dest = target_path / ".claude" / rel_path
                print(f"  {dest}")
            return installed_files

    try:
        # 复制文件
        for src_file, rel_path in file_mappings:
            dest_file = target_path / ".claude" / rel_path
            dest_dir = dest_file.parent

            # 创建目标目录
            dest_dir.mkdir(parents=True, exist_ok=True)

            # 检查文件是否已存在
            if dest_file.exists() and not force:
                if verbose:
                    print(f"⚠️  跳过已存在文件: {dest_file}")
                continue

            # 备份已存在文件（如果 force=True）
            if dest_file.exists() and force:
                backup_path = Path(str(dest_file) + ".backup")
                shutil.copy2(dest_file, backup_path)
                if verbose:
                    print(f"💾 备份: {dest_file} -> {backup_path}")
                installed_files.append(
                    InstalledFile(
                        source_path=src_file,
                        dest_path=str(dest_file),
                        is_backup=True,
                        backup_path=str(backup_path),
                    )
                )

            # 复制文件
            shutil.copy2(src_file, dest_file, follow_symlinks=False)
            if verbose:
                print(f"✓ 复制: {rel_path}")

            installed_files.append(
                InstalledFile(
                    source_path=src_file,
                    dest_path=str(dest_file),
                    is_backup=False,
                )
            )

        return installed_files

    except Exception as e:
        # 安装失败，执行回滚
        if verbose:
            print(f"❌ 安装失败: {e}")
            print("🔄 正在回滚...")
        try:
            rollback_installation(installed_files, verbose=verbose)
        except RollbackError as rollback_err:
            # 回滚失败，这是严重错误
            raise RollbackError(
                message=f"安装失败且回滚失败: {rollback_err.message}",
                failed_files=rollback_err.failed_files,
            ) from rollback_err
        raise InstallerError(
            message=f"安装失败，已回滚所有更改: {e}",
            details=str(e),
        ) from e


def rollback_installation(
    installed_files: List[InstalledFile],
    verbose: bool = False,
) -> None:
    """回滚已安装的文件

    Args:
        installed_files: 已安装文件列表（从 install_cli_files 返回）
        verbose: 显示详细输出（默认: False）

    Raises:
        RollbackError: 回滚失败（部分文件无法删除）
    """
    failed_files: List[str] = []

    # 按相反顺序删除文件（先删除最后复制的）
    for installed_file in reversed(installed_files):
        try:
            dest_path = Path(installed_file.dest_path)

            # 如果是备份文件，先恢复原始文件
            if installed_file.is_backup and installed_file.backup_path:
                backup_path = Path(installed_file.backup_path)
                if backup_path.exists():
                    shutil.move(str(backup_path), str(dest_path))
                    if verbose:
                        print(f"↩️  恢复: {dest_path}")

            # 删除已复制的文件
            if dest_path.exists():
                dest_path.unlink()
                if verbose:
                    print(f"🗑️  删除: {dest_path}")

        except Exception as e:
            failed_files.append(installed_file.dest_path)
            if verbose:
                print(f"⚠️  回滚失败: {installed_file.dest_path} - {e}")

    # 清理空目录
    try:
        target_claude_dir = Path(installed_files[0].dest_path).parent.parent
        for root, dirs, files in os.walk(target_claude_dir, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                try:
                    if dir_path.exists() and not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        if verbose:
                            print(f"🗑️  删除空目录: {dir_path}")
                except Exception:
                    pass  # 忽略目录删除失败
    except Exception:
        pass  # 忽略清理失败

    # 如果有任何文件回滚失败，抛出异常
    if failed_files:
        raise RollbackError(
            message="部分文件回滚失败",
            failed_files=failed_files,
        )
