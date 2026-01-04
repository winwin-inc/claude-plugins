"""文件安装器单元测试。

测试 installer_v2 模块的所有功能。
"""

import json
import pytest
from pathlib import Path
from wiki_generator.core.installer_v2 import (
    install_claude_files,
    confirm_overwrite,
    _get_template_version,
    _scan_templates,
    _extract_template_title,
    _extract_template_variables
)
from wiki_generator.models.config_models import InstallResult


class TestConfirmOverwrite:
    """覆盖确认测试类"""

    def test_confirm_overwrite_directory_not_exists(self, tmp_path, monkeypatch):
        """测试目录不存在时自动确认"""
        claude_target = tmp_path / ".claude"

        # 模拟用户不输入（不应该调用 confirm）
        result = confirm_overwrite(claude_target, force=False)

        assert result is True

    def test_confirm_overwrite_with_force(self, tmp_path):
        """测试强制覆盖模式"""
        claude_target = tmp_path / ".claude"
        claude_target.mkdir()

        result = confirm_overwrite(claude_target, force=True)

        assert result is True

    def test_confirm_overwrite_with_confirmation(self, tmp_path, monkeypatch):
        """测试需要用户确认（模拟用户确认）"""
        claude_target = tmp_path / ".claude"
        claude_target.mkdir()
        (claude_target / "test.txt").write_text("test")

        # 模拟用户输入 'y'
        monkeypatch.setattr("click.confirm", lambda *args, **kwargs: True)

        result = confirm_overwrite(claude_target, force=False)

        assert result is True

    def test_confirm_overwrite_user_declines(self, tmp_path, monkeypatch):
        """测试用户拒绝覆盖"""
        claude_target = tmp_path / ".claude"
        claude_target.mkdir()
        (claude_target / "test.txt").write_text("test")

        # 模拟用户输入 'n'
        monkeypatch.setattr("click.confirm", lambda *args, **kwargs: False)

        result = confirm_overwrite(claude_target, force=False)

        assert result is False


class TestGetTemplateVersion:
    """模板版本检测测试类"""

    def test_get_version_from_file(self, tmp_path):
        """测试从文件读取版本号"""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        version_file = claude_dir / ".template-version"
        version_file.write_text("2.0.0", encoding="utf-8")

        version = _get_template_version(claude_dir)

        assert version == "2.0.0"

    def test_get_version_file_not_exists(self, tmp_path):
        """测试版本文件不存在"""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        version = _get_template_version(claude_dir)

        assert version is None


class TestExtractTemplateTitle:
    """模板标题提取测试类"""

    def test_extract_title_with_standard_format(self, tmp_path):
        """测试提取标准格式的标题"""
        template_file = tmp_path / "test.md.template"
        template_file.write_text(
            "# 快速开始\n\n这是快速开始文档",
            encoding="utf-8"
        )

        title = _extract_template_title(template_file)

        assert title == "快速开始"

    def test_extract_title_with_alternative_format(self, tmp_path):
        """测试提取替代格式的标题"""
        template_file = tmp_path / "test.md.template"
        template_file.write_text(
            "#项目概述\n\n这是项目概述文档",
            encoding="utf-8"
        )

        title = _extract_template_title(template_file)

        assert title == "项目概述"

    def test_extract_title_no_title_found(self, tmp_path):
        """测试找不到标题时使用文件名"""
        template_file = tmp_path / "quickstart.md.template"
        template_file.write_text(
            "这是没有标题的文档",
            encoding="utf-8"
        )

        title = _extract_template_title(template_file)

        assert title == "quickstart"

    def test_extract_title_empty_file(self, tmp_path):
        """测试空文件"""
        template_file = tmp_path / "empty.md.template"
        template_file.write_text("", encoding="utf-8")

        title = _extract_template_title(template_file)

        # 应该返回文件名
        assert title == "empty"


