"""
验证器模块

提供各种验证函数：命令名称、版本号、校验和等。
"""

import re
import hashlib
from typing import Optional
from .errors import ErrorCode
from .error_handler import CommandInstallError


def validate_command_name(name: str) -> bool:
    """
    验证命令名称格式

    规则：
    - 以小写字母开头
    - 只允许小写字母、数字和连字符
    - 长度 2-50 个字符
    - 不能以连字符开头或结尾
    - 不能有连续的连字符

    Args:
        name: 命令名称

    Returns:
        是否有效

    Raises:
        CommandInstallError: 名称无效时
    """
    if not name:
        raise CommandInstallError(
            ErrorCode.VALIDATE_INVALID_COMMAND_NAME,
            "命令名称不能为空"
        )

    if len(name) < 2 or len(name) > 50:
        raise CommandInstallError(
            ErrorCode.VALIDATE_INVALID_COMMAND_NAME,
            f"命令名称长度必须在 2-50 个字符之间（当前：{len(name)}）"
        )

    # 正则表达式验证
    pattern = r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$"
    if not re.match(pattern, name):
        raise CommandInstallError(
            ErrorCode.VALIDATE_INVALID_COMMAND_NAME,
            "命令名称应以小写字母开头，只允许小写字母、数字和连字符，不能有连续连字符"
        )

    return True


def validate_version(version: str) -> bool:
    """
    验证版本号格式（SemVer）

    格式：MAJOR.MINOR.PATCH
    - MAJOR、MINOR、PATCH 都是非负整数
    - 允许前缀 "v" 或 "V"
    - 允许预发布标签（如 -alpha.1、-beta.2）
    - 允许构建元数据（如 +001、opt+hash）

    Args:
        version: 版本字符串

    Returns:
        是否有效

    Raises:
        CommandInstallError: 版本号无效时
    """
    if not version:
        raise CommandInstallError(
            ErrorCode.VALIDATE_INVALID_VERSION,
            "版本号不能为空"
        )

    # 移除可能的 v 前缀
    version_clean = version.lstrip("vV")

    # SemVer 正则表达式（简化版）
    pattern = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"

    if not re.match(pattern, version_clean):
        raise CommandInstallError(
            ErrorCode.VALIDATE_INVALID_VERSION,
            f"版本号 '{version}' 不符合 SemVer 格式（如 1.0.0）"
        )

    return True


def calculate_checksum(file_path: str, algorithm: str = "sha256") -> str:
    """
    计算文件的校验和

    Args:
        file_path: 文件路径
        algorithm: 哈希算法（默认 sha256）

    Returns:
        十六进制校验和字符串

    Raises:
        CommandInstallError: 文件读取失败时
    """
    try:
        hash_func = hashlib.new(algorithm)

        with open(file_path, "rb") as f:
            # 分块读取大文件
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)

        return hash_func.hexdigest()

    except FileNotFoundError:
        raise CommandInstallError(
            ErrorCode.VALIDATE_CHECKSUM_MISMATCH,
            f"文件不存在: {file_path}"
        )
    except PermissionError:
        raise CommandInstallError(
            ErrorCode.VALIDATE_CHECKSUM_MISMATCH,
            f"无权限读取文件: {file_path}"
        )
    except Exception as e:
        raise CommandInstallError(
            ErrorCode.VALIDATE_CHECKSUM_MISMATCH,
            f"计算校验和失败: {str(e)}"
        )


def validate_file_encoding(file_path: str, expected_encoding: str = "utf-8") -> bool:
    """
    验证文件编码

    Args:
        file_path: 文件路径
        expected_encoding: 期望的编码（默认 utf-8）

    Returns:
        是否有效

    Raises:
        CommandInstallError: 编码不正确时
    """
    try:
        with open(file_path, "r", encoding=expected_encoding) as f:
            f.read()
        return True

    except UnicodeDecodeError:
        raise CommandInstallError(
            ErrorCode.VALIDATE_FILE_ENCODING,
            f"文件编码不是 {expected_encoding}: {file_path}"
        )
    except Exception as e:
        raise CommandInstallError(
            ErrorCode.VALIDATE_FILE_ENCODING,
            f"读取文件失败: {str(e)}"
        )


def validate_json_file(file_path: str) -> bool:
    """
    验证 JSON 文件格式

    Args:
        file_path: JSON 文件路径

    Returns:
        是否有效

    Raises:
        CommandInstallError: JSON 格式无效时
    """
    import json

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            json.load(f)
        return True

    except json.JSONDecodeError as e:
        raise CommandInstallError(
            ErrorCode.CONFIG_INVALID_FORMAT,
            f"JSON 格式无效: {file_path}\n   {str(e)}"
        )
    except Exception as e:
        raise CommandInstallError(
            ErrorCode.CONFIG_INVALID_FORMAT,
            f"读取 JSON 文件失败: {str(e)}"
        )


def compare_checksums(file1: str, file2: str, algorithm: str = "sha256") -> bool:
    """
    比较两个文件的校验和

    Args:
        file1: 第一个文件路径
        file2: 第二个文件路径
        algorithm: 哈希算法（默认 sha256）

    Returns:
        是否相同

    Raises:
        CommandInstallError: 文件读取失败时
    """
    checksum1 = calculate_checksum(file1, algorithm)
    checksum2 = calculate_checksum(file2, algorithm)

    return checksum1 == checksum2


def validate_claude_directory(directory: str) -> bool:
    """
    验证 .claude/ 目录的有效性

    Args:
        directory: .claude/ 目录路径

    Returns:
        是否有效

    Raises:
        CommandInstallError: 目录无效时
    """
    import os
    from pathlib import Path

    claude_dir = Path(directory)

    if not claude_dir.exists():
        raise CommandInstallError(
            ErrorCode.SYSTEM_UNKNOWN_ERROR,
            f".claude/ 目录不存在: {directory}"
        )

    if not claude_dir.is_dir():
        raise CommandInstallError(
            ErrorCode.SYSTEM_UNKNOWN_ERROR,
            f".claude/ 路径不是目录: {directory}"
        )

    # 检查是否包含预期的子目录或文件
    expected_items = ["commands", "templates"]
    found_items = []

    for item in expected_items:
        if (claude_dir / item).exists():
            found_items.append(item)

    if not found_items:
        raise CommandInstallError(
            ErrorCode.SYSTEM_UNKNOWN_ERROR,
            f".claude/ 目录似乎无效（缺少 commands/ 或 templates/ 子目录）: {directory}"
        )

    return True
