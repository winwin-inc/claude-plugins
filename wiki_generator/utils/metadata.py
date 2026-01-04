"""
元数据提取模块

从 Markdown 文件的 frontmatter 中提取命令元数据。
"""

import re
import json
from typing import Dict, Any, Optional
from .error_handler import CommandInstallError
from .errors import ErrorCode


class MetadataExtractor:
    """元数据提取器"""

    # 支持的 frontmatter 格式
    FRONTMATTER_PATTERNS = [
        # YAML 格式（---包裹）
        r"^---\s*\n(.*?)\n---\s*\n(.*)",
        # JSON 格式（{{{包裹}}}）
        r"^\{\{\{\s*\n(.*?)\n\}}}\s*\n(.*)",
        # TOML 格式（+++包裹）
        r"^\+\+\+\s*\n(.*?)\n\+\+\+\s*\n(.*)",
    ]

    @staticmethod
    def extract_from_markdown(file_path: str) -> Dict[str, Any]:
        """
        从 Markdown 文件提取元数据

        Args:
            file_path: Markdown 文件路径

        Returns:
            元数据字典

        Raises:
            CommandInstallError: 文件读取或解析失败时
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 尝试各种 frontmatter 格式
            for pattern in MetadataExtractor.FRONTMATTER_PATTERNS:
                match = re.match(pattern, content, re.DOTALL)
                if match:
                    frontmatter_text = match.group(1)
                    body_text = match.group(2)

                    # 解析 frontmatter
                    metadata = MetadataExtractor.parse_frontmatter(frontmatter_text)
                    metadata["body"] = body_text.strip()
                    return metadata

            # 没有找到 frontmatter
            return {
                "body": content.strip()
            }

        except UnicodeDecodeError:
            raise CommandInstallError(
                ErrorCode.VALIDATE_FILE_ENCODING,
                f"文件编码错误（应为 UTF-8）: {file_path}"
            )
        except Exception as e:
            raise CommandInstallError(
                ErrorCode.VALIDATE_INVALID_FRONTMATTER,
                f"读取文件失败: {file_path}\n   {str(e)}"
            )

    @staticmethod
    def parse_frontmatter(text: str) -> Dict[str, Any]:
        """
        解析 frontmatter 文本

        Args:
            text: frontmatter 文本

        Returns:
            元数据字典

        Raises:
            CommandInstallError: 解析失败时
        """
        # 尝试 YAML 格式
        try:
            import yaml
            return yaml.safe_load(text) or {}
        except Exception:
            pass

        # 尝试 JSON 格式
        try:
            return json.loads(text)
        except Exception:
            pass

        # 如果都失败，返回空字典
        # 不抛出错误，因为 frontmatter 是可选的
        return {}

    @staticmethod
    def get_command_metadata(file_path: str) -> Dict[str, Any]:
        """
        获取命令元数据（提取常用字段）

        Args:
            file_path: 命令文件路径

        Returns:
            命令元数据字典，包含：
            - name: 命令名称
            - description: 描述
            - version: 版本
            - author: 作者
            - argument_hint: 参数提示
            - allowed_tools: 允许的工具
        """
        metadata = MetadataExtractor.extract_from_markdown(file_path)

        # 提取命令名称（从文件名）
        import os
        name = os.path.basename(file_path).replace(".md", "")

        # 构建标准化的元数据
        return {
            "name": metadata.get("name") or name,
            "description": metadata.get("description", ""),
            "version": metadata.get("version", "1.0.0"),
            "author": metadata.get("author", "Unknown"),
            "argument_hint": metadata.get("argument-hint", ""),
            "allowed_tools": metadata.get("allowed-tools", []),
            "metadata": metadata,  # 保存原始元数据
        }

    @staticmethod
    def extract_from_json(file_path: str) -> Dict[str, Any]:
        """
        从 JSON 文件提取元数据

        Args:
            file_path: JSON 文件路径

        Returns:
            元数据字典

        Raises:
            CommandInstallError: 文件读取或解析失败时
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)

        except json.JSONDecodeError as e:
            raise CommandInstallError(
                ErrorCode.CONFIG_INVALID_FORMAT,
                f"JSON 格式无效: {file_path}\n   {str(e)}"
            )
        except Exception as e:
            raise CommandInstallError(
                ErrorCode.CONFIG_LOAD_FAILED,
                f"读取 JSON 文件失败: {file_path}\n   {str(e)}"
            )

    @staticmethod
    def validate_command_metadata(metadata: Dict[str, Any]) -> bool:
        """
        验证命令元数据完整性

        Args:
            metadata: 元数据字典

        Returns:
            是否有效

        Raises:
            CommandInstallError: 元数据无效时
        """
        # 必需字段
        required_fields = ["name", "description"]

        for field in required_fields:
            if field not in metadata or not metadata[field]:
                raise CommandInstallError(
                    ErrorCode.VALIDATE_INVALID_FRONTMATTER,
                    f"缺少必需字段: {field}"
                )

        # 验证版本号格式
        if "version" in metadata:
            from .validator import validate_version
            validate_version(metadata["version"])

        return True
