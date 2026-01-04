"""配置初始化模块。

此模块负责创建默认配置和写入配置文件。
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any

from wiki_generator.models.config_models import WikiConfig, Language, StructureTemplate
from wiki_generator.utils.file_utils import write_file_content


def create_default_config(
    language: Language = Language.ZH,
    structure_template: StructureTemplate = StructureTemplate.REFERENCE,
    output_dir: str = "docs",
    include_sources: bool = True,
    generate_toc: bool = True
) -> WikiConfig:
    """创建默认配置。

    Args:
        language: 文档语言
        structure_template: 结构模板
        output_dir: 输出目录
        include_sources: 是否包含来源
        generate_toc: 是否生成目录

    Returns:
        WikiConfig 对象
    """
    return WikiConfig(
        output_dir=output_dir,
        language=language,
        structure_template=structure_template,
        include_sources=include_sources,
        generate_toc=generate_toc,
        version="2.0.0"
    )


def write_config(
    config: WikiConfig,
    config_path: Path,
    indent: int = 2,
    ensure_ascii: bool = False
) -> bool:
    """写入配置文件。

    Args:
        config: WikiConfig 对象
        config_path: 配置文件路径
        indent: JSON 缩进空格数
        ensure_ascii: 是否确保 ASCII 编码

    Returns:
        是否成功写入
    """
    # 转换为字典
    config_dict = {
        "output_dir": config.output_dir,
        "language": config.language.value,
        "structure_template": config.structure_template.value,
        "include_sources": config.include_sources,
        "generate_toc": config.generate_toc,
    }

    # 添加可选字段
    if config.sections:
        config_dict["sections"] = {
            "required": config.sections.required,
            "optional": config.sections.optional
        }

    if config.version:
        config_dict["version"] = config.version

    # 转换为 JSON
    json_content = json.dumps(config_dict, indent=indent, ensure_ascii=ensure_ascii)

    # 写入文件
    return write_file_content(config_path, json_content)


def create_and_write_config(
    config_path: Path,
    language: Language = Language.ZH,
    structure_template: StructureTemplate = StructureTemplate.REFERENCE,
    output_dir: str = "docs"
) -> bool:
    """创建并写入默认配置文件。

    Args:
        config_path: 配置文件路径
        language: 文档语言
        structure_template: 结构模板
        output_dir: 输出目录

    Returns:
        是否成功
    """
    config = create_default_config(
        language=language,
        structure_template=structure_template,
        output_dir=output_dir
    )

    return write_config(config, config_path)


def load_config_from_file(config_path: Path) -> Optional[Dict[str, Any]]:
    """从文件加载配置。

    Args:
        config_path: 配置文件路径

    Returns:
        配置字典，如果失败则返回 None
    """
    from wiki_generator.utils.file_utils import read_file_content

    if not config_path.exists():
        return None

    content = read_file_content(config_path)
    if content is None:
        return None

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return None
