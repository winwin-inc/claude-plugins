"""pytest 配置文件。"""

import pytest
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_config():
    """提供示例配置。"""
    return {
        "output_dir": "docs",
        "language": "zh",
        "structure_template": "reference",
        "include_sources": True,
        "generate_toc": True,
        "sections": {
            "required": ["quickstart", "overview"],
            "optional": ["datamodel"]
        }
    }


@pytest.fixture
def sample_template_content():
    """提供示例模板内容。"""
    return """# {title}

{toc}

## 概述

{overview_content}

## 快速开始

{quickstart_content}

---

## 参考来源

{sources}
"""
