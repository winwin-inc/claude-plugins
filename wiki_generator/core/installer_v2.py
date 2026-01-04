"""文件安装器（v2.0）。

此模块负责将 .claude/ 目录安装到项目中。
"""

import json
import shutil
import click
from pathlib import Path
from typing import Optional, List

from wiki_generator.models.config_models import InstallResult, TemplateInfo, TemplateManifest
from wiki_generator.utils.file_utils import (
    ensure_directory,
    copy_file_or_directory,
    backup_file,
    list_files
)
from wiki_generator.core.template_manifest import TemplateManifestManager
from wiki_generator.core.errors import InstallationError


def confirm_overwrite(claude_target: Path, force: bool = False) -> bool:
    """确认是否覆盖已存在的 .claude/ 目录。

    Args:
        claude_target: .claude/ 目录路径
        force: 是否强制覆盖（跳过确认）

    Returns:
        是否继续安装
    """
    if not claude_target.exists():
        return True

    if force:
        return True

    # 检查目录内容
    existing_files = list(claude_target.rglob("*"))
    file_count = len([f for f in existing_files if f.is_file()])

    click.echo(f"\n⚠️  .claude/ 目录已存在（包含 {file_count} 个文件）")
    click.echo("此操作将覆盖现有文件。\n")

    if not click.confirm("是否继续？", default=False):
        click.echo("❌ 操作已取消")
        return False

    return True


def install_claude_files(
    target_dir: Optional[Path] = None,
    source_dir: Optional[Path] = None,
    overwrite: bool = False,
    backup: bool = True
) -> InstallResult:
    """安装 .claude/ 文件到项目目录。

    Args:
        target_dir: 目标目录（通常是项目根目录）。如果为 None，使用当前目录。
        source_dir: 源目录（包内的 .claude/ 目录）。如果为 None，使用默认路径。
        overwrite: 是否覆盖已存在的文件
        backup: 是否备份已存在的文件

    Returns:
        安装结果
    """
    # 确定目标目录
    if target_dir is None:
        target_dir = Path.cwd()
    else:
        target_dir = Path(target_dir)

    claude_target = target_dir / ".claude"

    # 确定源目录
    if source_dir is None:
        # 使用包内的 .claude/ 目录
        current_file = Path(__file__)
        source_dir = current_file.parent.parent / ".claude"
    else:
        source_dir = Path(source_dir)

    source_dir = source_dir.resolve()

    # 检查源目录是否存在
    if not source_dir.exists():
        return InstallResult(
            success=False,
            error=f"源目录不存在: {source_dir}",
            target_dir=str(claude_target)
        )

    installed_files = []
    skipped_files = []
    backup_dir = None

    try:
        # 备份已存在的 .claude/ 目录
        if claude_target.exists() and backup:
            backup_path = claude_target.parent / f".claude.backup.{shutil.get_terminal_size().columns or 'tmp'}"
            # 使用时间戳创建备份目录
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = claude_target.parent / f".claude.backup.{timestamp}"

            if copy_file_or_directory(claude_target, backup_path, overwrite=True):
                backup_dir = str(backup_path)

        # 确保目标目录存在
        ensure_directory(claude_target)

        # 复制所有文件
        for item in source_dir.rglob("*"):
            if item.is_file():
                relative_path = item.relative_to(source_dir)
                target_file = claude_target / relative_path

                # 检查文件是否已存在
                if target_file.exists() and not overwrite:
                    skipped_files.append(str(relative_path))
                    continue

                # 复制文件
                if copy_file_or_directory(item, target_file, overwrite=overwrite):
                    installed_files.append(str(relative_path))

        # 创建或更新模板清单
        manifest_manager = TemplateManifestManager(claude_target)
        template_version = _get_template_version(claude_target)

        if template_version:
            # 扫描所有模板文件
            templates = _scan_templates(claude_target)
            manifest = manifest_manager.create_manifest(template_version, templates)
            manifest_manager.save_manifest(manifest)

        # 创建默认配置文件（如果不存在）
        config_file = claude_target / "wiki-config.json"
        if not config_file.exists():
            _create_default_config(config_file)
            installed_files.append("wiki-config.json")

        return InstallResult(
            success=True,
            installed_files=installed_files,
            skipped_files=skipped_files,
            target_dir=str(claude_target),
            backup_dir=backup_dir
        )

    except Exception as e:
        return InstallResult(
            success=False,
            error=f"安装失败: {str(e)}",
            target_dir=str(claude_target),
            backup_dir=backup_dir
        )


def _get_template_version(claude_dir: Path) -> Optional[str]:
    """获取模板版本号。

    Args:
        claude_dir: .claude/ 目录路径

    Returns:
        版本号，如果未找到则返回 None
    """
    version_file = claude_dir / ".template-version"
    if version_file.exists():
        content = version_file.read_text(encoding="utf-8").strip()
        return content
    return None


def _scan_templates(claude_dir: Path) -> List[TemplateInfo]:
    """扫描所有模板文件。

    Args:
        claude_dir: .claude/ 目录路径

    Returns:
        模板信息列表
    """
    templates = []
    templates_dir = claude_dir / "templates"

    if not templates_dir.exists():
        return templates

    template_version = _get_template_version(claude_dir) or "2.0.0"

    # 扫描语言目录
    for lang_dir in templates_dir.iterdir():
        if not lang_dir.is_dir():
            continue

        language = lang_dir.name
        if language not in ["zh", "en"]:
            continue

        # 扫描模板文件
        for template_file in lang_dir.glob("*.md.template"):
            # 提取模板信息
            name = template_file.stem  # 文件名不含扩展名
            title = _extract_template_title(template_file)
            variables = _extract_template_variables(template_file)

            template_info = TemplateInfo(
                name=name,
                language=language,
                path=str(template_file.relative_to(claude_dir)),
                title=title,
                version=template_version,
                variables=variables
            )
            templates.append(template_info)

    return templates


def _extract_template_title(template_file: Path) -> str:
    """从模板文件提取标题。

    Args:
        template_file: 模板文件路径

    Returns:
        模板标题
    """
    try:
        content = template_file.read_text(encoding="utf-8")
        # 查找第一个 # 标题
        for line in content.split("\n")[:10]:  # 只检查前 10 行
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()
            elif line.startswith("#") and not line.startswith("# "):
                return line[1:].strip()
    except Exception:
        pass

    return template_file.stem


def _extract_template_variables(template_file: Path) -> List[str]:
    """从模板文件提取变量列表。

    Args:
        template_file: 模板文件路径

    Returns:
        变量名列表
    """
    import re

    try:
        content = template_file.read_text(encoding="utf-8")
        # 查找所有 {variable} 格式的变量
        variables = re.findall(r"\{(\w+)\}", content)
        # 去重并排序
        return sorted(set(variables))
    except Exception:
        return []


def _create_default_config(config_file: Path) -> None:
    """创建默认配置文件。

    Args:
        config_file: 配置文件路径
    """
    default_config = {
        "output_dir": "docs",
        "language": "zh",
        "structure_template": "reference",
        "include_sources": True,
        "generate_toc": True
    }

    config_file.write_text(
        json.dumps(default_config, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
