"""
错误处理模块

提供统一的错误处理和格式化功能。
"""

import sys
from typing import Optional, Dict, Any
from .errors import ErrorCode, get_error_message


class CommandInstallError(Exception):
    """命令安装器基础异常类"""

    def __init__(self, error_code: ErrorCode, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """
        初始化异常

        Args:
            error_code: 错误码
            message: 自定义错误消息（可选）
            details: 额外错误详情（可选）
        """
        self.error_code = error_code
        self.message = message or get_error_message(error_code)
        self.details = details or {}

        super().__init__(self.message)


def format_error(error: Exception) -> str:
    """
    格式化错误消息

    Args:
        error: 异常对象

    Returns:
        格式化的错误消息字符串
    """
    if isinstance(error, CommandInstallError):
        msg = f"❌ 错误: {error.message}"

        if error.details:
            msg += f"\n   详情: {error.details}"

        # 添加建议
        suggestion = get_error_suggestion(error.error_code)
        if suggestion:
            msg += f"\n   建议: {suggestion}"

        return msg
    else:
        return f"❌ 未知错误: {str(error)}"


def get_error_suggestion(error_code: ErrorCode) -> Optional[str]:
    """
    根据错误码提供建议

    Args:
        error_code: 错误码

    Returns:
        建议字符串或 None
    """
    suggestions = {
        ErrorCode.RESOLVE_INVALID_SOURCE: "请检查来源 URL 或路径是否正确",
        ErrorCode.RESOLVE_PRESET_NOT_FOUND: "使用 'list' 命令查看可用的预设名称",

        ErrorCode.DOWNLOAD_GIT_CLONE_FAILED: "请检查网络连接和仓库 URL 是否正确",
        ErrorCode.DOWNLOAD_NETWORK_ERROR: "请检查网络连接",
        ErrorCode.DOWNLOAD_TIMEOUT: "操作超时，请重试",

        ErrorCode.VALIDATE_INVALID_COMMAND_NAME: "命令名称应以小写字母开头，允许连字符，长度 2-50",
        ErrorCode.VALIDATE_INVALID_VERSION: "版本号应符合 SemVer 格式（如 1.0.0）",
        ErrorCode.VALIDATE_INVALID_FRONTMATTER: "请检查命令文件的 frontmatter 格式",

        ErrorCode.INSTALL_COMMAND_EXISTS: "使用 '--strategy backup' 覆盖现有命令，或先卸载",
        ErrorCode.INSTALL_FILE_CONFLICT: "使用 '--strategy skip' 跳过冲突，或 '--strategy backup' 备份后覆盖",
        ErrorCode.INSTALL_PERMISSION_DENIED: "请检查目录权限",
        ErrorCode.INSTALL_DISK_SPACE_INSUFFICIENT: "请清理磁盘空间",

        ErrorCode.UPDATE_NOT_FOUND: "使用 'list' 命令查看已安装的命令",
        ErrorCode.UPDATE_NO_UPDATE_AVAILABLE: "当前已是最新版本",
        ErrorCode.UPDATE_BACKUP_FAILED: "请检查磁盘空间和权限",

        ErrorCode.UNINSTALL_NOT_FOUND: "使用 'list' 命令查看已安装的命令",
        ErrorCode.UNINSTALL_DELETE_FAILED: "请检查文件权限",

        ErrorCode.CONFIG_LOAD_FAILED: "请检查配置文件是否存在且格式正确",
        ErrorCode.CONFIG_SAVE_FAILED: "请检查目录权限",
    }

    return suggestions.get(error_code)


def handle_error(error: Exception, exit_on_error: bool = True) -> None:
    """
    统一错误处理函数

    Args:
        error: 异常对象
        exit_on_error: 是否在错误后退出程序
    """
    error_msg = format_error(error)
    print(error_msg, file=sys.stderr)

    if exit_on_error:
        # 根据错误类型设置不同的退出码
        if isinstance(error, CommandInstallError):
            sys.exit(1)
        else:
            sys.exit(2)
