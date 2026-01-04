"""
Wiki Generator CLI 安装工具

一个轻量级的 Python 命令行工具，用于将 Claude Code 自定义 Wiki 命令和模板安装到项目中。
通过 `uvx wiki-generator` 命令即可一键完成所有安装配置。

版本: 1.0.0
作者: Repo Wiki Generator Team
许可: MIT
"""

__version__ = "1.0.0"
__author__ = "Repo Wiki Generator Team"
__license__ = "MIT"

# 自定义异常类型


class InstallerError(Exception):
    """安装器基础异常类

    用于表示安装过程中的所有错误。
    """

    def __init__(self, message: str, details: str | None = None):
        """初始化异常

        Args:
            message: 错误消息（用户可见）
            details: 错误详情（用于调试）
        """
        self.message = message
        self.details = details
        super().__init__(self.message)


class RollbackError(InstallerError):
    """回滚失败异常

    当安装失败且回滚已安装文件时发生错误。
    这是一个严重错误，表示系统可能处于不一致状态。
    """

    def __init__(self, message: str, failed_files: list[str] | None = None):
        """初始化回滚异常

        Args:
            message: 错误消息
            failed_files: 回滚失败的文件列表
        """
        self.failed_files = failed_files or []
        super().__init__(message, details=f"Failed files: {self.failed_files}")


class ValidationError(InstallerError):
    """配置验证错误异常

    当配置文件格式不正确或包含无效值时抛出。
    """

    def __init__(
        self,
        field: str,
        message: str,
        expected: str | None = None,
        actual: str | None = None,
    ):
        """初始化验证错误

        Args:
            field: 出错字段名
            message: 错误描述
            expected: 期望的值类型或范围
            actual: 实际值（用于调试）
        """
        self.field = field
        self.message = message
        self.expected = expected
        self.actual = actual
        full_message = f"{field}: {message}"
        if expected:
            full_message += f" (expected: {expected})"
        super().__init__(full_message, details=f"actual: {actual}")


__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "InstallerError",
    "RollbackError",
    "ValidationError",
]
