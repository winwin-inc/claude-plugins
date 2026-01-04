"""
信息显示模块

显示命令的详细信息。
"""

from typing import Dict, Any
from .lister import show_command_info
from ..utils.error_handler import CommandInstallError
from ..utils.errors import ErrorCode


def show_info(command_name: str) -> Dict[str, Any]:
    """
    显示命令详细信息（包装函数，保持与 lister 一致的接口）

    Args:
        command_name: 命令名称

    Returns:
        结果字典
    """
    return show_command_info(command_name)
