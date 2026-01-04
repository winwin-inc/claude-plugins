"""测试初始化工作流。

验证 `wiki-generator --init` 命令的端到端功能。
"""

import pytest
import json
from pathlib import Path


class TestInitWorkflow:
    """测试初始化工作流。"""

    def test_init_creates_config_file(self, tmp_path):
        """测试初始化创建配置文件。"""
        from wiki_generator.core.installer import install_claude_files

        result = install_claude_files(target_dir=tmp_path)

        assert result.success is True
        config_file = tmp_path / "wiki-config.json"
        assert config_file.exists()

        with open(config_file, encoding="utf-8") as f:
            config = json.load(f)
            assert "language" in config
            assert config["language"] in ["zh", "en", "both"]

    def test_init_creates_templates_directory(self, tmp_path):
        """测试初始化创建模板目录。"""
        from wiki_generator.core.installer import install_claude_files

        result = install_claude_files(target_dir=tmp_path)

        assert result.success is True
        templates_dir = tmp_path / "templates"
        assert templates_dir.exists()
        assert templates_dir.is_dir()

    def test_init_creates_version_file(self, tmp_path):
        """测试初始化创建版本文件。"""
        from wiki_generator.core.installer import install_claude_files

        result = install_claude_files(target_dir=tmp_path)

        assert result.success is True
        version_file = tmp_path / ".template-version"
        assert version_file.exists()

        version = version_file.read_text(encoding="utf-8").strip()
        assert len(version.split(".")) == 3  # MAJOR.MINOR.PATCH

    def test_init_with_force_overwrites_existing(self, tmp_path):
        """测试使用 --force 覆盖已存在的文件。"""
        from wiki_generator.core.installer import install_claude_files

        # 第一次安装
        install_claude_files(target_dir=tmp_path)

        # 修改配置文件
        config_file = tmp_path / "wiki-config.json"
        with open(config_file, encoding="utf-8") as f:
            config = json.load(f)
        config["language"] = "en"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f)

        # 第二次安装（强制覆盖）
        result = install_claude_files(target_dir=tmp_path, overwrite=True)

        assert result.success is True
        with open(config_file, encoding="utf-8") as f:
            config = json.load(f)
            assert config["language"] == "zh"  # 恢复为默认值
