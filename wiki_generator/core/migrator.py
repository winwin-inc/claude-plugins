"""配置迁移器。

此模块负责执行配置文件从旧版本到新版本的迁移。
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any

from wiki_generator.models.config_models import MigrationResult
from wiki_generator.core.migrations import get_migration_rules, get_target_version
from wiki_generator.utils.file_utils import backup_file, write_file_content, read_file_content


def detect_version(config_path: Path) -> Optional[str]:
    """检测配置文件版本。

    Args:
        config_path: 配置文件路径

    Returns:
        版本号，如果未找到则返回 None
    """
    content = read_file_content(config_path)
    if content is None:
        return None

    try:
        config = json.loads(content)
        return config.get("version")
    except (json.JSONDecodeError, TypeError):
        return None


def backup_config(config_path: Path) -> Optional[Path]:
    """备份配置文件。

    Args:
        config_path: 配置文件路径

    Returns:
        备份文件路径，如果失败则返回 None
    """
    return backup_file(config_path)


def apply_migration(
    config_path: Path,
    target_version: Optional[str] = None,
    backup: bool = True
) -> MigrationResult:
    """应用配置迁移。

    Args:
        config_path: 配置文件路径
        target_version: 目标版本（如果为 None，迁移到最新版本）
        backup: 是否备份原文件

    Returns:
        迁移结果
    """
    # 检测当前版本
    current_version = detect_version(config_path)
    if current_version is None:
        return MigrationResult(
            success=False,
            errors=["无法检测配置文件版本"]
        )

    # 获取迁移规则
    migration_rules = get_migration_rules()

    # 查找适用的迁移规则
    if current_version not in migration_rules:
        return MigrationResult(
            success=False,
            errors=[f"没有从版本 {current_version} 的迁移规则"],
            from_version=current_version,
            to_version=target_version
        )

    # 确定目标版本
    if target_version is None:
        target_version = migration_rules[current_version][0]

    # 备份原文件
    backup_path = None
    if backup:
        backup_path = backup_config(config_path)
        if backup_path is None:
            return MigrationResult(
                success=False,
                errors=["备份文件失败"],
                from_version=current_version
            )

    # 读取配置
    content = read_file_content(config_path)
    if content is None:
        return MigrationResult(
            success=False,
            errors=["无法读取配置文件"],
            from_version=current_version
        )

    try:
        config = json.loads(content)
    except json.JSONDecodeError as e:
        return MigrationResult(
            success=False,
            errors=[f"JSON 解析失败: {str(e)}"],
            from_version=current_version
        )

    # 应用迁移规则
    migration_func = migration_rules[current_version][1]
    try:
        migrated_config = migration_func(config)
    except Exception as e:
        return MigrationResult(
            success=False,
            errors=[f"迁移失败: {str(e)}"],
            from_version=current_version
        )

    # 提取变更列表
    changes = migrated_config.pop("_migration_changes", [])

    # 写入迁移后的配置
    json_content = json.dumps(migrated_config, indent=2, ensure_ascii=False)
    if not write_file_content(config_path, json_content):
        return MigrationResult(
            success=False,
            errors=["写入配置文件失败"],
            from_version=current_version,
            to_version=target_version
        )

    return MigrationResult(
        success=True,
        backup_path=str(backup_path) if backup_path else None,
        changes=changes,
        from_version=current_version,
        to_version=target_version
    )


def generate_migration_report(result: MigrationResult) -> str:
    """生成迁移报告。

    Args:
        result: 迁移结果

    Returns:
        Markdown 格式的迁移报告
    """
    if not result.success:
        return f"""# 迁移失败

**错误**:
{chr(10).join(f"- {err}" for err in result.errors)}
"""

    report_lines = [
        "# 配置迁移报告",
        "",
        f"✅ 成功迁移到版本 {result.to_version}",
        "",
        "## 变更内容",
        ""
    ]

    for change in result.changes:
        report_lines.append(f"- {change}")

    if result.backup_path:
        report_lines.extend([
            "",
            f"**备份文件**: `{result.backup_path}`"
        ])

    report_lines.extend([
        "",
        "---",
        "",
        "**建议**:",
        "- 请检查迁移后的配置是否符合预期",
        "- 如果一切正常，可以删除备份文件",
        "- 如果有问题，可以从备份恢复"
    ])

    return "\n".join(report_lines)
