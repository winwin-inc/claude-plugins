"""
文件处理模块

提供文件复制、冲突检测和处理功能。
"""

import os
import shutil
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..utils.error_handler import CommandInstallError
from ..utils.errors import ErrorCode
from ..utils.validator import calculate_checksum
from ..utils.file_helper import FileHelper
from ..models.command import CommandFile


class FileHandler:
    """文件处理器"""

    # 目标目录
    COMMANDS_DIR = ".claude/commands"
    TEMPLATES_DIR = ".claude/templates"
    CONFIG_DIR = ".claude"

    def __init__(self, conflict_strategy: str = "skip"):
        """
        初始化文件处理器

        Args:
            conflict_strategy: 冲突处理策略（skip、backup、force）
        """
        self.conflict_strategy = conflict_strategy
        self.copied_files: List[CommandFile] = []
        self.skipped_files: List[str] = []
        self.backed_up_files: List[Dict[str, Any]] = []

    def install_command_file(self, source_path: str, command_name: Optional[str] = None) -> CommandFile:
        """
        安装命令文件

        Args:
            source_path: 源文件路径
            command_name: 命令名称（可选，用于重命名）

        Returns:
            命令文件对象

        Raises:
            CommandInstallError: 安装失败时
        """
        # 确定目标文件名
        if command_name:
            file_name = f"{command_name}.md"
        else:
            file_name = os.path.basename(source_path)

        target_path = os.path.join(self.COMMANDS_DIR, file_name)

        # 处理冲突
        if FileHelper.file_exists(target_path):
            if not self._handle_conflict(target_path):
                self.skipped_files.append(target_path)
                return None

        # 复制文件
        FileHelper.copy_file(source_path, target_path)

        # 计算校验和
        checksum = calculate_checksum(target_path)
        file_size = FileHelper.get_file_size(target_path)

        # 创建命令文件对象
        command_file = CommandFile(
            path=target_path,
            file_type="command",
            size=file_size,
            checksum=checksum
        )

        self.copied_files.append(command_file)
        return command_file

    def install_template_file(self, source_path: str) -> CommandFile:
        """
        安装模板文件

        Args:
            source_path: 源文件路径

        Returns:
            命令文件对象

        Raises:
            CommandInstallError: 安装失败时
        """
        # 确定目标路径
        file_name = os.path.basename(source_path)
        target_path = os.path.join(self.TEMPLATES_DIR, file_name)

        # 处理冲突
        if FileHelper.file_exists(target_path):
            if not self._handle_conflict(target_path):
                self.skipped_files.append(target_path)
                return None

        # 复制文件
        FileHelper.copy_file(source_path, target_path)

        # 计算校验和
        checksum = calculate_checksum(target_path)
        file_size = FileHelper.get_file_size(target_path)

        # 创建命令文件对象
        command_file = CommandFile(
            path=target_path,
            file_type="template",
            size=file_size,
            checksum=checksum
        )

        self.copied_files.append(command_file)
        return command_file

    def install_config_file(self, source_path: str) -> CommandFile:
        """
        安装配置文件

        Args:
            source_path: 源文件路径

        Returns:
            命令文件对象

        Raises:
            CommandInstallError: 安装失败时
        """
        # 配置文件通常不需要覆盖
        file_name = os.path.basename(source_path)
        target_path = os.path.join(self.CONFIG_DIR, file_name)

        # 如果目标已存在，跳过
        if FileHelper.file_exists(target_path):
            self.skipped_files.append(target_path)
            return None

        # 复制文件
        FileHelper.copy_file(source_path, target_path)

        # 计算校验和
        checksum = calculate_checksum(target_path)
        file_size = FileHelper.get_file_size(target_path)

        # 创建命令文件对象
        command_file = CommandFile(
            path=target_path,
            file_type="config",
            size=file_size,
            checksum=checksum
        )

        self.copied_files.append(command_file)
        return command_file

    def _handle_conflict(self, target_path: str) -> bool:
        """
        处理文件冲突

        Args:
            target_path: 目标文件路径

        Returns:
            是否应该继续安装（True=继续，False=跳过）
        """
        if self.conflict_strategy == "skip":
            # 跳过冲突文件
            return False

        elif self.conflict_strategy == "force":
            # 强制覆盖，不需要备份
            return True

        elif self.conflict_strategy == "backup":
            # 备份后覆盖
            self._backup_file(target_path)
            return True

        else:
            # 默认跳过
            return False

    def _backup_file(self, file_path: str) -> None:
        """
        备份文件

        Args:
            file_path: 文件路径
        """
        # 创建备份目录
        backup_dir = ".claude/backups"
        FileHelper.ensure_directory(backup_dir)

        # 生成备份文件名（时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = os.path.basename(file_path)
        backup_name = f"{timestamp}_{file_name}"
        backup_path = os.path.join(backup_dir, backup_name)

        # 复制文件到备份目录
        shutil.copy2(file_path, backup_path)

        # 记录备份信息
        self.backed_up_files.append({
            "original": file_path,
            "backup": backup_path,
            "timestamp": timestamp,
        })

    def get_summary(self) -> Dict[str, Any]:
        """
        获取安装摘要

        Returns:
            摘要字典
        """
        return {
            "copied_count": len(self.copied_files),
            "skipped_count": len(self.skipped_files),
            "backed_up_count": len(self.backed_up_files),
            "copied_files": [f.to_dict() for f in self.copied_files],
            "skipped_files": self.skipped_files,
            "backed_up_files": self.backed_up_files,
        }

    def cleanup_on_error(self) -> None:
        """
        出错时清理已复制的文件

        删除所有已复制的文件（回滚）
        """
        for command_file in self.copied_files:
            try:
                FileHelper.delete_file(command_file.path)
            except Exception:
                # 静默失败
                pass

        self.copied_files.clear()
