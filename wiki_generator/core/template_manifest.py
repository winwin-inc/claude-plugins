"""模板清单管理器。

此模块负责管理已安装模板的清单信息。
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from wiki_generator.models.config_models import TemplateInfo, TemplateManifest
from wiki_generator.utils.file_utils import read_file_content, write_file_content


class TemplateManifestManager:
    """模板清单管理器。

    负责创建、读取、更新模板清单文件。
    """

    MANIFEST_FILENAME = "template-manifest.json"

    def __init__(self, claude_dir: Optional[Path] = None):
        """初始化模板清单管理器。

        Args:
            claude_dir: .claude 目录路径。如果为 None，使用当前目录的 .claude/
        """
        if claude_dir is None:
            claude_dir = Path.cwd() / ".claude"

        self.claude_dir = Path(claude_dir)
        self.manifest_path = self.claude_dir / self.MANIFEST_FILENAME

    def create_manifest(
        self,
        version: str,
        templates: List[TemplateInfo]
    ) -> TemplateManifest:
        """创建新的模板清单。

        Args:
            version: 模板版本号
            templates: 模板信息列表

        Returns:
            模板清单对象
        """
        manifest = TemplateManifest(
            version=version,
            installed_date=datetime.utcnow().isoformat() + "Z",
            templates=templates
        )

        return manifest

    def load_manifest(self) -> Optional[TemplateManifest]:
        """加载模板清单。

        Returns:
            模板清单对象，如果文件不存在则返回 None
        """
        if not self.manifest_path.exists():
            return None

        content = read_file_content(self.manifest_path)
        if content is None:
            return None

        try:
            data = json.loads(content)
            return self._deserialize_manifest(data)
        except (json.JSONDecodeError, KeyError):
            return None

    def save_manifest(self, manifest: TemplateManifest) -> bool:
        """保存模板清单。

        Args:
            manifest: 模板清单对象

        Returns:
            是否成功保存
        """
        data = self._serialize_manifest(manifest)
        json_content = json.dumps(data, indent=2, ensure_ascii=False)

        return write_file_content(self.manifest_path, json_content)

    def get_template_info(self, template_name: str) -> Optional[TemplateInfo]:
        """获取指定模板的信息。

        Args:
            template_name: 模板名称

        Returns:
            模板信息，如果未找到则返回 None
        """
        manifest = self.load_manifest()
        if manifest is None:
            return None

        for template in manifest.templates:
            if template.name == template_name:
                return template

        return None

    def get_installed_templates(self) -> List[TemplateInfo]:
        """获取所有已安装的模板列表。

        Returns:
            模板信息列表
        """
        manifest = self.load_manifest()
        if manifest is None:
            return []

        return manifest.templates

    def get_version(self) -> Optional[str]:
        """获取已安装模板的版本号。

        Returns:
            版本号，如果未找到则返回 None
        """
        manifest = self.load_manifest()
        if manifest is None:
            return None

        return manifest.version

    def is_version_match(self, expected_version: str) -> bool:
        """检查已安装模板版本是否匹配。

        Args:
            expected_version: 期望的版本号

        Returns:
            是否版本匹配
        """
        installed_version = self.get_version()
        return installed_version == expected_version

    def update_installation_date(self) -> bool:
        """更新安装日期为当前时间。

        Returns:
            是否成功更新
        """
        manifest = self.load_manifest()
        if manifest is None:
            return False

        manifest.installed_date = datetime.utcnow().isoformat() + "Z"
        return self.save_manifest(manifest)

    def _serialize_manifest(self, manifest: TemplateManifest) -> dict:
        """序列化模板清单为字典。

        Args:
            manifest: 模板清单对象

        Returns:
            序列化后的字典
        """
        return {
            "version": manifest.version,
            "installed_date": manifest.installed_date,
            "templates": [
                {
                    "name": t.name,
                    "language": t.language,
                    "path": t.path,
                    "title": t.title,
                    "version": t.version,
                    "variables": t.variables
                }
                for t in manifest.templates
            ]
        }

    def _deserialize_manifest(self, data: dict) -> TemplateManifest:
        """从字典反序列化模板清单。

        Args:
            data: 序列化的字典

        Returns:
            模板清单对象
        """
        templates = [
            TemplateInfo(
                name=t["name"],
                language=t["language"],
                path=t["path"],
                title=t["title"],
                version=t["version"],
                variables=t.get("variables", [])
            )
            for t in data.get("templates", [])
        ]

        return TemplateManifest(
            version=data["version"],
            installed_date=data["installed_date"],
            templates=templates
        )
