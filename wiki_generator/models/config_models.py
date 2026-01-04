"""配置相关的数据模型。

此模块包含 Wiki 配置文件相关的所有数据类定义。
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class Language(str, Enum):
    """文档语言枚举"""

    ZH = "zh"
    EN = "en"
    BOTH = "both"


class StructureTemplate(str, Enum):
    """文档结构模板枚举"""

    REFERENCE = "reference"
    SIMPLE = "simple"
    CUSTOM = "custom"


@dataclass
class SectionConfig:
    """文档章节配置"""

    required: List[str] = field(default_factory=list)
    optional: List[str] = field(default_factory=list)


@dataclass
class WikiConfig:
    """Wiki 配置文件

    对应 .claude/wiki-config.json 的数据结构。
    """

    output_dir: str = "docs"
    language: Language = Language.ZH
    structure_template: StructureTemplate = StructureTemplate.REFERENCE
    include_sources: bool = True
    generate_toc: bool = True
    sections: Optional[SectionConfig] = None
    version: Optional[str] = None


@dataclass
class TemplateInfo:
    """单个模板文件的信息"""

    name: str
    language: str
    path: str
    title: str
    version: str
    variables: List[str] = field(default_factory=list)


@dataclass
class TemplateManifest:
    """所有已安装模板的清单"""

    version: str
    installed_date: str
    templates: List[TemplateInfo] = field(default_factory=list)

    @property
    def total_count(self) -> int:
        """模板总数"""
        return len(self.templates)


@dataclass
class ValidationResult:
    """配置文件验证的结果"""

    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    config_path: Optional[str] = None


@dataclass
class MigrationResult:
    """配置文件迁移的结果"""

    success: bool
    backup_path: Optional[str] = None
    changes: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    from_version: Optional[str] = None
    to_version: Optional[str] = None


@dataclass
class InstallResult:
    """.claude/ 文件安装的结果"""

    success: bool
    installed_files: List[str] = field(default_factory=list)
    skipped_files: List[str] = field(default_factory=list)
    error: Optional[str] = None
    target_dir: Optional[str] = None
    backup_dir: Optional[str] = None
