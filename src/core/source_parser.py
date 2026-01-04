"""
来源解析模块

提供命令来源解析功能：检测来源类型（Git、本地、预设）。
"""

import os
import re
from typing import Tuple, Optional
from ..utils.error_handler import CommandInstallError
from ..utils.errors import ErrorCode
from ..core.config_manager import ConfigManager


class SourceType:
    """来源类型常量"""
    LOCAL = "local"
    GIT = "git"
    PRESET = "preset"


class SourceParser:
    """来源解析器"""

    # Git URL 模式
    GIT_PATTERNS = [
        r"^https?://.*",  # HTTPS URL
        r"^git@.*",  # SSH URL
        r"^git://.*",  # Git 协议
        r"github\.com/.*",  # GitHub URL（简写）
        r"gitlab\.com/.*",  # GitLab URL（简写）
    ]

    # 本地路径模式
    LOCAL_PATTERNS = [
        r"^\.",  # 相对路径（./ 或 ../）
        r"^/",  # 绝对路径
        r"^~",  # 用户目录
        r"\.md$",  # Markdown 文件（不区分路径）
    ]

    @staticmethod
    def detect_source_type(source: str) -> str:
        """
        检测来源类型

        Args:
            source: 来源字符串

        Returns:
            来源类型（local、git、preset）

        Raises:
            CommandInstallError: 来源无效时
        """
        if not source or not source.strip():
            raise CommandInstallError(
                ErrorCode.RESOLVE_INVALID_SOURCE,
                "来源不能为空"
            )

        source = source.strip()

        # 1. 优先检测本地路径
        if SourceParser._is_local_path(source):
            return SourceType.LOCAL

        # 2. 检测 Git URL
        if SourceParser._is_git_url(source):
            return SourceType.GIT

        # 3. 默认为预设名称
        return SourceType.PRESET

    @staticmethod
    def _is_local_path(source: str) -> bool:
        """
        判断是否为本地路径

        Args:
            source: 来源字符串

        Returns:
            是否为本地路径
        """
        # 检查本地路径模式
        for pattern in SourceParser.LOCAL_PATTERNS:
            if re.search(pattern, source):
                return True

        return False

    @staticmethod
    def _is_git_url(source: str) -> bool:
        """
        判断是否为 Git URL

        Args:
            source: 来源字符串

        Returns:
            是否为 Git URL
        """
        # 检查 Git URL 模式
        for pattern in SourceParser.GIT_PATTERNS:
            if re.match(pattern, source, re.IGNORECASE):
                return True

        return False

    @staticmethod
    def parse_source(source: str, config_manager: Optional[ConfigManager] = None) -> Tuple[str, str]:
        """
        解析来源

        Args:
            source: 来源字符串
            config_manager: 配置管理器（用于预设解析）

        Returns:
            (来源类型, 标准化路径)

        Raises:
            CommandInstallError: 解析失败时
        """
        source_type = SourceParser.detect_source_type(source)

        if source_type == SourceType.LOCAL:
            # 标准化本地路径
            normalized_path = os.path.expanduser(source)
            normalized_path = os.path.abspath(normalized_path)

            # 检查路径是否存在
            if not os.path.exists(normalized_path):
                raise CommandInstallError(
                    ErrorCode.RESOLVE_INVALID_SOURCE,
                    f"本地路径不存在: {source}"
                )

            return (SourceType.LOCAL, normalized_path)

        elif source_type == SourceType.GIT:
            # 标准化 Git URL
            # 如果是简写格式（如 user/repo），转换为完整 URL
            if "/" in source and not re.match(r"^https?://", source) and not source.startswith("git@"):
                # 假设是 GitHub 简写格式
                normalized_url = f"https://github.com/{source}.git"
            else:
                normalized_url = source

            return (SourceType.GIT, normalized_url)

        elif source_type == SourceType.PRESET:
            # 从配置文件查找预设
            if config_manager is None:
                config_manager = ConfigManager()
                config_manager.load()

            preset_url = config_manager.get_preset_url(source)

            if preset_url is None:
                raise CommandInstallError(
                    ErrorCode.RESOLVE_PRESET_NOT_FOUND,
                    f"预设名称不存在: {source}\n   使用 'list' 命令查看可用预设"
                )

            # 递归解析预设 URL（可能是 Git URL 或本地路径）
            return SourceParser.parse_source(preset_url, config_manager)

        else:
            raise CommandInstallError(
                ErrorCode.RESOLVE_UNKNOWN_TYPE,
                f"无法识别的来源类型: {source}"
            )

    @staticmethod
    def resolve_source(source: str, config_manager: Optional[ConfigManager] = None) -> dict:
        """
        完全解析来源（返回详细信息）

        Args:
            source: 来源字符串
            config_manager: 配置管理器

        Returns:
            来源信息字典：
            {
                "type": "local" | "git" | "preset",
                "original": "原始输入",
                "resolved": "解析后的路径",
                "preset_name": "预设名称（仅 preset 类型）",
            }
        """
        source_type = SourceParser.detect_source_type(source)
        resolved_path = source

        if source_type == SourceType.PRESET:
            if config_manager is None:
                config_manager = ConfigManager()
                config_manager.load()

            preset_url = config_manager.get_preset_url(source)
            if preset_url is None:
                raise CommandInstallError(
                    ErrorCode.RESOLVE_PRESET_NOT_FOUND,
                    f"预设名称不存在: {source}"
                )

            # 重新检测预设 URL 的类型
            actual_type, resolved_path = SourceParser.parse_source(preset_url, config_manager)

            return {
                "type": actual_type,
                "original": source,
                "resolved": resolved_path,
                "preset_name": source,
            }
        else:
            source_type, resolved_path = SourceParser.parse_source(source, config_manager)

            return {
                "type": source_type,
                "original": source,
                "resolved": resolved_path,
            }
