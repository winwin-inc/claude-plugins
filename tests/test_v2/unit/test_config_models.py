"""测试配置数据模型。

验证 WikiConfig、SectionConfig、TemplateInfo 等数据类的正确性。
"""

import pytest
from wiki_generator.models.config_models import (
    Language,
    StructureTemplate,
    SectionConfig,
    WikiConfig,
    TemplateInfo,
    TemplateManifest,
    ValidationResult,
    MigrationResult,
    InstallResult,
)


class TestLanguage:
    """测试 Language 枚举。"""

    def test_values(self):
        """测试枚举值。"""
        assert Language.ZH == "zh"
        assert Language.EN == "en"
        assert Language.BOTH == "both"


class TestStructureTemplate:
    """测试 StructureTemplate 枚举。"""

    def test_values(self):
        """测试枚举值。"""
        assert StructureTemplate.REFERENCE == "reference"
        assert StructureTemplate.SIMPLE == "simple"
        assert StructureTemplate.CUSTOM == "custom"


class TestSectionConfig:
    """测试 SectionConfig 数据类。"""

    def test_default_values(self):
        """测试默认值。"""
        config = SectionConfig()
        assert config.required == []
        assert config.optional == []

    def test_with_values(self):
        """测试带值的配置。"""
        config = SectionConfig(
            required=["quickstart", "overview"],
            optional=["datamodel"]
        )
        assert len(config.required) == 2
        assert len(config.optional) == 1


class TestWikiConfig:
    """测试 WikiConfig 数据类。"""

    def test_default_values(self):
        """测试默认值。"""
        config = WikiConfig()
        assert config.output_dir == "docs"
        assert config.language == Language.ZH
        assert config.structure_template == StructureTemplate.REFERENCE
        assert config.include_sources is True
        assert config.generate_toc is True
        assert config.sections is None
        assert config.version is None

    def test_with_values(self):
        """测试带值的配置。"""
        sections = SectionConfig(required=["quickstart"])
        config = WikiConfig(
            output_dir="documentation",
            language=Language.EN,
            structure_template=StructureTemplate.CUSTOM,
            sections=sections,
            version="2.0.0"
        )
        assert config.output_dir == "documentation"
        assert config.language == Language.EN
        assert config.structure_template == StructureTemplate.CUSTOM
        assert config.sections == sections
        assert config.version == "2.0.0"


class TestTemplateInfo:
    """测试 TemplateInfo 数据类。"""

    def test_creation(self):
        """测试创建。"""
        info = TemplateInfo(
            name="quickstart",
            language="zh",
            path="templates/zh/quickstart.md.template",
            title="快速开始",
            version="2.0.0"
        )
        assert info.name == "quickstart"
        assert info.language == "zh"
        assert info.path == "templates/zh/quickstart.md.template"
        assert info.title == "快速开始"
        assert info.version == "2.0.0"
        assert info.variables == []

    def test_with_variables(self):
        """测试带变量列表。"""
        info = TemplateInfo(
            name="overview",
            language="en",
            path="templates/en/overview.md.template",
            title="Overview",
            version="2.0.0",
            variables=["title", "content", "sources"]
        )
        assert len(info.variables) == 3


class TestTemplateManifest:
    """测试 TemplateManifest 数据类。"""

    def test_creation(self):
        """测试创建。"""
        manifest = TemplateManifest(
            version="2.0.0",
            installed_date="2025-01-04T00:00:00Z"
        )
        assert manifest.version == "2.0.0"
        assert manifest.installed_date == "2025-01-04T00:00:00Z"
        assert manifest.templates == []
        assert manifest.total_count == 0

    def test_with_templates(self):
        """测试带模板列表。"""
        templates = [
            TemplateInfo(
                name="quickstart",
                language="zh",
                path="templates/zh/quickstart.md.template",
                title="快速开始",
                version="2.0.0"
            ),
            TemplateInfo(
                name="overview",
                language="zh",
                path="templates/zh/overview.md.template",
                title="项目概述",
                version="2.0.0"
            ),
        ]
        manifest = TemplateManifest(
            version="2.0.0",
            installed_date="2025-01-04T00:00:00Z",
            templates=templates
        )
        assert manifest.total_count == 2


class TestValidationResult:
    """测试 ValidationResult 数据类。"""

    def test_success(self):
        """测试成功结果。"""
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []
        assert result.config_path is None

    def test_failure(self):
        """测试失败结果。"""
        result = ValidationResult(
            is_valid=False,
            errors=["字段 'language': 必需"],
            config_path=".claude/wiki-config.json"
        )
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.config_path == ".claude/wiki-config.json"


class TestMigrationResult:
    """测试 MigrationResult 数据类。"""

    def test_success(self):
        """测试成功结果。"""
        result = MigrationResult(
            success=True,
            backup_path=".claude/wiki-config.json.backup",
            changes=["添加字段: language = zh"],
            from_version="1.0",
            to_version="2.0"
        )
        assert result.success is True
        assert result.backup_path.endswith(".backup")
        assert len(result.changes) == 1
        assert result.from_version == "1.0"
        assert result.to_version == "2.0"

    def test_failure(self):
        """测试失败结果。"""
        result = MigrationResult(
            success=False,
            errors=["无法读取配置文件"]
        )
        assert result.success is False
        assert len(result.errors) == 1


class TestInstallResult:
    """测试 InstallResult 数据类。"""

    def test_success(self):
        """测试成功结果。"""
        result = InstallResult(
            success=True,
            installed_files=[".claude/wiki-config.json"],
            target_dir=".claude"
        )
        assert result.success is True
        assert len(result.installed_files) == 1
        assert result.target_dir == ".claude"

    def test_failure(self):
        """测试失败结果。"""
        result = InstallResult(
            success=False,
            error="权限不足"
        )
        assert result.success is False
        assert result.error == "权限不足"
