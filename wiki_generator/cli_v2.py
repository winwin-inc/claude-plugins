#!/usr/bin/env python3
"""
Wiki Generator CLI 工具（v2.0）

这是一个 Python CLI 工具，提供安装、配置验证和迁移功能。
文档生成由 Claude Code /wiki-generate 命令实现。

使用方法：
    wiki-generator --init              # 初始化项目配置和模板
    wiki-generator --validate           # 验证配置文件
    wiki-generator --migrate            # 迁移旧配置
    wiki-generator --version            # 显示版本信息
"""

import click
import sys
import json
from pathlib import Path
from typing import Optional

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from wiki_generator.core.installer_v2 import install_claude_files, confirm_overwrite
from wiki_generator.core.config_validator import ConfigValidator
from wiki_generator.core.config_initializer import (
    create_default_config,
    create_and_write_config,
    load_config_from_file
)
from wiki_generator.core.migrator import (
    detect_version,
    apply_migration,
    generate_migration_report
)
from wiki_generator.core.errors import (
    WikiGeneratorError,
    ConfigError,
    InstallationError,
    format_error_message,
    handle_error
)
from wiki_generator.models.config_models import Language, StructureTemplate
from wiki_generator.utils import logger


# 版本信息
VERSION = "2.0.0"
TEMPLATE_VERSION = "2.0.0"


@click.group()
@click.version_option(version=VERSION, prog_name="wiki-generator")
def cli():
    """
    Wiki Generator CLI 工具（v2.0）

    提供项目初始化、配置验证和迁移功能。

    文档生成由 Claude Code /wiki-generate 命令实现。
    """
    pass


@cli.command()
@click.option(
    "--target", "-t",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    help="目标项目目录（默认为当前工作目录）"
)
@click.option(
    "--force", "-f",
    is_flag=True,
    help="强制覆盖已存在的 .claude/ 目录"
)
@click.option(
    "--no-validate",
    is_flag=True,
    help="跳过配置验证"
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="显示详细输出"
)
def init(target: Optional[Path], force: bool, no_validate: bool, verbose: bool):
    """
    初始化项目配置和模板

    在项目根目录创建 .claude/ 目录，包含：
    - 配置文件（wiki-config.json）
    - 22 个模板文件（中英各 11 个）
    - JSON Schema
    - Claude Code 命令（wiki-generate.md）

    示例：
        wiki-generator --init
        wiki-generator --init --target /path/to/project
        wiki-generator --init --force
    """
    try:
        # 确定目标目录
        if target is None:
            target_dir = Path.cwd()
        else:
            target_dir = target

        logger.log_info(f"🎯 目标目录: {target_dir}")
        logger.log_verbose(f"使用配置: force={force}, no_validate={no_validate}", verbose)

        # 检查是否已存在 .claude/ 目录
        claude_target = target_dir / ".claude"
        if claude_target.exists() and not force:
            # 使用确认提示
            if not confirm_overwrite(claude_target, force):
                return 1

        # 执行安装
        logger.log_info("📦 开始安装...")
        result = install_claude_files(
            target_dir=target_dir,
            overwrite=force,
            backup=True
        )

        # 显示结果
        click.echo()
        if result.success:
            logger.log_success(f"成功安装到: {result.target_dir}")
            logger.log_success("配置文件已创建: .claude/wiki-config.json")
            logger.log_info(f"模板版本: {TEMPLATE_VERSION}")

            if result.installed_files:
                logger.log_info(f"\n📄 已安装文件 ({len(result.installed_files)}):")
                for f in result.installed_files[:5]:
                    logger.log_info(f"   ✓ {f}")
                if len(result.installed_files) > 5:
                    logger.log_info(f"   ... 还有 {len(result.installed_files) - 5} 个文件")

            if result.skipped_files:
                logger.log_warning(f"\n跳过文件 ({len(result.skipped_files)}):")
                for f in result.skipped_files[:3]:
                    logger.log_info(f"   ⊘ {f}")
                if len(result.skipped_files) > 3:
                    logger.log_info(f"   ... 还有 {len(result.skipped_files) - 3} 个文件")

            if result.backup_dir:
                logger.log_info(f"\n💾 备份: {result.backup_dir}")

            # 验证配置（如果未禁用）
            if not no_validate:
                logger.log_info("\n🔍 验证配置...")
                config_file = claude_target / "wiki-config.json"
                validator = ConfigValidator()
                validation = validator.validate_config_file(config_file)

                if validation.is_valid:
                    logger.log_success("配置文件验证通过")
                else:
                    logger.log_warning("配置文件验证失败")
                    for error in validation.errors:
                        logger.log_info(f"   - {error}")

            logger.log_info("\n📝 下一步:")
            logger.log_info("   1. 编辑 .claude/wiki-config.json 配置")
            logger.log_info("   2. 在 Claude Code 中运行 /wiki-generate 命令")
            if no_validate:
                logger.log_info("   3. 验证配置: wiki-generator --validate")

            return 0
        else:
            logger.log_error(f"安装失败: {result.error or '未知错误'}")
            return 1

    except WikiGeneratorError as e:
        handle_error(e, "初始化失败", exit_code=1)
        return 1
    except Exception as e:
        logger.log_error(f"错误: {str(e)}")
        if verbose:
            import traceback
            traceback.print_exc()
        return 1


