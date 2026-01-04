"""配置迁移器单元测试。

测试 migrator 模块的所有功能。
"""

import json
import pytest
from pathlib import Path
from wiki_generator.core.migrator import (
    detect_version,
    apply_migration,
    generate_migration_report
)
from wiki_generator.core.migrations import get_migration_rules, migrate_1_to_2
from wiki_generator.models.config_models import MigrationResult


class TestDetectVersion:
    """版本检测测试类"""

    def test_detect_version_with_version_field(self, tmp_path):
        """测试检测带有 version 字段的配置"""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({"version": "2.0", "language": "zh"}),
            encoding="utf-8"
        )

        version = detect_version(config_file)

        assert version == "2.0"

    def test_detect_version_without_version_field(self, tmp_path):
        """测试检测没有 version 字段的配置"""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps({"language": "zh"}),
            encoding="utf-8"
        )

        version = detect_version(config_file)

        assert version is None

    def test_detect_version_invalid_json(self, tmp_path):
        """测试检测无效 JSON 文件"""
        config_file = tmp_path / "config.json"
        config_file.write_text("{ invalid json }", encoding="utf-8")

        version = detect_version(config_file)

        assert version is None

    def test_detect_version_nonexistent_file(self, tmp_path):
        """测试检测不存在的文件"""
        config_file = tmp_path / "nonexistent.json"

        version = detect_version(config_file)

        assert version is None


class TestMigrationRules:
    """迁移规则测试类"""

    def test_get_migration_rules(self):
        """测试获取迁移规则"""
        rules = get_migration_rules()

        assert isinstance(rules, dict)
        assert "1.0" in rules
        target_version, func = rules["1.0"]
        assert target_version == "2.0"
        assert callable(func)

    def test_migrate_1_to_2_renames_lang_to_language(self):
        """测试 lang → language 字段重命名"""
        old_config = {
            "lang": "zh",
            "output_dir": "docs"
        }

        new_config = migrate_1_to_2(old_config)

        assert "lang" not in new_config
        assert new_config["language"] == "zh"
        assert new_config["output_dir"] == "docs"

    def test_migrate_1_to_2_adds_default_fields(self):
        """测试添加默认字段"""
        old_config = {
            "lang": "en"
        }

        new_config = migrate_1_to_2(old_config)

        # 检查新字段
        assert "output_dir" in new_config
        assert "structure_template" in new_config
        assert "include_sources" in new_config
        assert "generate_toc" in new_config
        assert "version" in new_config

    def test_migrate_1_to_2_preserves_existing_values(self):
        """测试保留现有字段值"""
        old_config = {
            "lang": "zh",
            "output_dir": "wiki",
            "custom_field": "custom_value"
        }

        new_config = migrate_1_to_2(old_config)

        assert new_config["output_dir"] == "wiki"
        assert new_config.get("custom_field") == "custom_value"

    def test_migrate_1_to_2_updates_version(self):
        """测试版本号更新"""
        old_config = {"lang": "zh"}

        new_config = migrate_1_to_2(old_config)

        assert new_config["version"] == "2.0"

    def test_migrate_1_to_2_records_changes(self):
        """测试记录变更列表"""
        old_config = {"lang": "zh"}

        new_config = migrate_1_to_2(old_config)

        assert "_migration_changes" in new_config
        changes = new_config["_migration_changes"]
        assert isinstance(changes, list)
        assert len(changes) > 0


class TestApplyMigration:
    """应用迁移测试类"""

    def test_apply_migration_success(self, tmp_path):
        """测试成功迁移"""
        config_file = tmp_path / "wiki-config.json"
        config_file.write_text(
            json.dumps({"version": "1.0", "lang": "zh"}),
            encoding="utf-8"
        )

        result = apply_migration(config_file, backup=False)

        assert result.success
        assert result.from_version == "1.0"
        assert result.to_version == "2.0"
        assert len(result.changes) > 0

        # 验证迁移后的配置文件
        with open(config_file, encoding="utf-8") as f:
            new_config = json.load(f)

        assert "language" in new_config
        assert "lang" not in new_config
        assert new_config["version"] == "2.0"

    def test_apply_migration_with_backup(self, tmp_path):
        """测试带备份的迁移"""
        config_file = tmp_path / "wiki-config.json"
        config_file.write_text(
            json.dumps({"version": "1.0", "lang": "zh"}),
            encoding="utf-8"
        )

        result = apply_migration(config_file, backup=True)

        assert result.success
        assert result.backup_path is not None

        # 验证备份文件存在
        backup_path = Path(result.backup_path)
        assert backup_path.exists()

    def test_apply_migration_no_version_detected(self, tmp_path):
        """测试无法检测版本"""
        config_file = tmp_path / "wiki-config.json"
        config_file.write_text(
            json.dumps({"language": "zh"}),  # 没有 version 字段
            encoding="utf-8"
        )

        result = apply_migration(config_file, backup=False)

        assert not result.success
        assert len(result.errors) > 0
        assert "无法检测配置文件版本" in result.errors[0]

    def test_apply_migration_no_migration_rule(self, tmp_path):
        """测试没有适用的迁移规则"""
        config_file = tmp_path / "wiki-config.json"
        config_file.write_text(
            json.dumps({"version": "999.0"}),  # 不存在的版本
            encoding="utf-8"
        )

        result = apply_migration(config_file, backup=False)

        assert not result.success
        assert len(result.errors) > 0

    def test_apply_migration_invalid_json(self, tmp_path):
        """测试无效 JSON 配置"""
        config_file = tmp_path / "wiki-config.json"
        config_file.write_text("{ invalid }", encoding="utf-8")

        result = apply_migration(config_file, backup=False)

        assert not result.success
        assert len(result.errors) > 0


class TestGenerateMigrationReport:
    """迁移报告生成测试类"""

    def test_generate_success_report(self):
        """测试生成成功迁移报告"""
        result = MigrationResult(
            success=True,
            from_version="1.0",
            to_version="2.0",
            changes=[
                "字段 'lang' 重命名为 'language'",
                "添加字段 'output_dir'，默认值 'docs'",
                "添加字段 'structure_template'，默认值 'reference'"
            ],
            backup_path="/path/to/backup"
        )

        report = generate_migration_report(result)

        assert "配置迁移报告" in report
        assert "✅ 成功迁移到版本 2.0" in report
        assert "字段 'lang' 重命名为 'language'" in report
        assert "/path/to/backup" in report
        assert "建议" in report

    def test_generate_failure_report(self):
        """测试生成失败迁移报告"""
        result = MigrationResult(
            success=False,
            errors=["无法检测配置文件版本", "配置文件格式错误"]
        )

        report = generate_migration_report(result)

        assert "迁移失败" in report
        assert "无法检测配置文件版本" in report
        assert "配置文件格式错误" in report


# ==================== 测试辅助函数 ====================

def test_migration_result_model():
    """测试 MigrationResult 数据模型"""
    result = MigrationResult(
        success=True,
        from_version="1.0",
        to_version="2.0",
        changes=["变更1", "变更2"],
        backup_path="/path/to/backup"
    )

    assert result.success is True
    assert result.from_version == "1.0"
    assert result.to_version == "2.0"
    assert len(result.changes) == 2
    assert result.backup_path == "/path/to/backup"
    assert len(result.errors) == 0


def test_migration_result_with_errors():
    """测试包含错误的 MigrationResult"""
    result = MigrationResult(
        success=False,
        errors=["错误1", "错误2"],
        from_version="1.0"
    )

    assert result.success is False
    assert len(result.errors) == 2
    assert result.to_version is None
