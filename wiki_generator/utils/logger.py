"""日志工具模块。

提供简单的日志输出功能。
"""

import sys
from typing import Optional

# 导入 click
try:
    import click
except ImportError:
    # 如果 click 不可用，提供回退实现
    class click:
        @staticmethod
        def echo(message: str, err: bool = False):
            file = sys.stderr if err else sys.stdout
            file.write(message + "\n")


def log_info(message: str) -> None:
    """输出信息日志。

    Args:
        message: 日志消息
    """
    click.echo(message)


def log_success(message: str) -> None:
    """输出成功日志。

    Args:
        message: 日志消息
    """
    click.echo(f"✅ {message}")


def log_warning(message: str) -> None:
    """输出警告日志。

    Args:
        message: 日志消息
    """
    click.echo(f"⚠️  {message}", err=True)


def log_error(message: str) -> None:
    """输出错误日志。

    Args:
        message: 日志消息
    """
    click.echo(f"❌ {message}", err=True)


def log_verbose(message: str, verbose: bool = False) -> None:
    """输出详细日志。

    Args:
        message: 日志消息
        verbose: 是否显示
    """
    if verbose:
        click.echo(f"🔍 {message}")
