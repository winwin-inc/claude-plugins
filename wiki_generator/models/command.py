"""
命令数据模型

定义命令、文件、备份、来源等数据结构。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class CommandFile:
    """命令文件模型"""

    path: str  # 文件路径
    file_type: str  # 文件类型（command、template、config）
    size: int = 0  # 文件大小（字节）
    checksum: str = ""  # SHA-256 校验和

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "path": self.path,
            "type": self.file_type,
            "size": self.size,
            "checksum": self.checksum,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CommandFile":
        """从字典创建"""
        return cls(
            path=data["path"],
            file_type=data["type"],
            size=data.get("size", 0),
            checksum=data.get("checksum", ""),
        )


@dataclass
class Backup:
    """备份模型"""

    backup_id: str  # 备份 ID（时间戳）
    timestamp: str  # 备份时间
    reason: str  # 备份原因（update、uninstall）
    files: List[CommandFile] = field(default_factory=list)  # 备份的文件列表

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "backup_id": self.backup_id,
            "timestamp": self.timestamp,
            "reason": self.reason,
            "files": [f.to_dict() for f in self.files],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Backup":
        """从字典创建"""
        return cls(
            backup_id=data["backup_id"],
            timestamp=data["timestamp"],
            reason=data["reason"],
            files=[CommandFile.from_dict(f) for f in data.get("files", [])],
        )


@dataclass
class InstallSource:
    """安装来源模型"""

    source_type: str  # 来源类型（git、local、preset）
    url: str  # 来源 URL 或路径
    description: str = ""  # 来源描述
    latest_version: str = ""  # 最新版本
    last_checked: str = ""  # 最后检查时间

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "type": self.source_type,
            "url": self.url,
            "description": self.description,
            "latest_version": self.latest_version,
            "last_checked": self.last_checked,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InstallSource":
        """从字典创建"""
        return cls(
            source_type=data["type"],
            url=data["url"],
            description=data.get("description", ""),
            latest_version=data.get("latest_version", ""),
            last_checked=data.get("last_checked", ""),
        )


@dataclass
class InstalledCommand:
    """已安装命令模型"""

    name: str  # 命令名称
    version: str  # 版本号
    source: InstallSource  # 安装来源
    installed_at: str  # 安装时间
    files: List[CommandFile] = field(default_factory=list)  # 文件列表
    metadata: Dict[str, Any] = field(default_factory=dict)  # 额外元数据

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "version": self.version,
            "source": self.source.to_dict(),
            "installed_at": self.installed_at,
            "files": [f.to_dict() for f in self.files],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InstalledCommand":
        """从字典创建"""
        return cls(
            name=data["name"],
            version=data["version"],
            source=InstallSource.from_dict(data["source"]),
            installed_at=data["installed_at"],
            files=[CommandFile.from_dict(f) for f in data.get("files", [])],
            metadata=data.get("metadata", {}),
        )
