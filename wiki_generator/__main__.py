#!/usr/bin/env python3
"""
Wiki Generator 主入口

作为模块运行时: python -m wiki_generator
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入并运行 CLI
from cli import cli

if __name__ == "__main__":
    cli()
