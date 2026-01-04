"""文件操作相关的工具函数。

此模块包含文件安装、路径计算等工具函数。
"""

import shutil
from pathlib import Path
from typing import List, Optional


def ensure_directory(path: Path) -> None:
    """确保目录存在，如果不存在则创建。

    Args:
        path: 目录路径
    """
    path.mkdir(parents=True, exist_ok=True)


def copy_file_or_directory(src: Path, dst: Path, overwrite: bool = False) -> bool:
    """复制文件或目录。

    Args:
        src: 源路径
        dst: 目标路径
        overwrite: 是否覆盖已存在的文件

    Returns:
        是否成功复制
    """
    if not src.exists():
        return False

    if dst.exists() and not overwrite:
        return False

    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    elif src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=overwrite)

    return True


def list_files(directory: Path, pattern: str = "*") -> List[str]:
    """列出目录中的文件。

    Args:
        directory: 目录路径
        pattern: 文件匹配模式

    Returns:
        文件路径列表（相对路径）
    """
    if not directory.exists():
        return []

    files = []
    for item in directory.rglob(pattern):
        if item.is_file():
            files.append(str(item.relative_to(directory)))

    return files


def get_relative_path(source: Path, target: Path) -> Path:
    """计算相对路径。

    Args:
        source: 源路径
        target: 目标路径

    Returns:
        相对路径
    """
    try:
        return source.relative_to(target)
    except ValueError:
        # 没有共同祖先，返回绝对路径
        return source.absolute()


def backup_file(path: Path) -> Optional[Path]:
    """备份文件。

    Args:
        path: 文件路径

    Returns:
        备份文件路径，如果失败则返回 None
    """
    if not path.exists():
        return None

    backup_path = path.with_suffix(path.suffix + ".backup")

    try:
        shutil.copy2(path, backup_path)
        return backup_path
    except Exception:
        return None


def read_file_content(path: Path) -> Optional[str]:
    """读取文件内容。

    Args:
        path: 文件路径

    Returns:
        文件内容，如果失败则返回 None
    """
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def write_file_content(path: Path, content: str) -> bool:
    """写入文件内容。

    Args:
        path: 文件路径
        content: 文件内容

    Returns:
        是否成功写入
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return True
    except Exception:
        return False