@cli.command()
@click.option(
    "--config", "-c",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="配置文件路径（默认: .claude/wiki-config.json）"
)
def validate(config: Optional[Path]):
    """
    验证配置文件

    使用 JSON Schema 验证配置文件的正确性。

    示例：
        wiki-generator --validate
        wiki-generator --validate --config /path/to/wiki-config.json
    """
    try:
        # 确定配置文件路径
        if config is None:
            config_file = Path.cwd() / ".claude" / "wiki-config.json"
        else:
            config_file = config

        if not config_file.exists():
            logger.log_error(f"配置文件不存在: {config_file}")
            logger.log_info("   提示: 运行 wiki-generator --init 创建配置文件")
            return 1

        logger.log_info(f"🔍 验证配置文件: {config_file}")

        # 执行验证
        validator = ConfigValidator()
        result = validator.validate_config_file(config_file)

        # 显示结果
        click.echo()
        if result.is_valid:
            logger.log_success("配置文件验证通过")

            # 显示警告（如果有）
            if result.warnings:
                logger.log_warning("\n警告:")
                for warning in result.warnings:
                    logger.log_info(f"   - {warning}")

            return 0
        else:
            logger.log_error("配置文件验证失败")
            logger.log_info("\n错误:")
            for error in result.errors:
                logger.log_info(f"   - {error}")

            if result.warnings:
                logger.log_warning("\n警告:")
                for warning in result.warnings:
                    logger.log_info(f"   - {warning}")

            return 1

    except Exception as e:
        logger.log_error(f"错误: {str(e)}")
        return 1


@cli.command()
@click.option(
    "--config", "-c",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="配置文件路径（默认: .claude/wiki-config.json）"
)
@click.option(
    "--backup/--no-backup",
    default=True,
    help="是否备份原文件（默认: --backup）"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="显示将要执行的变更，但不实际修改"
)
def migrate(config: Optional[Path], backup: bool, dry_run: bool):
    """
    迁移配置文件到最新版本

    自动检测配置版本并应用迁移规则。

    示例：
        wiki-generator --migrate
        wiki-generator --migrate --no-backup
        wiki-generator --migrate --dry-run
    """
    try:
        # 确定配置文件路径
        if config is None:
            config_file = Path.cwd() / ".claude" / "wiki-config.json"
        else:
            config_file = config

        if not config_file.exists():
            logger.log_error(f"配置文件不存在: {config_file}")
            return 1

        logger.log_info(f"🔄 迁移配置文件: {config_file}")

        # 执行迁移
        result = apply_migration(config_file, backup=backup)

        # 显示结果
        click.echo()
        if result.success:
            logger.log_success(f"成功迁移到版本 {result.to_version}")

            logger.log_info("\n变更:")
            for change in result.changes:
                logger.log_info(f"   - {change}")

            if result.backup_path:
                logger.log_info(f"\n💾 备份: {result.backup_path}")

            # 生成迁移报告
            if not dry_run:
                report = generate_migration_report(result)
                report_file = config_file.parent / "migration-report.md"
                report_file.write_text(report, encoding="utf-8")
                logger.log_info(f"\n📄 迁移报告: {report_file}")

            return 0
        else:
            logger.log_error("迁移失败")

            if result.errors:
                logger.log_info("\n错误:")
                for error in result.errors:
                    logger.log_info(f"   - {error}")

            return 1

    except Exception as e:
        logger.log_error(f"错误: {str(e)}")
        return 1


@cli.command()
def version():
    """
    显示版本信息

    显示 wiki-generator 和模板的版本号。

    示例：
        wiki-generator --version
    """
    click.echo(f"wiki-generator version {VERSION}")
    click.echo(f"Template version: {TEMPLATE_VERSION}")
    click.echo(f"Python {sys.version}")


if __name__ == "__main__":
    cli()
