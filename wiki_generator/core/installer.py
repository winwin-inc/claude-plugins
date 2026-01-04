"""
命令安装模块

实现命令安装的主流程。
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
from .source_parser import SourceParser
from .file_scanner import FileScanner
from .file_handler import FileHandler
from .config_manager import ConfigManager
from ..utils.git_helper import GitHelper
from ..utils.file_helper import FileHelper
from ..utils.metadata import MetadataExtractor
from ..utils.validator import validate_command_name
from ..utils.error_handler import CommandInstallError
from ..utils.errors import ErrorCode
from ..models.command import InstalledCommand, InstallSource


def install_command(
    source: str,
    command_name: Optional[str] = None,
    conflict_strategy: str = "skip",
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    安装命令

    Args:
        source: 命令来源（Git URL、本地路径、预设名称）
        command_name: 命令名称（可选）
        conflict_strategy: 冲突处理策略（skip、backup、force）
        dry_run: 是否为预览模式

    Returns:
        安装结果字典：
        {
            "success": True/False,
            "command_name": "命令名称",
            "version": "版本号",
            "source": "来源",
            "files": ["文件列表"],
            "error": "错误信息（失败时）",
        }
    """
    config_manager = None
    temp_dir = None

    try:
        # 1. 解析来源
        source_info = SourceParser.resolve_source(source)
        source_type = source_info["type"]
        resolved_source = source_info["resolved"]

        # 2. 根据来源类型处理
        if source_type == "git":
            # Git 仓库：克隆到临时目录
            git_helper = GitHelper(timeout=60)
            temp_dir = git_helper.clone(resolved_source)
            scan_dir = temp_dir

        elif source_type == "local":
            # 本地路径：直接扫描
            scan_dir = resolved_source

        else:
            raise CommandInstallError(
                ErrorCode.RESOLVE_UNKNOWN_TYPE,
                f"不支持的来源类型: {source_type}"
            )

        # 3. 扫描资源
        scanner = FileScanner()
        resources = scanner.discover_resources(scan_dir)

        # 验证资源
        scanner.validate_resources(resources)

        # 4. 提取命令元数据
        command_files = resources.get("commands", [])
        if not command_files:
            raise CommandInstallError(
                ErrorCode.VALIDATE_INVALID_FRONTMATTER,
                "未找到命令文件"
            )

        # 从第一个命令文件提取元数据
        first_command_file = command_files[0]
        metadata = MetadataExtractor.get_command_metadata(first_command_file)

        # 确定命令名称
        if command_name is None:
            command_name = metadata["name"]

        # 验证命令名称
        validate_command_name(command_name)

        # 5. 检查命令是否已存在
        config_manager = ConfigManager()
        config_manager.load()

        existing_command = config_manager.get_installed_command(command_name)
        if existing_command and conflict_strategy == "skip":
            raise CommandInstallError(
                ErrorCode.INSTALL_COMMAND_EXISTS,
                f"命令已存在: {command_name}\n   使用 '--strategy backup' 覆盖，或先卸载"
            )

        # 6. 预览模式
        if dry_run:
            return {
                "success": True,
                "command_name": command_name,
                "version": metadata["version"],
                "source": resolved_source,
                "files": resources.get("commands", []) + resources.get("templates", []),
                "preview": True,
            }

        # 7. 执行安装
        file_handler = FileHandler(conflict_strategy=conflict_strategy)

        # 安装命令文件
        installed_files = []
        for cmd_file in resources.get("commands", []):
            result = file_handler.install_command_file(cmd_file, command_name if cmd_file == first_command_file else None)
            if result:
                installed_files.append(result)

        # 安装模板文件
        for template_file in resources.get("templates", []):
            result = file_handler.install_template_file(template_file)
            if result:
                installed_files.append(result)

        # 8. 记录到配置
        install_source = InstallSource(
            source_type=source_type,
            url=resolved_source,
            description=source_info.get("preset_name", ""),
            latest_version=metadata["version"],
            last_checked=datetime.now().isoformat(),
        )

        installed_command = InstalledCommand(
            name=command_name,
            version=metadata["version"],
            source=install_source,
            installed_at=datetime.now().isoformat(),
            files=installed_files,
            metadata=metadata,
        )

        config_manager.add_installed_command(command_name, installed_command.to_dict())
        config_manager.save()

        # 9. 清理临时目录
        if temp_dir:
            FileHelper.cleanup_temp_dir(temp_dir)

        # 10. 返回成功结果
        return {
            "success": True,
            "command_name": command_name,
            "version": metadata["version"],
            "source": resolved_source,
            "files": [f.path for f in installed_files],
            "installed_at": installed_command.installed_at,
        }

    except Exception as e:
        # 清理临时目录
        if temp_dir:
            FileHelper.cleanup_temp_dir(temp_dir)

        # 错误处理
        if isinstance(e, CommandInstallError):
            return {
                "success": False,
                "error": str(e),
                "error_code": e.error_code,
            }
        else:
            return {
                "success": False,
                "error": f"安装失败: {str(e)}",
            }
