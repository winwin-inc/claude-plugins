"""
配置管理模块

提供配置文件的加载、保存、更新等功能。
"""

import os
import json
import fcntl
from typing import Optional
from datetime import datetime
from ..models.config import Config
from ..utils.error_handler import CommandInstallError
from ..utils.errors import ErrorCode
from ..utils.validator import validate_json_file


class ConfigManager:
    """配置管理器"""

    DEFAULT_CONFIG_PATH = ".claude/command-install.json"
    LOCK_TIMEOUT = 10  # 锁超时时间（秒）

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器

        Args:
            config_path: 配置文件路径（可选，默认为 .claude/command-install.json）
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config: Optional[Config] = None
        self.lock_fd = None

    def load(self) -> Config:
        """
        加载配置文件

        Returns:
            配置对象

        Raises:
            CommandInstallError: 加载失败时
        """
        # 如果配置已加载，直接返回
        if self.config is not None:
            return self.config

        # 如果配置文件不存在，创建默认配置
        if not os.path.exists(self.config_path):
            self.config = Config()
            self.save()
            return self.config

        # 验证 JSON 格式
        try:
            validate_json_file(self.config_path)
        except CommandInstallError as e:
            raise CommandInstallError(
                ErrorCode.CONFIG_LOAD_FAILED,
                f"配置文件格式错误: {self.config_path}\n   {str(e)}"
            )

        # 加载配置文件
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.config = Config.from_dict(data)

        except json.JSONDecodeError as e:
            raise CommandInstallError(
                ErrorCode.CONFIG_LOAD_FAILED,
                f"配置文件 JSON 解析失败: {self.config_path}\n   {str(e)}"
            )
        except Exception as e:
            raise CommandInstallError(
                ErrorCode.CONFIG_LOAD_FAILED,
                f"加载配置文件失败: {self.config_path}\n   {str(e)}"
            )

        return self.config

    def save(self) -> None:
        """
        保存配置文件

        Raises:
            CommandInstallError: 保存失败时
        """
        if self.config is None:
            raise CommandInstallError(
                ErrorCode.CONFIG_SAVE_FAILED,
                "没有可保存的配置"
            )

        # 确保目录存在
        config_dir = os.path.dirname(self.config_path)
        if config_dir:
            os.makedirs(config_dir, exist_ok=True)

        # 保存配置文件
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config.to_dict(), f, ensure_ascii=False, indent=2)

        except Exception as e:
            raise CommandInstallError(
                ErrorCode.CONFIG_SAVE_FAILED,
                f"保存配置文件失败: {self.config_path}\n   {str(e)}"
            )

    def acquire_lock(self) -> bool:
        """
        获取文件锁

        Returns:
            是否成功获取锁
        """
        if self.lock_fd is not None:
            return True  # 已经持有锁

        try:
            lock_file = self.config_path + ".lock"
            self.lock_fd = open(lock_file, "w")

            # 尝试获取锁（非阻塞）
            fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True

        except (IOError, OSError):
            # 获取锁失败
            self.lock_fd = None
            return False

    def release_lock(self) -> None:
        """释放文件锁"""
        if self.lock_fd is not None:
            try:
                fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_UN)
                self.lock_fd.close()
            except Exception:
                pass
            finally:
                self.lock_fd = None

    def __enter__(self):
        """上下文管理器入口"""
        self.acquire_lock()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.release_lock()

    def add_installed_command(self, command_name: str, command_data: dict) -> None:
        """
        添加已安装命令

        Args:
            command_name: 命令名称
            command_data: 命令数据
        """
        if self.config is None:
            self.load()

        from ..models.command import InstalledCommand
        self.config.installed_commands[command_name] = InstalledCommand.from_dict(command_data)

    def remove_installed_command(self, command_name: str) -> None:
        """
        移除已安装命令

        Args:
            command_name: 命令名称
        """
        if self.config is None:
            self.load()

        if command_name in self.config.installed_commands:
            del self.config.installed_commands[command_name]

    def get_installed_command(self, command_name: str):
        """
        获取已安装命令

        Args:
            command_name: 命令名称

        Returns:
            命令对象或 None
        """
        if self.config is None:
            self.load()

        return self.config.installed_commands.get(command_name)

    def add_backup(self, backup_id: str, backup_data: dict) -> None:
        """
        添加备份

        Args:
            backup_id: 备份 ID
            backup_data: 备份数据
        """
        if self.config is None:
            self.load()

        from ..models.command import Backup
        self.config.backups[backup_id] = Backup.from_dict(backup_data)

        # 清理旧备份
        self.cleanup_old_backups()

    def cleanup_old_backups(self) -> None:
        """清理旧备份（保留数量由 settings.keep_backup_count 决定）"""
        if self.config is None:
            self.load()

        keep_count = self.config.settings.keep_backup_count

        # 按时间戳排序备份
        backups_sorted = sorted(
            self.config.backups.items(),
            key=lambda x: x[1].timestamp,
            reverse=True
        )

        # 保留最新的 N 个备份
        backups_to_keep = backups_sorted[:keep_count]
        backups_to_remove = backups_sorted[keep_count:]

        # 删除旧备份
        for backup_id, _ in backups_to_remove:
            del self.config.backups[backup_id]

    def add_preset(self, preset_name: str, url: str, description: str = "") -> None:
        """
        添加预设来源

        Args:
            preset_name: 预设名称
            url: URL 或路径
            description: 描述
        """
        if self.config is None:
            self.load()

        self.config.install_sources.presets[preset_name] = url

    def get_preset_url(self, preset_name: str) -> Optional[str]:
        """
        获取预设 URL

        Args:
            preset_name: 预设名称

        Returns:
            URL 或 None
        """
        if self.config is None:
            self.load()

        return self.config.install_sources.presets.get(preset_name)

    def get_all_installed_commands(self) -> dict:
        """
        获取所有已安装命令

        Returns:
            命令字典
        """
        if self.config is None:
            self.load()

        return self.config.installed_commands
