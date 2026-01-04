"""
文件扫描模块

提供资源发现和目录结构检测功能。
"""

import os
from typing import List, Dict, Any
from pathlib import Path
from ..utils.error_handler import CommandInstallError
from ..utils.errors import ErrorCode


class FileScanner:
    """文件扫描器"""

    # 支持的目录结构类型
    STRUCTURE_STANDARD = "standard"  # 标准结构（commands/、templates/）
    STRUCTURE_FLAT = "flat"  # 扁平结构（根目录）
    STRUCTURE_CUSTOM = "custom"  # 自定义结构

    # 命令文件模式
    COMMAND_FILE_PATTERNS = ["*.md"]
    TEMPLATE_FILE_PATTERNS = ["*.template", "*.md.template"]
    CONFIG_FILE_PATTERNS = ["command-install.json", "package.json"]

    @staticmethod
    def detect_structure(directory: str) -> str:
        """
        检测目录结构类型

        Args:
            directory: 目录路径

        Returns:
            结构类型（standard、flat、custom）
        """
        # 检查标准结构
        commands_dir = os.path.join(directory, "commands")
        templates_dir = os.path.join(directory, "templates")

        if os.path.isdir(commands_dir) and os.path.isdir(templates_dir):
            return FileScanner.STRUCTURE_STANDARD

        # 检查扁平结构
        md_files = list(Path(directory).glob("*.md"))
        if md_files:
            return FileScanner.STRUCTURE_FLAT

        # 默认为自定义结构
        return FileScanner.STRUCTURE_CUSTOM

    @staticmethod
    def discover_resources(directory: str) -> Dict[str, List[str]]:
        """
        发现资源文件

        Args:
            directory: 扫描目录

        Returns:
            资源字典：
            {
                "commands": ["命令文件路径列表"],
                "templates": ["模板文件路径列表"],
                "configs": ["配置文件路径列表"],
            }
        """
        structure = FileScanner.detect_structure(directory)

        if structure == FileScanner.STRUCTURE_STANDARD:
            return FileScanner._scan_standard_structure(directory)
        elif structure == FileScanner.STRUCTURE_FLAT:
            return FileScanner._scan_flat_structure(directory)
        else:
            return FileScanner._scan_custom_structure(directory)

    @staticmethod
    def _scan_standard_structure(directory: str) -> Dict[str, List[str]]:
        """
        扫描标准结构

        Args:
            directory: 目录路径

        Returns:
            资源字典
        """
        resources = {
            "commands": [],
            "templates": [],
            "configs": [],
        }

        # 扫描 commands/ 目录
        commands_dir = os.path.join(directory, "commands")
        if os.path.isdir(commands_dir):
            for pattern in FileScanner.COMMAND_FILE_PATTERNS:
                for file_path in Path(commands_dir).glob(pattern):
                    if file_path.is_file():
                        resources["commands"].append(str(file_path))

        # 扫描 templates/ 目录
        templates_dir = os.path.join(directory, "templates")
        if os.path.isdir(templates_dir):
            for pattern in FileScanner.TEMPLATE_FILE_PATTERNS:
                for file_path in Path(templates_dir).rglob(pattern):
                    if file_path.is_file():
                        resources["templates"].append(str(file_path))

        # 扫描配置文件
        for pattern in FileScanner.CONFIG_FILE_PATTERNS:
            for file_path in Path(directory).glob(pattern):
                if file_path.is_file():
                    resources["configs"].append(str(file_path))

        return resources

    @staticmethod
    def _scan_flat_structure(directory: str) -> Dict[str, List[str]]:
        """
        扫描扁平结构

        Args:
            directory: 目录路径

        Returns:
            资源字典
        """
        resources = {
            "commands": [],
            "templates": [],
            "configs": [],
        }

        # 扫描命令文件（根目录的 .md 文件）
        for pattern in FileScanner.COMMAND_FILE_PATTERNS:
            for file_path in Path(directory).glob(pattern):
                if file_path.is_file():
                    # 排除 README
                    if file_path.name.lower() != "readme.md":
                        resources["commands"].append(str(file_path))

        # 扫描模板文件
        for pattern in FileScanner.TEMPLATE_FILE_PATTERNS:
            for file_path in Path(directory).rglob(pattern):
                if file_path.is_file():
                    resources["templates"].append(str(file_path))

        # 扫描配置文件
        for pattern in FileScanner.CONFIG_FILE_PATTERNS:
            for file_path in Path(directory).glob(pattern):
                if file_path.is_file():
                    resources["configs"].append(str(file_path))

        return resources

    @staticmethod
    def _scan_custom_structure(directory: str) -> Dict[str, List[str]]:
        """
        扫描自定义结构（递归扫描）

        Args:
            directory: 目录路径

        Returns:
            资源字典
        """
        resources = {
            "commands": [],
            "templates": [],
            "configs": [],
        }

        # 递归扫描所有文件
        for root, dirs, files in os.walk(directory):
            # 跳过隐藏目录和 .git
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != ".git"]

            for file_name in files:
                file_path = os.path.join(root, file_name)

                # 分类文件
                if file_name.endswith(".md"):
                    # 排除 README
                    if file_name.lower() != "readme.md":
                        resources["commands"].append(file_path)

                elif ".template" in file_name:
                    resources["templates"].append(file_path)

                elif file_name in FileScanner.CONFIG_FILE_PATTERNS:
                    resources["configs"].append(file_path)

        return resources

    @staticmethod
    def validate_resources(resources: Dict[str, List[str]]) -> bool:
        """
        验证资源有效性

        Args:
            resources: 资源字典

        Returns:
            是否有效

        Raises:
            CommandInstallError: 资源无效时
        """
        # 检查是否有命令文件
        if not resources.get("commands"):
            raise CommandInstallError(
                ErrorCode.VALIDATE_INVALID_FRONTMATTER,
                "未找到任何命令文件（.md）"
            )

        # 验证文件存在性
        all_files = (
            resources.get("commands", []) +
            resources.get("templates", []) +
            resources.get("configs", [])
        )

        for file_path in all_files:
            if not os.path.isfile(file_path):
                raise CommandInstallError(
                    ErrorCode.VALIDATE_INVALID_FRONTMATTER,
                    f"文件不存在: {file_path}"
                )

        return True

    @staticmethod
    def get_resource_summary(resources: Dict[str, List[str]]) -> str:
        """
        获取资源摘要

        Args:
            resources: 资源字典

        Returns:
            摘要字符串
        """
        lines = [
            "发现资源:",
            f"  命令文件: {len(resources.get('commands', []))} 个",
            f"  模板文件: {len(resources.get('templates', []))} 个",
            f"  配置文件: {len(resources.get('configs', []))} 个",
        ]

        return "\n".join(lines)