class TestExtractTemplateVariables:
    """模板变量提取测试类"""

    def test_extract_variables_from_template(self, tmp_path):
        """测试从模板提取变量"""
        template_file = tmp_path / "test.md.template"
        template_file.write_text(
            "# {title}\n\n项目: {project_name}\n版本: {version}",
            encoding="utf-8"
        )

        variables = _extract_template_variables(template_file)

        assert "project_name" in variables
        assert "title" in variables
        assert "version" in variables

    def test_extract_variables_removes_duplicates(self, tmp_path):
        """测试去除重复变量"""
        template_file = tmp_path / "test.md.template"
        template_file.write_text(
            "{name} {name} {name}",
            encoding="utf-8"
        )

        variables = _extract_template_variables(template_file)

        assert len(variables) == 1
        assert "name" in variables

    def test_extract_variables_sorts_output(self, tmp_path):
        """测试变量排序输出"""
        template_file = tmp_path / "test.md.template"
        template_file.write_text(
            "{zebra} {apple} {banana}",
            encoding="utf-8"
        )

        variables = _extract_template_variables(template_file)

        assert variables == ["apple", "banana", "zebra"]

    def test_extract_variables_no_variables(self, tmp_path):
        """测试没有变量的模板"""
        template_file = tmp_path / "test.md.template"
        template_file.write_text(
            "这是没有变量的文档",
            encoding="utf-8"
        )

        variables = _extract_template_variables(template_file)

        assert len(variables) == 0


class TestScanTemplates:
    """模板扫描测试类"""

    def test_scan_templates_zh_directory(self, tmp_path):
        """测试扫描中文模板目录"""
        claude_dir = tmp_path / ".claude"
        templates_dir = claude_dir / "templates" / "zh"
        templates_dir.mkdir(parents=True)

        # 创建版本文件
        version_file = claude_dir / ".template-version"
        version_file.write_text("2.0.0", encoding="utf-8")

        # 创建测试模板文件
        (templates_dir / "quickstart.md.template").write_text(
            "# 快速开始\n\n项目: {project_name}",
            encoding="utf-8"
        )
        (templates_dir / "overview.md.template").write_text(
            "# 项目概述\n\n{overview_summary}",
            encoding="utf-8"
        )

        templates = _scan_templates(claude_dir)

        assert len(templates) == 2
        assert any(t.name == "quickstart" for t in templates)
        assert any(t.name == "overview" for t in templates)
        assert all(t.language == "zh" for t in templates)
        assert all(t.version == "2.0.0" for t in templates)

    def test_scan_templates_en_directory(self, tmp_path):
        """测试扫描英文模板目录"""
        claude_dir = tmp_path / ".claude"
        templates_dir = claude_dir / "templates" / "en"
        templates_dir.mkdir(parents=True)

        version_file = claude_dir / ".template-version"
        version_file.write_text("2.0.0", encoding="utf-8")

        (templates_dir / "quickstart.md.template").write_text(
            "# Quick Start\n\nProject: {project_name}",
            encoding="utf-8"
        )

        templates = _scan_templates(claude_dir)

        assert len(templates) == 1
        assert templates[0].language == "en"
        assert templates[0].name == "quickstart"

    def test_scan_templates_no_templates_directory(self, tmp_path):
        """测试模板目录不存在"""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        templates = _scan_templates(claude_dir)

        assert len(templates) == 0

    def test_scan_templates_filters_non_md_files(self, tmp_path):
        """测试过滤非 .md.template 文件"""
        claude_dir = tmp_path / ".claude"
        templates_dir = claude_dir / "templates" / "zh"
        templates_dir.mkdir(parents=True)

        version_file = claude_dir / ".template-version"
        version_file.write_text("2.0.0", encoding="utf-8")

        # 创建模板文件和其他文件
        (templates_dir / "quickstart.md.template").write_text("# Test", encoding="utf-8")
        (templates_dir / "readme.txt").write_text("Readme", encoding="utf-8")
        (templates_dir / "config.json").write_text("{}", encoding="utf-8")

        templates = _scan_templates(claude_dir)

        assert len(templates) == 1
        assert templates[0].name == "quickstart"


