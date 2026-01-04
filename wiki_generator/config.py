"""
Wiki Generator 配置文件生成和验证

负责生成和验证 wiki-config.json 配置文件。
"""

import json
import shutil
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
from wiki_generator import InstallerError, ValidationError


# 默认配置
DEFAULT_CONFIG = {
    "output_dir": "docs",
    "exclude_patterns": ["node_modules", "dist", ".git"],
    "quality_threshold": 80,
    "diagrams_enabled": True,
    "diagrams_detail_level": "medium",
}


@dataclass
class WikiConfig:
    """Wiki 配置数据类

    包含所有配置字段，用于类型检查和验证。
    """

    output_dir: str  # 文档输出目录
    exclude_patterns: list[str]  # 排除的文件/目录模式
    quality_threshold: int  # 文档质量分数阈值（0-100）
    diagrams_enabled: bool  # 是否生成 Mermaid 图表
    diagrams_detail_level: str  # 图表细节级别（low|medium|high）


def validate_config(config_path: str) -> tuple[bool, list[ValidationError]]:
    """验证 wiki-config.json 配置文件

    Args:
        config_path: 配置文件路径

    Returns:
        tuple[bool, list[ValidationError]]: (是否有效, 错误列表)

    Side Effects:
        - 读取并解析 JSON 文件
        - 无副作用（只读操作）
    """
    errors: list[ValidationError] = []

    try:
        config_file = Path(config_path)
        if not config_file.exists():
            errors.append(
                ValidationError(
                    field="config_file",
                    message="配置文件不存在",
                    expected=f"存在文件: {config_path}",
                    actual="文件未找到",
                )
            )
            return False, errors

        # 读取 JSON 文件
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)

        # 验证必需字段
        required_fields = {
            "output_dir": str,
            "exclude_patterns": list,
            "quality_threshold": int,
            "diagrams_enabled": bool,
            "diagrams_detail_level": str,
        }

        for field, field_type in required_fields.items():
            if field not in config:
                errors.append(
                    ValidationError(
                        field=field,
                        message=f"缺少必需字段 '{field}'",
                        expected=field_type.__name__,
                        actual=None,
                    )
                )
                continue

            if not isinstance(config[field], field_type):
                errors.append(
                    ValidationError(
                        field=field,
                        message=f"字段类型错误",
                        expected=field_type.__name__,
                        actual=type(config[field]).__name__,
                    )
                )

        # 验证枚举值
        if "diagrams_detail_level" in config:
            valid_levels = ["low", "medium", "high"]
            if config["diagrams_detail_level"] not in valid_levels:
                errors.append(
                    ValidationError(
                        field="diagrams_detail_level",
                        message="diagrams_detail_level 必须是 'low', 'medium', 或 'high'",
                        expected="|".join(valid_levels),
                        actual=config["diagrams_detail_level"],
                    )
                )

        # 验证数值范围
        if "quality_threshold" in config:
            threshold = config["quality_threshold"]
            if not isinstance(threshold, int) or not (0 <= threshold <= 100):
                errors.append(
                    ValidationError(
                        field="quality_threshold",
                        message="quality_threshold 必须在 0 到 100 之间",
                        expected="0-100",
                        actual=str(threshold),
                    )
                )

        # 验证数组不为空
        if "exclude_patterns" in config:
            patterns = config["exclude_patterns"]
            if isinstance(patterns, list) and len(patterns) == 0:
                errors.append(
                    ValidationError(
                        field="exclude_patterns",
                        message="exclude_patterns 不能为空数组",
                        expected="至少 1 个元素",
                        actual="空数组",
                    )
                )

        return len(errors) == 0, errors

    except json.JSONDecodeError as e:
        errors.append(
            ValidationError(
                field="JSON",
                message=f"JSON 格式无效: {e.msg}",
                expected="有效 JSON",
                actual=str(e.lineno) if e.lineno else "未知位置",
            )
        )
        return False, errors
    except Exception as e:
        errors.append(
            ValidationError(
                field="config_file",
                message=f"读取配置文件失败: {e}",
                expected="可读文件",
                actual=str(type(e).__name__),
            )
        )
        return False, errors


def generate_config(
    target_dir: str = ".", overwrite: bool = False
) -> dict[str, Any]:
    """生成 wiki-config.json 配置文件

    Args:
        target_dir: 目标目录路径（默认: 当前目录）
        overwrite: 是否覆盖已存在的配置（默认: False）

    Returns:
        dict[str, Any]: 生成的配置对象

    Raises:
        InstallerError: 配置文件已存在且 overwrite=False
        ValidationError: 现有配置文件格式无效

    Side Effects:
        - 创建 wiki-config.json 文件
        - 备份已存在的配置（如果 overwrite=True）
    """
    target_path = Path(target_dir).resolve()
    config_file = target_path / "wiki-config.json"

    # 检查配置文件是否已存在
    if config_file.exists():
        if not overwrite:
            # 验证现有配置
            is_valid, errors = validate_config(str(config_file))
            if is_valid:
                # 配置有效，读取并返回
                with open(config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                # 配置无效，备份并重新生成
                backup_file = Path(str(config_file) + ".backup")
                shutil.copy2(config_file, backup_file)
                print(f"⚠️  现有配置无效，已备份为: {backup_file.name}")

        # overwrite=True 或配置无效，继续生成新配置
        if overwrite:
            backup_file = Path(str(config_file) + ".backup")
            shutil.copy2(config_file, backup_file)
            print(f"💾 已备份现有配置: {backup_file.name}")

    # 生成新配置
    config = DEFAULT_CONFIG.copy()

    # 写入配置文件（标准 JSON 格式，无注释）
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return config
