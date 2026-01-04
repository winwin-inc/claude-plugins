"""配置迁移规则。

此模块定义了配置文件从旧版本迁移到新版本的规则。
"""

from typing import Dict, Any, Callable, List


# 迁移规则类型
MigrationRule = Callable[[Dict[str, Any]], Dict[str, Any]]


def migrate_1_to_2(config: Dict[str, Any]) -> Dict[str, Any]:
    """从 v1.0 迁移到 v2.0。

    Args:
        config: v1.0 配置

    Returns:
        v2.0 配置
    """
    changes = []

    # 重命名字段: lang -> language
    if "lang" in config:
        config["language"] = config.pop("lang")
        changes.append("重命名字段: lang -> language")

    # 添加默认字段（如果不存在）
    if "output_dir" not in config:
        config["output_dir"] = "docs"
        changes.append("添加字段: output_dir = docs")

    if "structure_template" not in config:
        config["structure_template"] = "reference"
        changes.append("添加字段: structure_template = reference")

    if "include_sources" not in config:
        config["include_sources"] = True
        changes.append("添加字段: include_sources = true")

    if "generate_toc" not in config:
        config["generate_toc"] = True
        changes.append("添加字段: generate_toc = true")

    # 更新版本号
    config["version"] = "2.0.0"
    changes.append("更新版本: 1.0 -> 2.0")

    # 添加 _changes 元数据（用于生成报告）
    config["_migration_changes"] = changes

    return config


# 迁移规则映射表
# 格式: { "from_version": (to_version, migration_function) }
MIGRATION_RULES: Dict[str, tuple[str, MigrationRule]] = {
    "1.0": ("2.0", migrate_1_to_2),
}


def get_migration_rules() -> Dict[str, tuple[str, MigrationRule]]:
    """获取所有迁移规则。

    Returns:
        迁移规则字典
    """
    return MIGRATION_RULES.copy()


def get_available_versions() -> List[str]:
    """获取所有支持的源版本。

    Returns:
        版本号列表
    """
    return list(MIGRATION_RULES.keys())


def get_target_version(source_version: str) -> str:
    """获取迁移目标版本。

    Args:
        source_version: 源版本号

    Returns:
        目标版本号，如果未找到规则则返回 None
    """
    rule = MIGRATION_RULES.get(source_version)
    return rule[0] if rule else None
