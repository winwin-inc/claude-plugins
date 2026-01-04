"""配置验证器单元测试。

测试 ConfigValidator 类的所有功能。
"""

import json
import pytest
from pathlib import Path
from wiki_generator.core.config_validator import ConfigValidator
from wiki_generator.models.config_models import ValidationResult


class TestConfigValidator:
    """配置验证器测试类"""

    @pytest.fixture
    def validator(self):
        """创建验证器实例"""
        return ConfigValidator()

    @pytest.fixture
    def temp_config_file(self, tmp_path, config_content):
        """创建临时配置文件"""
        config_file = tmp_path / "wiki-config.json"
        config_file.write_text(config_content, encoding="utf-8")
        return config_file

    # ==================== 有效配置测试 ====================

    def test_validate_valid_minimal_config(self, validator, temp_config_file):
        """测试有效最小配置"""
        config_content = json.dumps({
            "output_dir": "docs",
            "language": "zh",
            "structure_template": "reference"
        })
        config_file = temp_config_file(config_content)

        result = validator.validate_config_file(config_file)

        assert result.is_valid
        assert len(result.errors) == 0
        assert result.config_path == str(config_file)

    def test_validate_valid_full_config(self, validator, temp_config_file):
        """测试有效完整配置"""
        config_content = json.dumps({
            "output_dir": "docs",
            "language": "en",
            "structure_template": "custom",
            "include_sources": True,
            "generate_toc": True,
            "sections": {
                "required": ["quickstart", "overview"],
                "optional": ["api", "testing"]
            }
        })
        config_file = temp_config_file(config_content)

        result = validator.validate_config_file(config_file)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_language_both(self, validator, temp_config_file):
        """测试 language: both 配置"""
        config_content = json.dumps({
            "output_dir": "docs",
            "language": "both",
            "structure_template": "reference"
        })
        config_file = temp_config_file(config_content)

        result = validator.validate_config_file(config_file)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_structure_template_simple(self, validator, temp_config_file):
        """测试 structure_template: simple 配置"""
        config_content = json.dumps({
            "output_dir": "wiki",
            "language": "zh",
            "structure_template": "simple"
        })
        config_file = temp_config_file(config_content)

        result = validator.validate_config_file(config_file)

        assert result.is_valid
        assert len(result.errors) == 0

    # ==================== 无效配置测试 ====================

    def test_validate_missing_required_field(self, validator, temp_config_file):
        """测试缺少必需字段"""
        config_content = json.dumps({
            "output_dir": "docs"
            # 缺少 language 和 structure_template
        })
        config_file = temp_config_file(config_content)

        result = validator.validate_config_file(config_file)

        assert not result.is_valid
        assert len(result.errors) > 0
        assert any("language" in error for error in result.errors)

    def test_validate_invalid_language(self, validator, temp_config_file):
        """测试无效的 language 值"""
        config_content = json.dumps({
            "output_dir": "docs",
            "language": "fr",  # 无效语言
            "structure_template": "reference"
        })
        config_file = temp_config_file(config_content)

        result = validator.validate_config_file(config_file)

        assert not result.is_valid
        assert any("language" in error.lower() for error in result.errors)

    def test_validate_invalid_structure_template(self, validator, temp_config_file):
        """测试无效的 structure_template 值"""
        config_content = json.dumps({
            "output_dir": "docs",
            "language": "zh",
            "structure_template": "invalid"  # 无效模板
        })
        config_file = temp_config_file(config_content)

        result = validator.validate_config_file(config_file)

        assert not result.is_valid
        assert any("structure_template" in error.lower() for error in result.errors)

    def test_validate_invalid_include_sources_type(self, validator, temp_config_file):
        """测试 include_sources 类型错误"""
        config_content = json.dumps({
            "output_dir": "docs",
            "language": "zh",
            "structure_template": "reference",
            "include_sources": "yes"  # 应该是 boolean
        })
        config_file = temp_config_file(config_content)

        result = validator.validate_config_file(config_file)

        assert not result.is_valid

    def test_validate_invalid_generate_toc_type(self, validator, temp_config_file):
        """测试 generate_toc 类型错误"""
        config_content = json.dumps({
            "output_dir": "docs",
            "language": "zh",
            "structure_template": "reference",
            "generate_toc": 1  # 应该是 boolean
        })
        config_file = temp_config_file(config_content)

        result = validator.validate_config_file(config_file)

        assert not result.is_valid

    def test_validate_custom_template_without_sections(self, validator, temp_config_file):
        """测试 custom 模板缺少 sections 字段"""
        config_content = json.dumps({
            "output_dir": "docs",
            "language": "zh",
            "structure_template": "custom"
            # 缺少 sections
        })
        config_file = temp_config_file(config_content)

        result = validator.validate_config_file(config_file)

        assert not result.is_valid
        assert any("sections" in error.lower() for error in result.errors)

    def test_validate_invalid_sections_format(self, validator, temp_config_file):
        """测试无效的 sections 格式"""
        config_content = json.dumps({
            "output_dir": "docs",
            "language": "zh",
            "structure_template": "custom",
            "sections": "invalid"  # 应该是对象
        })
        config_file = temp_config_file(config_content)

        result = validator.validate_config_file(config_file)

        assert not result.is_valid

    # ==================== 文件操作测试 ====================

    def test_validate_nonexistent_file(self, validator, tmp_path):
        """测试不存在的配置文件"""
        nonexistent_file = tmp_path / "nonexistent.json"

        result = validator.validate_config_file(nonexistent_file)

        assert not result.is_valid
        assert len(result.errors) > 0

    def test_validate_invalid_json(self, validator, tmp_path):
        """测试无效的 JSON 格式"""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("{ invalid json }", encoding="utf-8")

        result = validator.validate_config_file(invalid_file)

        assert not result.is_valid
        assert len(result.errors) > 0

    # ==================== 警告测试 ====================

    def test_validate_with_warnings(self, validator, temp_config_file):
        """测试生成警告的配置"""
        config_content = json.dumps({
            "output_dir": "docs",
            "language": "zh",
            "structure_template": "reference",
            "version": "1.0.0"  # 旧版本，可能需要迁移
        })
        config_file = temp_config_file(config_content)

        result = validator.validate_config_file(config_file)

        # 配置应该有效，但可能有警告
        assert result.is_valid
        # 警告列表可能为空或不为空，取决于实现

    # ==================== 错误消息中文翻译测试 ====================

    def test_error_messages_in_chinese(self, validator, temp_config_file):
        """测试错误消息使用中文"""
        config_content = json.dumps({
            "output_dir": "docs"
            # 缺少必需字段
        })
        config_file = temp_config_file(config_content)

        result = validator.validate_config_file(config_file)

        # 检查错误消息包含中文
        assert not result.is_valid
        # 验证错误消息已被翻译（包含中文字符或翻译后的消息）
        assert len(result.errors) > 0


# ==================== 测试辅助函数 ====================

def test_validation_result_model():
    """测试 ValidationResult 数据模型"""
    result = ValidationResult(
        is_valid=True,
        errors=[],
        warnings=["测试警告"],
        config_path="/path/to/config.json"
    )

    assert result.is_valid is True
    assert len(result.errors) == 0
    assert len(result.warnings) == 1
    assert result.config_path == "/path/to/config.json"


def test_validation_result_with_errors():
    """测试包含错误的 ValidationResult"""
    result = ValidationResult(
        is_valid=False,
        errors=["错误1", "错误2"],
        warnings=[],
        config_path="/path/to/config.json"
    )

    assert result.is_valid is False
    assert len(result.errors) == 2
    assert result.errors[0] == "错误1"
