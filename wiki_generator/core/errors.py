"""统一的错误处理模块。

此模块定义了所有自定义异常类和错误处理工具。
"""

from typing import Optional, List
from pathlib import Path


class WikiGeneratorError(Exception):
    """Wiki Generator 基础异常类。"""

    def __init__(self, message: str, suggestion: Optional[str] = None):
        """初始化异常。

        Args:
            message: 错误消息
            suggestion: 修复建议
        """
        self.message = message
        self.suggestion = suggestion
        super().__init__(self.message)

    def __str__(self) -> str:
        """返回格式化的错误消息。"""
        if self.suggestion:
            return f"{self.message}\n   建议: {self.suggestion}"
        return self.message


class ConfigError(WikiGeneratorError):
    """配置相关错误。"""

    pass


class ValidationError(ConfigError):
    """配置验证错误。"""

    def __init__(self, message: str, errors: List[str]):
        """初始化验证错误。

        Args:
            message: 错误消息
            errors: 错误列表
        """
        self.errors = errors
        suggestion = "请检查配置文件格式和字段值"
        super().__init__(message, suggestion)


class InstallationError(WikiGeneratorError):
    """文件安装错误。"""

    pass


class MigrationError(WikiGeneratorError):
    """配置迁移错误。"""

    pass


class TemplateError(WikiGeneratorError):
    """模板相关错误。"""

    pass


class FileNotFoundError(WikiGeneratorError):
    """文件或目录不存在错误。"""

    def __init__(self, path: Path, file_type: str = "文件"):
        """初始化文件不存在错误。

        Args:
            path: 文件路径
            file_type: 文件类型描述
        """
        message = f"{file_type}不存在: {path}"
        suggestion = f"请检查路径是否正确，或运行 'wiki-generator --init' 创建"
        super().__init__(message, suggestion)


def format_error_message(error: Exception, context: Optional[str] = None) -> str:
    """格式化错误消息以供用户显示。

    Args:
        error: 异常对象
        context: 上下文信息

    Returns:
        格式化的错误消息
    """
    lines = []

    if context:
        lines.append(f"❌ {context}")

    if isinstance(error, WikiGeneratorError):
        lines.append(f"   {error.message}")
        if error.suggestion:
            lines.append(f"   {error.suggestion}")
    else:
        lines.append(f"   错误: {str(error)}")

    return "\n".join(lines)


def handle_error(error: Exception, context: Optional[str] = None, exit_code: int = 1) -> None:
    """处理错误并退出。

    Args:
        error: 异常对象
        context: 上下文信息
        exit_code: 退出码
    """
    import click
    click.echo(format_error_message(error, context), err=True)
    raise SystemExit(exit_code)