class TestInstallClaudeFiles:
    """文件安装测试类"""

    def test_install_to_new_directory(self, tmp_path):
        """测试安装到新目录"""
        # 创建源目录（模拟包内的 .claude 目录）
        source_dir = tmp_path / "source" / ".claude"
        source_templates = source_dir / "templates" / "zh"
        source_templates.mkdir(parents=True)

        # 创建模板文件
        (source_templates / "quickstart.md.template").write_text("# Test", encoding="utf-8")
        (source_dir / ".template-version").write_text("2.0.0", encoding="utf-8")

        # 创建目标目录
        target_dir = tmp_path / "target"

        result = install_claude_files(
            target_dir=target_dir,
            source_dir=source_dir,
            overwrite=False,
            backup=False
        )

        assert result.success
        assert result.target_dir == str(target_dir / ".claude")
        assert len(result.installed_files) > 0
        assert len(result.skipped_files) == 0

        # 验证文件已安装
        claude_target = target_dir / ".claude"
        assert claude_target.exists()
        assert (claude_target / "templates" / "zh" / "quickstart.md.template").exists()
        assert (claude_target / "wiki-config.json").exists()

    def test_install_creates_config_file(self, tmp_path):
        """测试创建默认配置文件"""
        source_dir = tmp_path / "source" / ".claude"
        source_templates = source_dir / "templates" / "zh"
        source_templates.mkdir(parents=True)
        (source_templates / "test.md.template").write_text("# Test", encoding="utf-8")

        target_dir = tmp_path / "target"

        install_claude_files(
            target_dir=target_dir,
            source_dir=source_dir,
            overwrite=False,
            backup=False
        )

        # 验证配置文件
        config_file = target_dir / ".claude" / "wiki-config.json"
        assert config_file.exists()

        with open(config_file, encoding="utf-8") as f:
            config = json.load(f)

        assert "output_dir" in config
        assert "language" in config
        assert "structure_template" in config

    def test_install_with_backup(self, tmp_path):
        """测试带备份的安装"""
        # 创建已存在的 .claude 目录
        target_dir = tmp_path / "target"
        claude_target = target_dir / ".claude"
        claude_target.mkdir(parents=True)
        (claude_target / "existing.txt").write_text("existing", encoding="utf-8")

        # 创建源目录
        source_dir = tmp_path / "source" / ".claude"
        source_templates = source_dir / "templates" / "zh"
        source_templates.mkdir(parents=True)
        (source_templates / "test.md.template").write_text("# Test", encoding="utf-8")

        result = install_claude_files(
            target_dir=target_dir,
            source_dir=source_dir,
            overwrite=True,
            backup=True
        )

        assert result.success
        assert result.backup_dir is not None

        # 验证备份目录存在
        backup_path = Path(result.backup_dir)
        assert backup_path.exists()
        assert (backup_path / "existing.txt").exists()

    def test_install_source_directory_not_exists(self, tmp_path):
        """测试源目录不存在"""
        target_dir = tmp_path / "target"
        source_dir = tmp_path / "nonexistent"

        result = install_claude_files(
            target_dir=target_dir,
            source_dir=source_dir,
            overwrite=False,
            backup=False
        )

        assert not result.success
        assert "源目录不存在" in result.error


# ==================== 测试辅助函数 ====================

def test_install_result_model():
    """测试 InstallResult 数据模型"""
    result = InstallResult(
        success=True,
        target_dir="/path/to/.claude",
        installed_files=["file1", "file2"],
        skipped_files=[],
        backup_dir="/path/to/backup"
    )

    assert result.success is True
    assert len(result.installed_files) == 2
    assert len(result.skipped_files) == 0
    assert result.backup_dir == "/path/to/backup"


def test_install_result_with_error():
    """测试包含错误的 InstallResult"""
    result = InstallResult(
        success=False,
        error="安装失败: 权限不足",
        target_dir="/path/to/.claude"
    )

    assert result.success is False
    assert "权限不足" in result.error
    assert result.installed_files is None
