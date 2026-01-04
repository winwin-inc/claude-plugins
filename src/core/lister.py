"""
列表功能模块

实现命令列表和详细信息查询功能。
"""

import os
from typing import Dict, Any, List
from .config_manager import ConfigManager
from ..utils.metadata import MetadataExtractor
from ..utils.formatter import format_table, format_json_output
from ..utils.file_helper import FileHelper
from ..utils.error_handler import CommandInstallError
from ..utils.errors import ErrorCode


def list_commands(output_format: str = "table") -> Dict[str, Any]:
    """
    列出所有已安装的命令

    Args:
        output_format: 输出格式（table、json）

    Returns:
        结果字典：
        {
            "count": 命令数量,
            "output": 格式化输出,
            "total_size": 总占用空间,
        }
    """
    # 加载配置
    config_manager = ConfigManager()
    config_manager.load()

    # 获取已安装命令
    installed_commands = config_manager.get_all_installed_commands()

    # 如果没有命令
    if not installed_commands:
        return {
            "count": 0,
            "output": "没有已安装的命令",
            "total_size": "0 B",
        }

    # 构建命令列表
    commands_data = []
    total_size = 0

    for cmd_name, cmd_dict in installed_commands.items():
        # 从配置中获取基本信息
        cmd_info = {
            "name": cmd_name,
            "description": cmd_dict.get("metadata", {}).get("description", ""),
            "version": cmd_dict.get("version", "1.0.0"),
            "installed_at": cmd_dict.get("installed_at", ""),
        }

        # 计算文件大小
        files = cmd_dict.get("files", [])
        cmd_size = sum(f.get("size", 0) for f in files)
        total_size += cmd_size

        commands_data.append(cmd_info)

    # 格式化输出
    if output_format == "json":
        output = format_json_output({
            "commands": commands_data,
            "count": len(commands_data),
            "total_size": total_size,
        })
    else:
        # 表格格式
        headers = ["命令名称", "描述", "版本", "安装日期"]
        rows = []
        for cmd in commands_data:
            rows.append([
                cmd["name"],
                cmd["description"][:50],  # 限制描述长度
                cmd["version"],
                cmd["installed_at"][:10],  # 只显示日期部分
            ])
        output = format_table(headers, rows)

    # 格式化文件大小
    size_str = FileHelper._format_size(total_size)

    return {
        "count": len(commands_data),
        "output": output,
        "total_size": size_str,
        "commands": commands_data,  # 用于后续处理
    }


def show_command_info(command_name: str) -> Dict[str, Any]:
    """
    显示命令详细信息

    Args:
        command_name: 命令名称

    Returns:
        结果字典：
        {
            "found": True/False,
            "name": "命令名称",
            "version": "版本",
            "description": "描述",
            "author": "作者",
            "source": "来源",
            "installed_at": "安装时间",
            "files": ["文件列表"],
        }
    """
    # 加载配置
    config_manager = ConfigManager()
    config_manager.load()

    # 获取命令信息
    cmd_dict = config_manager.get_installed_command(command_name)

    if cmd_dict is None:
        return {
            "found": False,
            "name": command_name,
        }

    # 提取信息
    from ..models.command import InstalledCommand
    cmd_obj = InstalledCommand.from_dict(cmd_dict)

    # 构建返回信息
    result = {
        "found": True,
        "name": cmd_obj.name,
        "version": cmd_obj.version,
        "description": cmd_obj.metadata.get("description", ""),
        "author": cmd_obj.metadata.get("author", "Unknown"),
        "source": cmd_obj.source.url,
        "installed_at": cmd_obj.installed_at,
        "files": [f.path for f in cmd_obj.files],
    }

    return result


# 添加格式化文件大小的辅助函数
def _format_size(size_bytes: int) -> str:
    """
    格式化文件大小

    Args:
        size_bytes: 字节数

    Returns:
        格式化的大小字符串
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


# 将辅助函数添加到 FileHelper
FileHelper._format_size = staticmethod(_format_size)
