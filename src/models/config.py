"""
配置数据模型

定义命令安装器的配置结构。
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from .command import InstalledCommand, Backup


@dataclass
class InstallSettings:
    """安装设置"""

    auto_update: bool = False  # 是否自动更新
    backup_before_update: bool = True  # 更新前是否备份
    keep_backup_count: int = 3  # 保留备份数量
    conflict_strategy: str = "skip"  # 默认冲突处理策略
    timeout_seconds: int = 60  # 操作超时时间（秒）
    max_retries: int = 3  # 最大重试次数

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "auto_update": self.auto_update,
            "backup_before_update": self.backup_before_update,
            "keep_backup_count": self.keep_backup_count,
            "conflict_strategy": self.conflict_strategy,
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InstallSettings":
        """从字典创建"""
        return cls(
            auto_update=data.get("auto_update", False),
            backup_before_update=data.get("backup_before_update", True),
            keep_backup_count=data.get("keep_backup_count", 3),
            conflict_strategy=data.get("conflict_strategy", "skip"),
            timeout_seconds=data.get("timeout_seconds", 60),
            max_retries=data.get("max_retries", 3),
        )


@dataclass
class InstallSources:
    """安装来源配置"""

    presets: Dict[str, str] = field(default_factory=dict)  # 预设名称到 URL 的映射

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "presets": self.presets,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InstallSources":
        """从字典创建"""
        return cls(
            presets=data.get("presets", {}),
        )


@dataclass
class Config:
    """命令安装器配置"""

    version: str = "1.0.0"  # 配置版本
    installed_commands: Dict[str, InstalledCommand] = field(default_factory=dict)  # 已安装命令
    install_sources: InstallSources = field(default_factory=InstallSources)  # 安装来源
    settings: InstallSettings = field(default_factory=InstallSettings)  # 设置
    backups: Dict[str, Backup] = field(default_factory=dict)  # 备份

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "version": self.version,
            "installed_commands": {
                name: cmd.to_dict() for name, cmd in self.installed_commands.items()
            },
            "install_sources": self.install_sources.to_dict(),
            "settings": self.settings.to_dict(),
            "backups": {
                backup_id: backup.to_dict() for backup_id, backup in self.backups.items()
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """从字典创建"""
        installed_commands = {}
        for name, cmd_data in data.get("installed_commands", {}).items():
            installed_commands[name] = InstalledCommand.from_dict(cmd_data)

        backups = {}
        for backup_id, backup_data in data.get("backups", {}).items():
            backups[backup_id] = Backup.from_dict(backup_data)

        return cls(
            version=data.get("version", "1.0.0"),
            installed_commands=installed_commands,
            install_sources=InstallSources.from_dict(data.get("install_sources", {})),
            settings=InstallSettings.from_dict(data.get("settings", {})),
            backups=backups,
        )
