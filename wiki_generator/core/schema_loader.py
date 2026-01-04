"""JSON Schema 加载器。

此模块负责加载和管理 JSON Schema 文件，用于配置验证。
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any

from wiki_generator.utils.file_utils import read_file_content


class SchemaLoader:
    """JSON Schema 加载器。

    负责从文件系统加载 JSON Schema，并提供缓存机制。
    """

    def __init__(self, schema_dir: Optional[Path] = None):
        """初始化 Schema 加载器。

        Args:
            schema_dir: Schema 文件目录。如果为 None，使用默认目录。
        """
        if schema_dir is None:
            # 默认使用包内的 schema 目录
            current_file = Path(__file__)
            schema_dir = current_file.parent.parent / ".claude" / "schema"

        self.schema_dir = Path(schema_dir)
        self._cache: Dict[str, Dict[str, Any]] = {}

    def load_schema(self, schema_name: str) -> Optional[Dict[str, Any]]:
        """加载 JSON Schema。

        Args:
            schema_name: Schema 文件名（如 "wiki-config-schema-v2.json"）

        Returns:
            Schema 字典，如果加载失败则返回 None
        """
        # 检查缓存
        if schema_name in self._cache:
            return self._cache[schema_name]

        # 构建 Schema 文件路径
        schema_path = self.schema_dir / schema_name

        if not schema_path.exists():
            return None

        # 读取文件内容
        content = read_file_content(schema_path)
        if content is None:
            return None

        try:
            schema = json.loads(content)
            # 缓存 Schema
            self._cache[schema_name] = schema
            return schema
        except json.JSONDecodeError:
            return None

    def clear_cache(self) -> None:
        """清除缓存。"""
        self._cache.clear()

    def get_available_schemas(self) -> list[str]:
        """获取所有可用的 Schema 文件列表。

        Returns:
            Schema 文件名列表
        """
        if not self.schema_dir.exists():
            return []

        schemas = []
        for schema_file in self.schema_dir.glob("*.json"):
            schemas.append(schema_file.name)

        return sorted(schemas)


# 默认 Schema 加载器实例（单例模式）
_default_loader: Optional[SchemaLoader] = None


def get_default_loader() -> SchemaLoader:
    """获取默认 Schema 加载器实例。

    Returns:
        SchemaLoader 实例
    """
    global _default_loader
    if _default_loader is None:
        _default_loader = SchemaLoader()
    return _default_loader
