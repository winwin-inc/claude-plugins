"""
格式化输出模块

提供统一的输出格式化功能。
"""

import click
from typing import Any, Dict, List


def format_success(message: str) -> None:
    """
    格式化成功消息（绿色）

    Args:
        message: 消息内容
    """
    click.secho(message, fg="green", bold=True)


def format_info(message: str) -> None:
    """
    格式化信息消息（蓝色）

    Args:
        message: 消息内容
    """
    click.secho(message, fg="blue")


def format_warning(message: str) -> None:
    """
    格式化警告消息（黄色）

    Args:
        message: 消息内容
    """
    click.secho(message, fg="yellow", bold=True)


def format_error(message: str) -> None:
    """
    格式化错误消息（红色）

    Args:
        message: 消息内容
    """
    click.secho(message, fg="red", bold=True)


def format_table(headers: List[str], rows: List[List[str]]) -> str:
    """
    格式化表格输出

    Args:
        headers: 表头列表
        rows: 行数据列表（每行是一个字符串列表）

    Returns:
        格式化的表格字符串
    """
    # 计算每列的最大宽度
    col_widths = [len(h) for h in headers]

    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    # 构建表格
    lines = []

    # 表头
    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    lines.append(header_line)

    # 分隔线
    separator = "-+-".join("-" * w for w in col_widths)
    lines.append(separator)

    # 数据行
    for row in rows:
        row_line = " | ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths))
        lines.append(row_line)

    return "\n".join(lines)


def format_install_summary(result: Dict[str, Any]) -> str:
    """
    格式化安装摘要

    Args:
        result: 安装结果字典

    Returns:
        格式化的摘要字符串
    """
    lines = [
        f"✓ 命令安装成功: {result['command_name']}",
        f"  版本: {result['version']}",
        f"  来源: {result['source']}",
        f"  文件数: {len(result['files'])}",
    ]

    if "installed_at" in result:
        lines.append(f"  安装时间: {result['installed_at']}")

    return "\n".join(lines)


def format_list_output(commands: List[Dict[str, Any]]) -> str:
    """
    格式化命令列表输出

    Args:
        commands: 命令字典列表

    Returns:
        格式化的表格字符串
    """
    if not commands:
        return "没有已安装的命令"

    headers = ["命令名称", "描述", "版本", "安装日期"]
    rows = []

    for cmd in commands:
        rows.append([
            cmd.get("name", ""),
            cmd.get("description", "")[:50],  # 限制描述长度
            cmd.get("version", ""),
            cmd.get("installed_at", ""),
        ])

    return format_table(headers, rows)


def format_json_output(data: Dict[str, Any]) -> str:
    """
    格式化 JSON 输出

    Args:
        data: 要输出的数据字典

    Returns:
        JSON 字符串
    """
    import json

    return json.dumps(data, ensure_ascii=False, indent=2)


def format_file_list(files: List[str], prefix: str = "  ") -> str:
    """
    格式化文件列表

    Args:
        files: 文件路径列表
        prefix: 每行前缀

    Returns:
        格式化的文件列表字符串
    """
    return "\n".join(f"{prefix}- {f}" for f in files)
