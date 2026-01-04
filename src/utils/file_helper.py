"""
文件工具模块

提供文件操作辅助功能：临时目录、文件复制、目录清理等。
"""

import os
import shutil
import tempfile
from typing import List, Optional
from pathlib import Path
from .error_handler import CommandInstallError
from .errors import ErrorCode


class FileHelper:
    """文件操作辅助类"""

    @staticmethod
    def create_temp_dir(prefix: str = "command-install-") -> str:
        """
        创建临时目录

        Args:
            prefix: 目录名前缀

        Returns:
            临时目录路径

        Raises:
            CommandInstallError: 创建失败时
        """
        try:
            temp_dir = tempfile.mkdtemp(prefix=prefix)
            return temp_dir

        except Exception as e:
            raise CommandInstallError(
                ErrorCode.DOWNLOAD_TEMP_DIR_ERROR,
                f"创建临时目录失败: {str(e)}"
            )

    @staticmethod
    def cleanup_temp_dir(temp_dir: str) -> None:
        """
        清理临时目录

        Args:
            temp_dir: 临时目录路径
        """
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except Exception:
            # 静默失败，清理错误不是致命错误
            pass

    @staticmethod
    def ensure_directory(directory: str) -> None:
        """
        确保目录存在（不存在则创建）

        Args:
            directory: 目录路径

        Raises:
            CommandInstallError: 创建失败时
        """
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)

        except Exception as e:
            raise CommandInstallError(
                ErrorCode.INSTALL_COPY_FAILED,
                f"创建目录失败: {directory}\n   {str(e)}"
            )

    @staticmethod
    def copy_file(src: str, dst: str) -> str:
        """
        复制文件

        Args:
            src: 源文件路径
            dst: 目标文件路径

        Returns:
            目标文件路径

        Raises:
            CommandInstallError: 复制失败时
        """
        try:
            # 确保目标目录存在
            FileHelper.ensure_directory(os.path.dirname(dst))

            # 复制文件
            shutil.copy2(src, dst)

            return dst

        except PermissionError:
            raise CommandInstallError(
                ErrorCode.INSTALL_PERMISSION_DENIED,
                f"无权限复制文件: {src} -> {dst}"
            )
        except Exception as e:
            raise CommandInstallError(
                ErrorCode.INSTALL_COPY_FAILED,
                f"文件复制失败: {src} -> {dst}\n   {str(e)}"
            )

    @staticmethod
    def delete_file(file_path: str) -> None:
        """
        删除文件

        Args:
            file_path: 文件路径

        Raises:
            CommandInstallError: 删除失败时
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)

        except PermissionError:
            raise CommandInstallError(
                ErrorCode.UNINSTALL_DELETE_FAILED,
                f"无权限删除文件: {file_path}"
            )
        except Exception as e:
            raise CommandInstallError(
                ErrorCode.UNINSTALL_DELETE_FAILED,
                f"删除文件失败: {file_path}\n   {str(e)}"
            )

    @staticmethod
    def delete_directory(directory: str) -> None:
        """
        删除目录

        Args:
            directory: 目录路径

        Raises:
            CommandInstallError: 删除失败时
        """
        try:
            if os.path.exists(directory):
                shutil.rmtree(directory)

        except PermissionError:
            raise CommandInstallError(
                ErrorCode.UNINSTALL_DELETE_FAILED,
                f"无权限删除目录: {directory}"
            )
        except Exception as e:
            raise CommandInstallError(
                ErrorCode.UNINSTALL_DELETE_FAILED,
                f"删除目录失败: {directory}\n   {str(e)}"
            )

    @staticmethod
    def list_files(directory: str, pattern: Optional[str] = None) -> List[str]:
        """
        列出目录中的文件

        Args:
            directory: 目录路径
            pattern: 文件名模式（可选，如 "*.md"）

        Returns:
            文件路径列表
        """
        try:
            path = Path(directory)

            if pattern:
                files = list(path.glob(pattern))
            else:
                files = list(path.rglob("*"))

            # 只返回文件，不返回目录
            return [str(f) for f in files if f.is_file()]

        except Exception as e:
            raise CommandInstallError(
                ErrorCode.SYSTEM_UNKNOWN_ERROR,
                f"列出文件失败: {directory}\n   {str(e)}"
            )

    @staticmethod
    def file_exists(file_path: str) -> bool:
        """
        检查文件是否存在

        Args:
            file_path: 文件路径

        Returns:
            是否存在
        """
        return os.path.isfile(file_path)

    @staticmethod
    def directory_exists(directory: str) -> bool:
        """
        检查目录是否存在

        Args:
            directory: 目录路径

        Returns:
            是否存在
        """
        return os.path.isdir(directory)

    @staticmethod
    def get_file_size(file_path: str) -> int:
        """
        获取文件大小（字节）

        Args:
            file_path: 文件路径

        Returns:
            文件大小（字节）

        Raises:
            CommandInstallError: 文件不存在时
        """
        try:
            return os.path.getsize(file_path)

        except FileNotFoundError:
            raise CommandInstallError(
                ErrorCode.SYSTEM_UNKNOWN_ERROR,
                f"文件不存在: {file_path}"
            )
        except Exception as e:
            raise CommandInstallError(
                ErrorCode.SYSTEM_UNKNOWN_ERROR,
                f"获取文件大小失败: {file_path}\n   {str(e)}"
            )

    @staticmethod
    def get_directory_size(directory: str) -> int:
        """
        获取目录总大小（字节）

        Args:
            directory: 目录路径

        Returns:
            总大小（字节）
        """
        total_size = 0

        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(file_path)

        except Exception:
            # 静默失败，返回已计算的大小
            pass

        return total_size


def calculate_directory_size(directory: Path) -> int:
    """
    计算目录的总大小（字节）

    Args:
        directory: 目录路径

    Returns:
        总大小（字节）
    """
    total_size = 0

    try:
        if directory.is_dir():
            for item in directory.rglob("*"):
                if item.is_file():
                    total_size += item.stat().st_size
    except Exception:
        # 静默失败，返回已计算的大小
        pass

    return total_size


def format_size(size_bytes: int) -> str:
    """
    格式化字节大小为人类可读的格式

    Args:
        size_bytes: 字节大小

    Returns:
        格式化后的字符串（如 "1.5 KB", "2.3 MB"）
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
